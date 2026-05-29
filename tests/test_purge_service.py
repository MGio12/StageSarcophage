"""Tests unitaires du service de purge et de contrôle de fraîcheur (vrai DB)."""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta

import pytest

from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement
from app.models.source import Source
from app.services.purge_service import mettre_a_jour_statuts, purger_source


# --- Fixtures --------------------------------------------------------------- #

@pytest.fixture()
def storage_dir(app, tmp_path):
    old = app.config["STORAGE_DIR"]
    app.config["STORAGE_DIR"] = str(tmp_path)
    yield tmp_path
    app.config["STORAGE_DIR"] = old


def _source(db, **kwargs):
    defaults = dict(
        nom="Src-Purge",
        type_serveur="linux",
        protocole="sftp",
        adresse="192.168.1.50",
        chemin_distant="/data/docs",
        retention_jours=90,
        seuil_avertissement_jours=30,
        seuil_critique_jours=60,
    )
    defaults.update(kwargs)
    src = Source(**defaults)
    db.session.add(src)
    db.session.flush()
    return src


def _doc(db, source, nom="fiche.pdf", age_jours=0, chemin_local=None):
    maintenant = datetime.now(timezone.utc)
    date_collecte = maintenant - timedelta(days=age_jours)
    date_modification = maintenant - timedelta(days=age_jours)
    doc = Document(
        source_id=source.id,
        nom_fichier=nom,
        chemin_local=chemin_local or f"/data/{nom}",
        date_collecte=date_collecte,
        date_modification_source=date_modification,
    )
    db.session.add(doc)
    db.session.commit()
    return doc


# --- Tests mettre_a_jour_statuts ------------------------------------------- #

class TestMettreAJourStatuts:
    def test_document_recent_reste_ok(self, app, db):
        src = _source(db)
        doc = _doc(db, src, age_jours=5)
        mettre_a_jour_statuts(src)
        db.session.expire(doc)
        assert doc.statut == StatutDocument.OK

    def test_document_depasse_seuil_avertissement(self, app, db):
        src = _source(db, seuil_avertissement_jours=30, seuil_critique_jours=60)
        doc = _doc(db, src, age_jours=40)
        mettre_a_jour_statuts(src)
        db.session.expire(doc)
        assert doc.statut == StatutDocument.AVERTISSEMENT

    def test_document_depasse_seuil_critique(self, app, db):
        src = _source(db, seuil_avertissement_jours=30, seuil_critique_jours=60)
        doc = _doc(db, src, age_jours=70)
        mettre_a_jour_statuts(src)
        db.session.expire(doc)
        assert doc.statut == StatutDocument.CRITIQUE

    def test_document_purge_non_touche(self, app, db):
        src = _source(db)
        doc = _doc(db, src, age_jours=100)
        doc.statut = StatutDocument.PURGE
        db.session.commit()
        mettre_a_jour_statuts(src)
        db.session.expire(doc)
        assert doc.statut == StatutDocument.PURGE

    def test_plusieurs_docs_statuts_differents(self, app, db):
        src = _source(db, seuil_avertissement_jours=30, seuil_critique_jours=60)
        doc_ok = _doc(db, src, nom="ok.pdf", age_jours=10)
        doc_av = _doc(db, src, nom="av.pdf", age_jours=45)
        doc_cr = _doc(db, src, nom="cr.pdf", age_jours=75)
        mettre_a_jour_statuts(src)
        db.session.expire_all()
        assert doc_ok.statut == StatutDocument.OK
        assert doc_av.statut == StatutDocument.AVERTISSEMENT
        assert doc_cr.statut == StatutDocument.CRITIQUE


# --- Tests purger_source ---------------------------------------------------- #

class TestPurgerSource:
    def test_document_expire_passe_en_purge(self, app, db, storage_dir):
        src = _source(db, retention_jours=30)
        doc = _doc(db, src, age_jours=40)
        result = purger_source(src)
        db.session.expire(doc)
        assert result.fichiers_purges == 1
        assert doc.statut == StatutDocument.PURGE

    def test_document_recent_non_purge(self, app, db, storage_dir):
        src = _source(db, retention_jours=90)
        doc = _doc(db, src, age_jours=10)
        result = purger_source(src)
        db.session.expire(doc)
        assert result.fichiers_purges == 0
        assert doc.statut == StatutDocument.OK

    def test_fichier_physique_deplace_en_corbeille(self, app, db, storage_dir):
        src = _source(db, retention_jours=30)
        # Créer un vrai fichier
        fichier = storage_dir / "fiche.pdf"
        fichier.write_bytes(b"PDF content")
        doc = _doc(db, src, nom="fiche.pdf", age_jours=40, chemin_local=str(fichier))

        purger_source(src)

        assert not fichier.exists()
        corbeille = storage_dir / "_corbeille" / str(src.id) / "fiche.pdf"
        assert corbeille.exists()

    def test_document_sans_date_collecte_ignore(self, app, db, storage_dir):
        src = _source(db, retention_jours=1)
        doc = Document(
            source_id=src.id, nom_fichier="sans-date.pdf",
            chemin_local="/data/sans-date.pdf",
        )
        db.session.add(doc)
        db.session.commit()
        result = purger_source(src)
        assert result.fichiers_purges == 0

    def test_journal_cree_apres_purge(self, app, db, storage_dir):
        src = _source(db, retention_jours=10)
        _doc(db, src, age_jours=20)
        purger_source(src)
        entree = Journal.query.filter_by(source_id=src.id, type_evenement=TypeEvenement.PURGE).first()
        assert entree is not None
        assert entree.details["fichiers_purges"] == 1

    def test_pas_de_journal_si_rien_a_purger(self, app, db, storage_dir):
        src = _source(db, retention_jours=90)
        _doc(db, src, age_jours=5)
        purger_source(src)
        entree = Journal.query.filter_by(source_id=src.id).first()
        assert entree is None

    def test_collision_nom_corbeille_renommee(self, app, db, storage_dir):
        src = _source(db, retention_jours=1)
        # Créer deux documents expirés avec le même nom de fichier
        # (cas improbable mais possible si corbeille non vidée)
        corbeille = storage_dir / "_corbeille" / str(src.id)
        corbeille.mkdir(parents=True)
        (corbeille / "fiche.pdf").write_bytes(b"old")

        fichier = storage_dir / "fiche.pdf"
        fichier.write_bytes(b"new content")
        doc = _doc(db, src, nom="fiche.pdf", age_jours=5, chemin_local=str(fichier))

        purger_source(src)

        # Le fichier original en corbeille doit être préservé + nouveau ajouté avec suffixe
        assert (corbeille / "fiche.pdf").exists()
        suffixes = list(corbeille.glob("fiche_*.pdf"))
        assert len(suffixes) == 1

    def test_purge_refuse_fichier_hors_storage(self, app, db, storage_dir, tmp_path):
        src = _source(db, retention_jours=1)
        outside = tmp_path.parent / f"{tmp_path.name}_outside.pdf"
        outside.write_bytes(b"%PDF outside")
        doc = _doc(db, src, nom="outside.pdf", age_jours=5, chemin_local=str(outside))

        result = purger_source(src)

        db.session.expire(doc)
        assert result.fichiers_purges == 0
        assert result.erreurs == 1
        assert outside.exists()
        assert doc.statut != StatutDocument.PURGE
