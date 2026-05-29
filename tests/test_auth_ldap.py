from types import SimpleNamespace
from unittest.mock import patch

from app.models.role import Role
from app.models.user import User
from app.routes.auth import _authentifier_utilisateur, _is_safe_next_url
from app import create_app
from app.services.ldap_service import (
    LDAPConfig,
    authentifier_ldap,
    _filtre_utilisateur,
    synchroniser_groupes_utilisateurs,
    tester_connexion_ldap,
)


def test_compte_ldap_cree_sans_mot_de_passe_local(app, db):
    app.config["LDAP_ENABLED"] = True
    role = Role(nom="lecteur", permissions={"documents.view": True})
    db.session.add(role)
    db.session.commit()

    with patch("app.services.ldap_service.authentifier_ldap", return_value=True), \
         patch("app.services.ldap_service.get_ldap_config", return_value=SimpleNamespace(default_role="lecteur")):
        user = _authentifier_utilisateur("jdupont", "MotDePasseAD")

    assert user is not None
    assert user.auth_provider == "ldap"
    assert user.role.nom == "lecteur"

    with patch("app.services.ldap_service.authentifier_ldap", return_value=False):
        assert _authentifier_utilisateur("jdupont", "MotDePasseAD") is None


def test_fallback_local_refuse_pour_compte_ldap_existant(app, db):
    app.config["LDAP_ENABLED"] = True
    user = User(username="ldap-user", auth_provider="ldap")
    user.set_password("ancien-mdp-ad")
    db.session.add(user)
    db.session.commit()

    with patch("app.services.ldap_service.authentifier_ldap", return_value=False):
        assert _authentifier_utilisateur("ldap-user", "ancien-mdp-ad") is None


def test_fallback_local_reste_possible_pour_compte_local(app, db):
    app.config["LDAP_ENABLED"] = True
    user = User(username="local-user", auth_provider="local")
    user.set_password("motdepasse-local")
    db.session.add(user)
    db.session.commit()

    with patch("app.services.ldap_service.authentifier_ldap", return_value=False):
        assert _authentifier_utilisateur("local-user", "motdepasse-local") == user


def test_auth_ldap_ne_convertit_pas_compte_local_existant(app, db):
    app.config["LDAP_ENABLED"] = True
    role = Role(nom="admin", permissions={"*": True})
    user = User(username="admin", auth_provider="local", role=role)
    user.set_password("motdepasse-local")
    db.session.add_all([role, user])
    db.session.commit()

    with patch("app.services.ldap_service.authentifier_ldap", return_value=True):
        assert _authentifier_utilisateur("admin", "motdepasse-ad") is None

    assert user.auth_provider == "local"
    assert user.role.nom == "admin"


def test_login_next_refuse_url_scheme_relative():
    assert _is_safe_next_url("//evil.example/path") is False
    assert _is_safe_next_url("/\\evil.example/path") is False
    assert _is_safe_next_url("/documents/") is True


def test_filtre_ldap_echappe_username():
    config = LDAPConfig(
        host="ldap.example.local",
        port=389,
        use_ssl=False,
        base_dn="DC=example,DC=local",
        bind_dn="CN=svc,DC=example,DC=local",
        bind_password="placeholder",  # pragma: allowlist secret
        user_filter="(sAMAccountName={username})",
        default_role="lecteur",
    )

    filtre = _filtre_utilisateur(config, "*)(|(sAMAccountName=admin))")

    assert filtre == r"(sAMAccountName=\2a\29\28|\28sAMAccountName=admin\29\29)"


def test_tester_connexion_ldap_masque_exception(app):
    app.config.update(
        LDAP_ENABLED=True,
        LDAP_HOST="ldap.example.local",
        LDAP_BIND_DN="CN=svc,DC=example,DC=local",
        LDAP_BIND_PASSWORD="super-secret",  # pragma: allowlist secret
    )

    with patch(
        "app.services.ldap_service.Server",
        side_effect=RuntimeError("super-secret /etc/ldap.conf"),  # pragma: allowlist secret
    ):
        success, message = tester_connexion_ldap()

    assert success is False
    assert message == "Erreur LDAP."
    assert "super-secret" not in message
    assert "/etc/ldap.conf" not in message


def test_production_refuse_ldap_sans_tls(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "prod-secret")
    monkeypatch.setenv(
        "ENCRYPTION_KEY",
        "gAAAAABlZHVtbXlfa2V5X2Zvcl90ZXN0aW5nX25vdF91c2Vk",
    )
    from cryptography.fernet import Fernet

    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    monkeypatch.setenv("LDAP_ENABLED", "true")
    monkeypatch.setenv("LDAP_HOST", "ldap.example.local")
    monkeypatch.setenv("LDAP_USE_SSL", "false")

    with patch("app.scheduler.tasks.demarrer_scheduler"):
        try:
            create_app("production")
        except RuntimeError as exc:
            message = str(exc)
        else:
            raise AssertionError("create_app('production') should reject LDAP without TLS")

    assert "LDAP_REQUIRE_TLS" in message


def test_authentifier_ldap_configure_timeout(app):
    app.config.update(
        LDAP_ENABLED=True,
        LDAP_HOST="ldap.example.local",
        LDAP_BIND_DN="CN=svc,DC=example,DC=local",
        LDAP_BIND_PASSWORD="super-secret",  # pragma: allowlist secret
        LDAP_BASE_DN="DC=example,DC=local",
        LDAP_TIMEOUT_SECONDS=7,
    )

    with patch("app.services.ldap_service.Server") as server_cls, \
         patch("app.services.ldap_service._trouver_dn_utilisateur", return_value=None):
        authentifier_ldap("jdupont", "motdepasse")

    assert server_cls.call_args.kwargs["connect_timeout"] == 7


def test_sync_groupes_ldap_masque_exception(app, db):
    app.config.update(LDAP_SYNC_GROUPS=True)
    role = Role(nom="lecteur", permissions={"documents.view": True})
    user = User(username="ldap-user", auth_provider="ldap", role=role)
    user.set_unusable_password()
    db.session.add_all([role, user])
    db.session.commit()

    config = SimpleNamespace(default_role="lecteur")
    with patch("app.services.ldap_service.get_ldap_config", return_value=config), \
         patch(
             "app.services.ldap_service.recuperer_infos_utilisateur",
             side_effect=RuntimeError("super-secret /etc/ldap.conf"),  # pragma: allowlist secret
         ):
        stats = synchroniser_groupes_utilisateurs()

    assert stats["errors"] == ["ldap-user: erreur synchronisation"]
    assert "super-secret" not in stats["errors"][0]
    assert "/etc/ldap.conf" not in stats["errors"][0]
