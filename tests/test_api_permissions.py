from datetime import datetime, timezone
from unittest.mock import patch

from app.models.api_token import APIToken
from app.models.document import Document
from app.models.role import Role
from app.models.source import Source
from app.models.user import User


def _token(db, permissions):
    role = Role(nom="api-role", permissions=permissions)
    user = User(username="api-user", role=role)
    user.set_password("secret123")
    db.session.add_all([role, user])
    db.session.flush()
    api_token, token_clair = APIToken.create(user.id, "test")
    db.session.add(api_token)
    db.session.commit()
    return token_clair


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _source(db):
    src = Source(
        nom="API Source",
        type_serveur="linux",
        protocole="local",
        chemin_distant="/tmp",
    )
    db.session.add(src)
    db.session.flush()
    return src


def test_stats_requiert_sources_et_documents_view(client, db):
    token = _token(db, {"documents.view": True})

    response = client.get("/api/v1/stats", headers=_headers(token))

    assert response.status_code == 403
    assert "sources.view" in response.get_json()["missing_permissions"]


def test_sources_requiert_permission_sources_view(client, db):
    token = _token(db, {"documents.view": True})

    response = client.get("/api/v1/sources", headers=_headers(token))

    assert response.status_code == 403
    assert "sources.view" in response.get_json()["missing_permissions"]


def test_documents_requiert_permission_documents_view(client, db):
    token = _token(db, {"sources.view": True})

    response = client.get("/api/v1/documents", headers=_headers(token))

    assert response.status_code == 403
    assert "documents.view" in response.get_json()["missing_permissions"]


def test_download_requiert_permission_documents_download(client, db, app, tmp_path):
    token = _token(db, {"documents.view": True})
    app.config["STORAGE_DIR"] = str(tmp_path)
    fichier = tmp_path / "doc.pdf"
    fichier.write_bytes(b"%PDF")
    src = _source(db)
    doc = Document(
        source_id=src.id,
        nom_fichier="doc.pdf",
        chemin_local=str(fichier),
        date_collecte=datetime.now(timezone.utc),
    )
    db.session.add(doc)
    db.session.commit()

    response = client.get(f"/api/v1/documents/{doc.id}/download", headers=_headers(token))

    assert response.status_code == 403
    assert "documents.download" in response.get_json()["missing_permissions"]


def test_download_refuse_chemin_hors_storage(client, db, app, tmp_path):
    token = _token(db, {"documents.download": True})
    storage = tmp_path / "storage"
    storage.mkdir()
    outside = tmp_path / "storage_evil" / "doc.pdf"
    outside.parent.mkdir()
    outside.write_bytes(b"%PDF")
    app.config["STORAGE_DIR"] = str(storage)
    src = _source(db)
    doc = Document(
        source_id=src.id,
        nom_fichier="doc.pdf",
        chemin_local=str(outside),
    )
    db.session.add(doc)
    db.session.commit()

    response = client.get(f"/api/v1/documents/{doc.id}/download", headers=_headers(token))

    assert response.status_code == 403


def test_api_post_sync_est_exempte_csrf_et_retourne_job(client, db, app):
    token = _token(db, {"sources.sync": True})
    src = _source(db)
    app.config["JOBS_RUN_INLINE"] = True
    ancien_csrf = app.config["WTF_CSRF_ENABLED"]
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        from app.services.sync_service import ResultatSync
        from unittest.mock import patch

        with patch("app.services.sync_service.synchroniser_source", return_value=ResultatSync(source_id=src.id)), \
             patch("app.services.purge_service.mettre_a_jour_statuts"):
            response = client.post(f"/api/v1/sources/{src.id}/sync", headers=_headers(token))
    finally:
        app.config["WTF_CSRF_ENABLED"] = ancien_csrf

    assert response.status_code == 202
    body = response.get_json()
    assert body["job"]["id"]
    assert body["job"]["status"] == "succeeded"
    assert body["job"]["status_url"].endswith(f"/api/v1/jobs/{body['job']['id']}")


def test_api_sync_masque_exception_interne(client, db):
    token = _token(db, {"sources.sync": True})
    src = _source(db)

    with patch(
        "app.services.sync_service.synchroniser_source",
        side_effect=RuntimeError("secret path /etc/shadow"),
    ):
        response = client.post(f"/api/v1/sources/{src.id}/sync", headers=_headers(token))

    assert response.status_code == 202
    body = response.get_json()
    job_response = client.get(body["job"]["status_url"], headers=_headers(token))
    assert job_response.status_code == 200
    job = job_response.get_json()["job"]
    assert job["status"] == "failed"
    assert job["error"] == "Erreur interne pendant le traitement du job."
    assert "/etc/shadow" not in job["error"]


def test_api_job_status_requiert_permission_operation(client, db):
    token = _token(db, {"sources.view": True})
    src = _source(db)

    from app.models.background_job import BackgroundJob

    job = BackgroundJob(
        operation="source_sync",
        status="succeeded",
        payload={"source_id": src.id},
        result={"fichiers_copies": 0},
    )
    db.session.add(job)
    db.session.commit()

    response = client.get(f"/api/v1/jobs/{job.id}", headers=_headers(token))

    assert response.status_code == 403
    assert "sources.sync" in response.get_json()["missing_permissions"]
