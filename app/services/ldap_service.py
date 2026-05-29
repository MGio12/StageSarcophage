"""
Service d'authentification LDAP / Active Directory.

Phase 2 - CDC §8.2 : Authentification LDAP / Active Directory.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError
from ldap3.utils.conv import escape_filter_chars
from flask import current_app

logger = logging.getLogger(__name__)


@dataclass
class LDAPConfig:
    host: str
    port: int
    use_ssl: bool
    base_dn: str
    bind_dn: str
    bind_password: str
    user_filter: str
    default_role: str
    timeout_seconds: int = 10


@dataclass
class LDAPUserInfo:
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    groups: Optional[list] = None


def get_ldap_config() -> Optional[LDAPConfig]:
    if not current_app.config.get("LDAP_ENABLED"):
        return None

    host = current_app.config.get("LDAP_HOST")
    if not host:
        return None

    return LDAPConfig(
        host=host,
        port=current_app.config.get("LDAP_PORT", 389),
        use_ssl=current_app.config.get("LDAP_USE_SSL", False),
        base_dn=current_app.config.get("LDAP_BASE_DN", ""),
        bind_dn=current_app.config.get("LDAP_BIND_DN", ""),
        bind_password=current_app.config.get("LDAP_BIND_PASSWORD", ""),
        user_filter=current_app.config.get("LDAP_USER_FILTER", "(sAMAccountName={username})"),
        default_role=current_app.config.get("LDAP_DEFAULT_ROLE", "lecteur"),
        timeout_seconds=current_app.config.get("LDAP_TIMEOUT_SECONDS", 10),
    )


def _filtre_utilisateur(config: LDAPConfig, username: str) -> str:
    return config.user_filter.format(username=escape_filter_chars(username))


def authentifier_ldap(username: str, password: str) -> bool:
    """
    Authentifie un utilisateur via LDAP.

    Args:
        username: Nom d'utilisateur (sAMAccountName pour AD)
        password: Mot de passe

    Returns:
        True si l'authentification réussit, False sinon
    """
    config = get_ldap_config()
    if not config:
        return False

    if not username or not password:
        return False

    try:
        server = Server(
            config.host,
            port=config.port,
            use_ssl=config.use_ssl,
            get_info=ALL,
            connect_timeout=config.timeout_seconds,
        )

        user_dn = _trouver_dn_utilisateur(server, config, username)
        if not user_dn:
            logger.warning("Utilisateur LDAP non trouve : %s", username)
            return False

        conn = Connection(server, user=user_dn, password=password)
        if conn.bind():
            logger.info("Authentification LDAP reussie : %s", username)
            conn.unbind()
            return True
        else:
            logger.warning("Echec bind LDAP pour %s : %s", username, conn.result)
            return False

    except LDAPBindError as exc:
        logger.warning("Erreur bind LDAP pour %s (%s)", username, type(exc).__name__)
        return False
    except LDAPException as exc:
        logger.error("Erreur LDAP (%s)", type(exc).__name__)
        return False
    except Exception as exc:
        logger.error("Erreur inattendue LDAP (%s)", type(exc).__name__)
        return False


def recuperer_infos_utilisateur(username: str) -> Optional[LDAPUserInfo]:
    """
    Récupère les informations d'un utilisateur depuis LDAP.

    Args:
        username: Nom d'utilisateur

    Returns:
        LDAPUserInfo ou None si non trouvé
    """
    config = get_ldap_config()
    if not config:
        return None

    try:
        server = Server(
            config.host,
            port=config.port,
            use_ssl=config.use_ssl,
            get_info=ALL,
            connect_timeout=config.timeout_seconds,
        )

        conn = Connection(server, user=config.bind_dn, password=config.bind_password)
        if not conn.bind():
            logger.error("Impossible de se connecter au LDAP avec le bind DN")
            return None

        search_filter = _filtre_utilisateur(config, username)
        conn.search(
            config.base_dn,
            search_filter,
            search_scope=SUBTREE,
            attributes=["displayName", "mail", "memberOf", "sAMAccountName"]
        )

        if not conn.entries:
            return None

        entry = conn.entries[0]
        info = LDAPUserInfo(
            username=str(entry.sAMAccountName) if hasattr(entry, "sAMAccountName") else username,
            display_name=str(entry.displayName) if hasattr(entry, "displayName") else None,
            email=str(entry.mail) if hasattr(entry, "mail") else None,
            groups=list(entry.memberOf) if hasattr(entry, "memberOf") else []
        )

        conn.unbind()
        return info

    except LDAPException as exc:
        logger.error("Erreur LDAP lors de la recherche de %s (%s)", username, type(exc).__name__)
        return None


def _trouver_dn_utilisateur(server, config: LDAPConfig, username: str) -> Optional[str]:
    """Trouve le DN complet d'un utilisateur à partir de son username."""
    try:
        conn = Connection(server, user=config.bind_dn, password=config.bind_password)
        if not conn.bind():
            logger.error("Impossible de se connecter au LDAP avec le bind DN")
            return None

        search_filter = _filtre_utilisateur(config, username)
        conn.search(
            config.base_dn,
            search_filter,
            search_scope=SUBTREE,
            attributes=["distinguishedName"]
        )

        if conn.entries:
            dn = conn.entries[0].entry_dn
            conn.unbind()
            return dn

        conn.unbind()
        return None

    except LDAPException as exc:
        logger.error("Erreur lors de la recherche DN (%s)", type(exc).__name__)
        return None


