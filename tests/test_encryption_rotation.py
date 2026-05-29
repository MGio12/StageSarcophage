from cryptography.fernet import Fernet

from app.models.source import Source


def test_rotate_encryption_key_reencrypts_source_credentials(app, db, monkeypatch):
    old_key = Fernet.generate_key().decode()
    new_key = Fernet.generate_key().decode()
    app.config["ENCRYPTION_KEY"] = old_key

    source = Source(
        nom="Rotation",
        type_serveur="linux",
        protocole="sftp",
        adresse="192.0.2.10",
        chemin_distant="/exports",
    )
    source.login = "svc-rotation"
    source.mot_de_passe = "secret-rotation"
    db.session.add(source)
    db.session.commit()
    old_login_token = source._login
    old_password_token = source._mot_de_passe

    monkeypatch.setenv("OLD_ENCRYPTION_KEY", old_key)
    monkeypatch.setenv("NEW_ENCRYPTION_KEY", new_key)

    result = app.test_cli_runner().invoke(args=["rotate-encryption-key"])

    assert result.exit_code == 0
    db.session.expire_all()
    rotated = db.session.get(Source, source.id)
    assert rotated._login != old_login_token
    assert rotated._mot_de_passe != old_password_token

    app.config["ENCRYPTION_KEY"] = new_key
    assert rotated.login == "svc-rotation"
    assert rotated.mot_de_passe == "secret-rotation"
