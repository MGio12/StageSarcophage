from app.models.role import Role
from app.models.user import User


def _login(client, db, permissions):
    role = Role(nom="admin-slice-role", permissions=permissions)
    user = User(username="admin-slice-user", role=role)
    user.set_password("secret123")
    db.session.add_all([role, user])
    db.session.commit()
    with client.session_transaction() as session:
        session["_user_id"] = str(user.id)
        session["_fresh"] = True
    return user


def test_admin_users_permission_autorise_page_utilisateurs(client, db):
    _login(client, db, {"admin.users": True})

    response = client.get("/admin/utilisateurs")

    assert response.status_code == 200


def test_admin_users_permission_ne_donne_pas_acces_aux_roles(client, db):
    _login(client, db, {"admin.users": True})

    response = client.get("/admin/roles")

    assert response.status_code == 403


def test_notifications_aide_smtp_precise_auth_optionnelle(client, db):
    _login(client, db, {"admin.notifications": True})

    response = client.get("/admin/notifications")

    assert response.status_code == 200, response.data.decode()
    assert b"SMTP_HOST" in response.data
    assert b"SMTP_FROM" in response.data
    assert "SMTP_USER et SMTP_PASSWORD seulement si".encode() in response.data
    assert b"SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD et SMTP_FROM" not in response.data
