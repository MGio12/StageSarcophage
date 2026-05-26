from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from app.models.role import Role
from app.models.source import Source
from app.models.user import User


def _login(client, db, permissions):
    role = Role(nom="sources-role", permissions=permissions)
    user = User(username="source-user", role=role)
    user.set_password("secret123")
    db.session.add_all([role, user])
    db.session.commit()
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True
    return user


def _source(db, **kwargs):
    defaults = dict(
        nom="Source route",
        type_serveur="linux",
        protocole="local",
        chemin_distant="/tmp",
    )
    defaults.update(kwargs)
    src = Source(**defaults)
    db.session.add(src)
    db.session.commit()
    return src


def test_liste_sources_archivees_affiche_restauration(client, db):
    _login(client, db, {"sources.view": True, "sources.edit": True})
    _source(db, nom="Archivee", actif=False, deleted_at=datetime.now(timezone.utc))

    response = client.get("/sources/archivees")

    assert response.status_code == 200, response.data.decode()
    assert b"Archivee" in response.data
    assert b"Restaurer" in response.data


def test_route_tester_source_retourne_json(client, db):
    _login(client, db, {"sources.view": True})
    src = _source(db)

    with patch("app.routes.sources._tester_connexion_source", return_value={"succes": True, "message": "OK", "nb_fichiers": 1}):
        response = client.post(
            f"/sources/{src.id}/tester",
            headers={"Accept": "application/json"},
        )

    assert response.status_code == 200, response.data.decode()
    assert response.get_json()["succes"] is True


def test_route_tester_source_masque_exception_json(client, db):
    _login(client, db, {"sources.view": True})
    src = _source(db)

    with patch("app.routes.sources._tester_connexion_source", side_effect=RuntimeError("secret /etc/shadow")):
        response = client.post(
            f"/sources/{src.id}/tester",
            headers={"Accept": "application/json"},
        )

    assert response.status_code == 200, response.data.decode()
    body = response.get_json()
    assert body["succes"] is False
    assert body["message"] == "Test de connexion impossible."
    assert "/etc/shadow" not in body["message"]


def test_tester_parametres_requiert_sources_edit(client, db):
    _login(client, db, {"sources.view": True})

    with patch("app.services.sftp_service.tester_connexion") as tester_connexion:
        response = client.post(
            "/sources/tester-parametres",
            data={"protocole": "sftp", "adresse": "127.0.0.1", "chemin_distant": "/"},
            headers={"Accept": "application/json"},
        )

    assert response.status_code == 403
    tester_connexion.assert_not_called()


def test_tester_parametres_autorise_sources_edit(client, db):
    _login(client, db, {"sources.edit": True})

    resultat = SimpleNamespace(
        succes=True,
        message="OK",
        nb_fichiers=0,
        fingerprint_nouveau=None,
    )
    with patch("app.services.sftp_service.tester_connexion", return_value=resultat):
        response = client.post(
            "/sources/tester-parametres",
            data={"protocole": "sftp", "adresse": "127.0.0.1", "chemin_distant": "/"},
            headers={"Accept": "application/json"},
        )

    assert response.status_code == 200, response.data.decode()
    assert response.get_json()["succes"] is True


def test_tester_parametres_masque_exception(client, db):
    _login(client, db, {"sources.edit": True})

    with patch("app.services.sftp_service.tester_connexion", side_effect=RuntimeError("password=secret")):
        response = client.post(
            "/sources/tester-parametres",
            data={"protocole": "sftp", "adresse": "127.0.0.1", "chemin_distant": "/"},
            headers={"Accept": "application/json"},
        )

    assert response.status_code == 200, response.data.decode()
    body = response.get_json()
    assert body["succes"] is False
    assert body["message"] == "Test de connexion impossible."
    assert "secret" not in body["message"]
