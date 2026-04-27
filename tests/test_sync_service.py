
"""Tests unitaires du service de synchronisation (mock connecteurs, vrai DB)."""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement
from app.models.source import Source
from app.services.sftp_service import FichierDistant
from app.services.sync_service import synchroniser_source, _slugify, _hash_fichier


# --- Fixtures --------------------------------------------------------------- #

CONTENU_PDF = b"%PDF-1.4 fake content for tests"
HASH_PDF = hashlib.sha256(CONTENU_PDF).hexdigest()


@pytest.fixture()
def storage_dir(app, tmp_path):
    old = app.config["STORAGE_DIR"]
    app.config["STORAGE_DIR"] = str(tmp_path)
    yield tmp_path
    app.config["STORAGE_DIR"] = old


def _source_sftp(db, nom="Src-SFTP"):
    src = Source(
        nom=nom,
        type_serveur="linux",
        protocole="sftp",
        adresse="192.168.1.50",
        chemin_distant="/data/docs",
    )
    db.session.add(src)
    db.session.flush()
    return src


def _f_distant(nom="doc.pdf", taille=len(CONTENU_PDF), mtime=None):
    if mtime is None:
        mtime = datetime.now(timezone.utc)
    return FichierDistant(nom=nom, chemin=f"/data/docs/{nom}", taille=taille, date_modification=mtime)


def _mock_dl(source, fichier, chemin_local):
    """Écrit CONTENU_PDF dans le fichier temporaire, comme le ferait paramiko."""
    with open(chemin_local, "wb") as f:
        f.write(CONTENU_PDF)


# --- Tests ------------------------------------------------------------------ #

class TestSlugify:
    def test_remplace_espaces(self):
        assert "_" in _slugify("mon serveur")

    def test_minuscules(self):
        assert _slugify("SERVEUR") == "serveur"

    def test_chaine_vide_retourne_source(self):
        assert _slugify("") == "source"


