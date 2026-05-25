from types import SimpleNamespace
from unittest.mock import patch

from app.models.role import Role
from app.models.user import User
from app.routes.auth import _authentifier_utilisateur


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
