from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from app.models.role import Role
from app.models.source import Source
from app.models.ssh_fingerprint import SSHFingerprint
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


def test_formulaire_source_n_expose_pas_type_serveur(client, db):
    _login(client, db, {"sources.edit": True})

    response = client.get("/sources/nouvelle")

    assert response.status_code == 200, response.data.decode()
    assert b"Type de serveur" not in response.data
    assert b'name="type_serveur"' not in response.data


def test_liste_et_detail_sources_n_exposent_pas_type_serveur(client, db):
    _login(client, db, {"sources.view": True})
    src = _source(db, nom="Visible")

    response_liste = client.get("/sources/")
    response_detail = client.get(f"/sources/{src.id}")

    assert response_liste.status_code == 200, response_liste.data.decode()
    assert response_detail.status_code == 200, response_detail.data.decode()
    assert b'<th scope="col">Type</th>' not in response_liste.data
    assert b'<span class="text-muted">Type</span>' not in response_detail.data


def test_formulaire_modification_affiche_adresse_vide_si_absente(client, db):
    _login(client, db, {"sources.view": True, "sources.edit": True})
    src = _source(db, nom="Sans adresse", adresse=None)

    response = client.get(f"/sources/{src.id}/modifier")

    assert response.status_code == 200, response.data.decode()
    assert b'value="None"' not in response.data
    assert b'id="adresse" name="adresse"' in response.data


def test_creation_sftp_requiert_adresse(client, db):
    _login(client, db, {"sources.view": True, "sources.edit": True})

    response = client.post(
        "/sources/nouvelle",
        data={
            "nom": "SFTP sans adresse",
            "protocole": "sftp",
            "chemin_distant": "/upload",
            "login": "demo",
            "mot_de_passe": "demo123",
            "actif": "on",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200, response.data.decode()
    assert Source.query.filter_by(nom="SFTP sans adresse").first() is None
    assert "Adresse obligatoire".encode() in response.data


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


def test_formulaire_source_explique_fingerprint_non_persistant(client, db):
    _login(client, db, {"sources.edit": True})

    response = client.get("/sources/nouvelle")

    assert response.status_code == 200, response.data.decode()
    assert "Ce test ne l'enregistre pas".encode() in response.data


def test_detail_sftp_affiche_fingerprint_stocke(client, db):
    _login(client, db, {"sources.view": True})
    src = _source(
        db,
        nom="SFTP connu",
        protocole="sftp",
        adresse="sftp",
        port=22,
        chemin_distant="/upload",
    )
    db.session.add(
        SSHFingerprint(
            source_id=src.id,
            hostname="sftp",
            port=22,
            key_type="ssh-ed25519",
            fingerprint="SHA256:fingerprint-stocke",
        )
    )
    db.session.commit()

    response = client.get(f"/sources/{src.id}")

    assert response.status_code == 200, response.data.decode()
    assert b"Fingerprint SSH" in response.data
    assert b"ssh-ed25519" in response.data
    assert b"SHA256:fingerprint-stocke" in response.data
    assert b"Accepter fingerprint" not in response.data


def test_detail_sftp_affiche_action_accepter_si_fingerprint_en_attente(client, db):
    _login(client, db, {"sources.view": True, "sources.edit": True})
    src = _source(
        db,
        nom="SFTP attente",
        protocole="sftp",
        adresse="sftp",
        port=22,
        chemin_distant="/upload",
    )
    with client.session_transaction() as session:
        session[f"sftp_pending_fingerprint:{src.id}"] = {
            "fingerprint": "SHA256:fingerprint-detecte",
            "key_type": "ssh-ed25519",
        }

    response = client.get(f"/sources/{src.id}")

    assert response.status_code == 200, response.data.decode()
    assert b"Accepter fingerprint" in response.data
    assert b"SHA256:fingerprint-detecte" in response.data


def test_tester_sftp_stocke_fingerprint_en_attente(client, db):
    _login(client, db, {"sources.view": True})
    src = _source(
        db,
        nom="SFTP nouveau",
        protocole="sftp",
        adresse="sftp",
        port=22,
        chemin_distant="/upload",
    )
    resultat = SimpleNamespace(
        succes=False,
        message="Nouvelle clé SSH détectée.",
        nb_fichiers=0,
        fingerprint_nouveau="SHA256:fingerprint-detecte",
        fingerprint_key_type="ssh-ed25519",
    )

    with patch("app.services.sftp_service.tester_connexion", return_value=resultat):
        response = client.post(f"/sources/{src.id}/tester", follow_redirects=True)

    assert response.status_code == 200, response.data.decode()
    assert b"SHA256:fingerprint-detecte" in response.data
    with client.session_transaction() as session:
        pending = session[f"sftp_pending_fingerprint:{src.id}"]
    assert pending == {
        "fingerprint": "SHA256:fingerprint-detecte",
        "key_type": "ssh-ed25519",
    }


def test_accepter_fingerprint_requiert_test_fiche_source(client, db):
    _login(client, db, {"sources.view": True, "sources.edit": True})
    src = _source(
        db,
        nom="SFTP sans test",
        protocole="sftp",
        adresse="sftp",
        port=22,
        chemin_distant="/upload",
    )

    with patch("app.services.sftp_service.accepter_fingerprint") as accept:
        response = client.post(
            f"/sources/{src.id}/accepter-fingerprint",
            follow_redirects=True,
        )

    assert response.status_code == 200, response.data.decode()
    accept.assert_not_called()
    assert b"Tester depuis la fiche source" in response.data


def test_accepter_fingerprint_deja_stocke_sans_pending(client, db):
    _login(client, db, {"sources.view": True, "sources.edit": True})
    src = _source(
        db,
        nom="SFTP deja accepte",
        protocole="sftp",
        adresse="sftp",
        port=22,
        chemin_distant="/upload",
    )
    db.session.add(
        SSHFingerprint(
            source_id=src.id,
            hostname="sftp",
            port=22,
            key_type="ssh-ed25519",
            fingerprint="SHA256:fingerprint-stocke",
        )
    )
    db.session.commit()

    with patch("app.services.sftp_service.accepter_fingerprint") as accept:
        response = client.post(
            f"/sources/{src.id}/accepter-fingerprint",
            follow_redirects=True,
        )

    assert response.status_code == 200, response.data.decode()
    accept.assert_not_called()
    assert "Fingerprint SSH déjà accepté".encode() in response.data


def test_accepter_fingerprint_utilise_empreinte_detectee(client, db):
    _login(client, db, {"sources.view": True, "sources.edit": True})
    src = _source(
        db,
        nom="SFTP pret",
        protocole="sftp",
        adresse="sftp",
        port=22,
        chemin_distant="/upload",
    )
    with client.session_transaction() as session:
        session[f"sftp_pending_fingerprint:{src.id}"] = {
            "fingerprint": "SHA256:fingerprint-detecte",
            "key_type": "ssh-ed25519",
        }

    with patch("app.services.sftp_service.accepter_fingerprint", return_value=True) as accept:
        response = client.post(
            f"/sources/{src.id}/accepter-fingerprint",
            follow_redirects=True,
        )

    assert response.status_code == 200, response.data.decode()
    args, kwargs = accept.call_args
    assert args[0].id == src.id
    assert kwargs == {
        "expected_fingerprint": "SHA256:fingerprint-detecte",
        "expected_key_type": "ssh-ed25519",
    }
    with client.session_transaction() as session:
        assert f"sftp_pending_fingerprint:{src.id}" not in session