class TestSynchroniserSource:
    @patch("app.services.sftp_service.telecharger_fichier", side_effect=_mock_dl)
    @patch("app.services.sftp_service.lister_fichiers")
    def test_nouveau_fichier_copie_et_enregistre(self, mock_lister, mock_dl, app, db, storage_dir):
        mock_lister.return_value = [_f_distant()]
        src = _source_sftp(db)

        result = synchroniser_source(src)

        assert result.fichiers_copies == 1
        assert result.erreurs == 0

        doc = Document.query.filter_by(source_id=src.id).first()
        assert doc is not None
        assert doc.nom_fichier == "doc.pdf"
        assert doc.hash_sha256 == HASH_PDF
        assert doc.taille_octets == len(CONTENU_PDF)
        assert doc.statut == StatutDocument.OK
        assert os.path.exists(doc.chemin_local)

    @patch("app.services.sftp_service.telecharger_fichier", side_effect=_mock_dl)
    @patch("app.services.sftp_service.lister_fichiers")
    def test_fichier_inchange_ignore_sans_telechargement(self, mock_lister, mock_dl, app, db, storage_dir):
        """Même date + même taille → skip immédiat, pas de téléchargement."""
        mtime = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_lister.return_value = [_f_distant(mtime=mtime)]
        src = _source_sftp(db)

        # Pré-créer un Document avec les mêmes métadonnées
        doc = Document(
            source_id=src.id,
            nom_fichier="doc.pdf",
            chemin_local="/data/doc.pdf",
            hash_sha256=HASH_PDF,
            taille_octets=len(CONTENU_PDF),
            date_modification_source=mtime,
        )
        db.session.add(doc)
        db.session.commit()

        result = synchroniser_source(src)

        assert result.fichiers_ignores == 1
        assert result.fichiers_copies == 0
        mock_dl.assert_not_called()

    @patch("app.services.sftp_service.telecharger_fichier", side_effect=_mock_dl)
    @patch("app.services.sftp_service.lister_fichiers")
    def test_meme_hash_apres_dl_ignore(self, mock_lister, mock_dl, app, db, storage_dir):
        """Date différente mais contenu identique → ignore après téléchargement."""
        mtime_ancienne = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mtime_nouvelle = datetime(2025, 6, 1, tzinfo=timezone.utc)
        mock_lister.return_value = [_f_distant(mtime=mtime_nouvelle)]
        src = _source_sftp(db)

        doc = Document(
            source_id=src.id,
            nom_fichier="doc.pdf",
            chemin_local="/data/doc.pdf",
            hash_sha256=HASH_PDF,
            taille_octets=len(CONTENU_PDF) + 1,  # taille diff → force DL
            date_modification_source=mtime_ancienne,
        )
        db.session.add(doc)
        db.session.commit()

        result = synchroniser_source(src)

        assert result.fichiers_ignores == 1
        assert result.fichiers_copies == 0

    @patch("app.services.sftp_service.telecharger_fichier", side_effect=_mock_dl)
    @patch("app.services.sftp_service.lister_fichiers")
    def test_fichier_modifie_mis_a_jour(self, mock_lister, mock_dl, app, db, storage_dir):
        """Nouveau hash → copie + mise à jour du Document."""
        mtime = datetime(2025, 6, 1, tzinfo=timezone.utc)
        mock_lister.return_value = [_f_distant(mtime=mtime)]
        src = _source_sftp(db)

        doc = Document(
            source_id=src.id,
            nom_fichier="doc.pdf",
            chemin_local="/data/doc.pdf",
            hash_sha256="a" * 64,  # ancien hash différent
            taille_octets=9999,
            date_modification_source=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

        result = synchroniser_source(src)

        assert result.fichiers_copies == 1
        db.session.expire(doc)
        assert doc.hash_sha256 == HASH_PDF

    @patch("app.services.sftp_service.lister_fichiers")
    def test_erreur_connexion_journalisee(self, mock_lister, app, db, storage_dir):
        mock_lister.side_effect = OSError("Connexion refusée")
        src = _source_sftp(db)

        result = synchroniser_source(src)

        assert result.erreurs == 1
        assert result.fichiers_copies == 0
        entree = Journal.query.filter_by(source_id=src.id, type_evenement=TypeEvenement.ERREUR).first()
        assert entree is not None

    @patch("app.services.sftp_service.telecharger_fichier", side_effect=_mock_dl)
    @patch("app.services.sftp_service.lister_fichiers")
    def test_journal_sync_cree(self, mock_lister, mock_dl, app, db, storage_dir):
        mock_lister.return_value = [_f_distant("a.pdf"), _f_distant("b.pdf")]
        src = _source_sftp(db)

        synchroniser_source(src)

        entree = Journal.query.filter_by(source_id=src.id, type_evenement=TypeEvenement.SYNC).first()
        assert entree is not None
        assert entree.details["fichiers_copies"] == 2

    @patch("app.services.sftp_service.telecharger_fichier", side_effect=_mock_dl)
    @patch("app.services.sftp_service.lister_fichiers")
    def test_plusieurs_fichiers_mix(self, mock_lister, mock_dl, app, db, storage_dir):
        """3 fichiers : 1 nouveau, 1 inchangé, 1 modifié."""
        mtime_fixe = datetime(2025, 1, 1, tzinfo=timezone.utc)

        # Fichier inchangé en base
        src = _source_sftp(db)
        doc_inchange = Document(
            source_id=src.id, nom_fichier="inchange.pdf",
            chemin_local="/data/inchange.pdf", hash_sha256=HASH_PDF,
            taille_octets=len(CONTENU_PDF), date_modification_source=mtime_fixe,
        )
        doc_modifie = Document(
            source_id=src.id, nom_fichier="modifie.pdf",
            chemin_local="/data/modifie.pdf", hash_sha256="b" * 64,
            taille_octets=9999, date_modification_source=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        db.session.add_all([doc_inchange, doc_modifie])
        db.session.commit()

        mock_lister.return_value = [
            _f_distant("nouveau.pdf"),
            _f_distant("inchange.pdf", mtime=mtime_fixe),
            _f_distant("modifie.pdf", mtime=datetime(2025, 6, 1, tzinfo=timezone.utc)),
        ]

        result = synchroniser_source(src)

        assert result.fichiers_copies == 2   # nouveau + modifié
        assert result.fichiers_ignores == 1  # inchangé
        assert result.erreurs == 0
