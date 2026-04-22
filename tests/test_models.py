"""Tests unitaires des modèles SQLAlchemy."""

import pytest
from sqlalchemy import inspect
from app.extensions import db as _db
from app.models.source import Source
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement


class TestCreationTables:
    def test_table_sources_existe(self, app):
        with app.app_context():
            inspector = inspect(_db.engine)
            assert "sources" in inspector.get_table_names()

    def test_table_documents_existe(self, app):
        with app.app_context():
            inspector = inspect(_db.engine)
            assert "documents" in inspector.get_table_names()

    def test_table_journaux_existe(self, app):
        with app.app_context():
            inspector = inspect(_db.engine)
            assert "journaux" in inspector.get_table_names()

    def test_colonnes_sources(self, app):
        with app.app_context():
            inspector = inspect(_db.engine)
            colonnes = {c["name"] for c in inspector.get_columns("sources")}
            attendues = {
                "id", "nom", "description", "type_serveur", "protocole",
                "adresse", "port", "chemin_distant", "login", "mot_de_passe",
                "filtre_fichiers", "frequence_sync_minutes", "retention_jours",
                "seuil_avertissement_jours", "seuil_critique_jours",
                "actif", "created_at", "updated_at",
            }
            assert attendues.issubset(colonnes)

    def test_colonnes_documents(self, app):
        with app.app_context():
            inspector = inspect(_db.engine)
            colonnes = {c["name"] for c in inspector.get_columns("documents")}
            attendues = {
                "id", "source_id", "nom_fichier", "chemin_local",
                "hash_sha256", "taille_octets", "date_modification_source",
                "date_collecte", "statut", "created_at", "updated_at",
            }
            assert attendues.issubset(colonnes)

    def test_colonnes_journaux(self, app):
        with app.app_context():
            inspector = inspect(_db.engine)
            colonnes = {c["name"] for c in inspector.get_columns("journaux")}
            attendues = {
                "id", "source_id", "type_evenement", "message",
                "details", "created_at",
            }
            assert attendues.issubset(colonnes)


class TestModeleSource:
    def _nouvelle_source(self):
        return Source(
            nom="Serveur-Test",
            type_serveur="linux",
            protocole="sftp",
            adresse="192.168.1.10",
            chemin_distant="/data/modes-degrades",
        )

    def test_creation_source(self, app, db):
        with app.app_context():
            src = self._nouvelle_source()
            db.session.add(src)
            db.session.commit()
            assert src.id is not None

    def test_login_chiffre_en_base(self, app, db):
        with app.app_context():
            src = self._nouvelle_source()
            src.login = "admin_sftp"
            db.session.add(src)
            db.session.commit()

            # La colonne physique doit être chiffrée (différente du texte clair)
            assert src._login != "admin_sftp"
            assert src._login != ""

    def test_login_dechiffre_a_la_lecture(self, app, db):
        with app.app_context():
            src = self._nouvelle_source()
            src.login = "admin_sftp"
            src.mot_de_passe = "s3cr3t!"
            db.session.add(src)
            db.session.commit()

            db.session.expire(src)  # force rechargement depuis la BDD
            assert src.login == "admin_sftp"
            assert src.mot_de_passe == "s3cr3t!"

    def test_login_vide_reste_vide(self, app, db):
        with app.app_context():
            src = self._nouvelle_source()
            src.login = ""
            db.session.add(src)
            db.session.commit()
            assert src.login == ""
            assert src._login is None

    def test_valeurs_par_defaut(self, app, db):
        with app.app_context():
            src = self._nouvelle_source()
            db.session.add(src)
            db.session.commit()
            assert src.filtre_fichiers == "*.pdf"
            assert src.frequence_sync_minutes == 60
            assert src.retention_jours == 90
            assert src.actif is True
            assert src.created_at is not None
            assert src.updated_at is not None

    def test_unicite_nom(self, app, db):
        with app.app_context():
            src1 = self._nouvelle_source()
            src2 = Source(
                nom="Serveur-Test",  # même nom
                type_serveur="windows",
                protocole="smb",
                chemin_distant="\\\\srv\\partage",
            )
            db.session.add(src1)
            db.session.commit()
            db.session.add(src2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()


class TestModeleDocument:
    def _source(self, db):
        src = Source(
            nom="Source-Doc-Test",
            type_serveur="linux",
            protocole="sftp",
            chemin_distant="/data",
        )
        db.session.add(src)
        db.session.flush()
        return src

    def test_creation_document(self, app, db):
        with app.app_context():
            src = self._source(db)
            doc = Document(
                source_id=src.id,
                nom_fichier="fiche-urgence.pdf",
                chemin_local="/data/source-doc-test/fiche-urgence.pdf",
                hash_sha256="a" * 64,
                taille_octets=12345,
            )
            db.session.add(doc)
            db.session.commit()
            assert doc.id is not None
            assert doc.statut == StatutDocument.OK

    def test_statut_par_defaut_ok(self, app, db):
        with app.app_context():
            src = self._source(db)
            doc = Document(
                source_id=src.id,
                nom_fichier="proc-degradee.pdf",
                chemin_local="/data/proc-degradee.pdf",
            )
            db.session.add(doc)
            db.session.commit()
            assert doc.statut == StatutDocument.OK

    def test_statut_critique(self, app, db):
        with app.app_context():
            src = self._source(db)
            doc = Document(
                source_id=src.id,
                nom_fichier="vieux-doc.pdf",
                chemin_local="/data/vieux-doc.pdf",
                statut=StatutDocument.CRITIQUE,
            )
            db.session.add(doc)
            db.session.commit()
            db.session.expire(doc)
            assert doc.statut == StatutDocument.CRITIQUE


class TestModeleJournal:
    def test_creation_journal_sans_source(self, app, db):
        with app.app_context():
            entree = Journal(
                type_evenement=TypeEvenement.ERREUR,
                message="Connexion impossible à 192.168.1.50",
            )
            db.session.add(entree)
            db.session.commit()
            assert entree.id is not None
            assert entree.source_id is None

    def test_details_json_serialisation(self, app, db):
        with app.app_context():
            entree = Journal(
                type_evenement=TypeEvenement.SYNC,
                message="Synchronisation terminée",
            )
            entree.details = {"fichiers_copies": 12, "erreurs": 0, "ignores": 3}
            db.session.add(entree)
            db.session.commit()
            db.session.expire(entree)
            assert entree.details == {"fichiers_copies": 12, "erreurs": 0, "ignores": 3}

    def test_details_none_reste_none(self, app, db):
        with app.app_context():
            entree = Journal(
                type_evenement=TypeEvenement.PURGE,
                message="Purge OK",
            )
            db.session.add(entree)
            db.session.commit()
            assert entree.details is None

    def test_created_at_automatique(self, app, db):
        with app.app_context():
            entree = Journal(
                type_evenement=TypeEvenement.ACCES,
                message="Connexion utilisateur",
            )
            db.session.add(entree)
            db.session.commit()
            assert entree.created_at is not None