def tester_connexion_ldap() -> tuple[bool, str]:
    """
    Teste la connexion LDAP avec les paramètres configurés.

    Returns:
        Tuple (succès, message)
    """
    config = get_ldap_config()
    if not config:
        return False, "LDAP non configure (LDAP_ENABLED=false ou LDAP_HOST manquant)"

    try:
        server = Server(
            config.host,
            port=config.port,
            use_ssl=config.use_ssl,
            get_info=ALL,
            connect_timeout=config.timeout_seconds,
        )

        conn = Connection(server, user=config.bind_dn, password=config.bind_password)
        if conn.bind():
            info = f"Connecte a {config.host}:{config.port}"
            if server.info:
                info += f" - {server.info.vendor_name or 'LDAP'}"
            conn.unbind()
            return True, info
        else:
            logger.warning(
                "Echec bind LDAP test : %s",
                conn.result.get("description", "erreur inconnue"),
            )
            return False, "Echec bind LDAP."

    except LDAPException as exc:
        logger.warning("Erreur LDAP lors du test de connexion (%s)", type(exc).__name__)
        return False, "Erreur LDAP."
    except Exception as exc:
        logger.error("Erreur inattendue lors du test LDAP (%s)", type(exc).__name__)
        return False, "Erreur LDAP."


def get_group_mapping() -> dict:
    """
    Parse la configuration de mapping groupes AD -> rôles.

    Format LDAP_GROUP_MAPPING : "CN=Admins,OU=Groups,DC=example,DC=com:admin;CN=Users,OU=Groups,DC=example,DC=com:lecteur"
    """
    mapping_str = current_app.config.get("LDAP_GROUP_MAPPING", "")
    if not mapping_str:
        return {}

    mapping = {}
    for pair in mapping_str.split(";"):
        if ":" in pair:
            group_dn, role_name = pair.rsplit(":", 1)
            mapping[group_dn.strip().lower()] = role_name.strip()
    return mapping


def determiner_role_depuis_groupes(groups: list) -> Optional[str]:
    """
    Détermine le rôle applicatif à partir des groupes AD de l'utilisateur.

    Args:
        groups: Liste des DNs de groupes AD (memberOf)

    Returns:
        Nom du rôle correspondant, ou None si aucun mapping
    """
    mapping = get_group_mapping()
    if not mapping:
        return None

    groups_lower = [g.lower() if isinstance(g, str) else str(g).lower() for g in groups]

    if any("admin" in mapping.get(g, "") for g in groups_lower if g in mapping):
        for g in groups_lower:
            if g in mapping and mapping[g] == "admin":
                return "admin"

    for g in groups_lower:
        if g in mapping:
            return mapping[g]

    return None


def synchroniser_groupes_utilisateurs() -> dict:
    """
    Synchronise les rôles de tous les utilisateurs LDAP avec leurs groupes AD.

    Returns:
        Dict avec statistiques : {"synced": n, "unchanged": n, "errors": []}
    """
    from app.extensions import db
    from app.models.user import User
    from app.models.role import Role

    if not current_app.config.get("LDAP_SYNC_GROUPS"):
        return {"synced": 0, "unchanged": 0, "errors": ["LDAP_SYNC_GROUPS desactive"]}

    config = get_ldap_config()
    if not config:
        return {"synced": 0, "unchanged": 0, "errors": ["LDAP non configure"]}

    stats = {"synced": 0, "unchanged": 0, "errors": []}
    roles_cache = {r.nom: r for r in Role.query.all()}

    users = User.query.filter(User.is_active == True).all()

    for user in users:
        try:
            info = recuperer_infos_utilisateur(user.username)
            if not info or not info.groups:
                continue

            nouveau_role_nom = determiner_role_depuis_groupes(info.groups)
            if not nouveau_role_nom:
                nouveau_role_nom = config.default_role

            if nouveau_role_nom not in roles_cache:
                stats["errors"].append(f"Role '{nouveau_role_nom}' inexistant pour {user.username}")
                continue

            nouveau_role = roles_cache[nouveau_role_nom]
            if user.role_id != nouveau_role.id:
                user.role_id = nouveau_role.id
                stats["synced"] += 1
                logger.info("Role de %s mis a jour : %s", user.username, nouveau_role_nom)
            else:
                stats["unchanged"] += 1

        except Exception as exc:
            stats["errors"].append(f"{user.username}: erreur synchronisation")
            logger.warning("Erreur sync groupes pour %s (%s)", user.username, type(exc).__name__)

    db.session.commit()
    return stats
