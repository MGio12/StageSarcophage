from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.models.document import Document, StatutDocument
from app.models.notification_config import NotificationConfig
from app.models.source import Source
from app.services.purge_service import mettre_a_jour_statuts
from app.services.sync_service import synchroniser_source


def _source(db, **kwargs):
    defaults = dict(
        nom="Source notifications",
        type_serveur="linux",
        protocole="sftp",
        adresse="127.0.0.1",
        chemin_distant="/data",
        seuil_avertissement_jours=30,
        seuil_critique_jours=60,
    )
    defaults.update(kwargs)
    src = Source(**defaults)
    db.session.add(src)
    db.session.flush()
    return src


def _notification(db, **kwargs):
    defaults = dict(email="ops@example.local", actif=True)
    defaults.update(kwargs)
    config = NotificationConfig(**defaults)
    db.session.add(config)
    db.session.commit()
    return config


def test_notification_envoyee_quand_document_devient_critique(app, db):
    src = _source(db)
    _notification(db, notif_critiques=True)
    doc = Document(
        source_id=src.id,
        nom_fichier="critique.pdf",
        chemin_local="/tmp/critique.pdf",
        statut=StatutDocument.OK,
        date_modification_source=datetime.now(timezone.utc) - timedelta(days=70),
    )
    db.session.add(doc)
    db.session.commit()

    with patch("app.services.notification_service.envoyer_email", return_value=True) as mock_email:
        mettre_a_jour_statuts(src)

    db.session.expire(doc)
    assert doc.statut == StatutDocument.CRITIQUE
    assert mock_email.call_count == 1
    assert "critique.pdf" in mock_email.call_args.args[2]


def test_document_deja_critique_ne_renotifie_pas(app, db):
    src = _source(db)
    _notification(db, notif_critiques=True)
    doc = Document(
        source_id=src.id,
        nom_fichier="deja.pdf",
        chemin_local="/tmp/deja.pdf",
        statut=StatutDocument.CRITIQUE,
        date_modification_source=datetime.now(timezone.utc) - timedelta(days=70),
    )
    db.session.add(doc)
    db.session.commit()

    with patch("app.services.notification_service.envoyer_email", return_value=True) as mock_email:
        mettre_a_jour_statuts(src)

    mock_email.assert_not_called()


@patch("app.services.sftp_service.lister_fichiers")
def test_notification_erreur_envoyee_au_troisieme_echec(mock_lister, app, db, tmp_path):
    app.config["STORAGE_DIR"] = str(tmp_path)
    mock_lister.side_effect = OSError("connexion refusee")
    src = _source(db)
    _notification(db, notif_erreurs=True)

    with patch("app.services.notification_service.envoyer_email", return_value=True) as mock_email:
        synchroniser_source(src)
        synchroniser_source(src)
        synchroniser_source(src)
        synchroniser_source(src)

    db.session.expire(src)
    assert src.echecs_consecutifs == 4
    assert mock_email.call_count == 1


@patch("app.services.sftp_service.lister_fichiers", return_value=[])
def test_succes_sync_reinitialise_echecs(mock_lister, app, db, tmp_path):
    app.config["STORAGE_DIR"] = str(tmp_path)
    src = _source(db, echecs_consecutifs=2)

    synchroniser_source(src)

    db.session.expire(src)
    assert src.echecs_consecutifs == 0
