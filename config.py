import os
from datetime import timedelta
from sqlalchemy.pool import StaticPool

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _env_bool(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).lower() in ("true", "1", "yes")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Répertoire de stockage local des PDF collectés
    STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(BASE_DIR, "data"))

    # Scheduler APScheduler
    SCHEDULER_API_ENABLED = False
    SCHEDULER_TIMEZONE = os.environ.get("TZ", "Europe/Paris")

    # Durée de session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Clé de chiffrement des identifiants sources (Fernet)
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "")

    # Configuration SMTP pour les notifications
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = os.environ.get("SMTP_PORT", "587")
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM = os.environ.get("SMTP_FROM", "noreply@example.com")
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true")

    # Configuration LDAP / Active Directory
    LDAP_ENABLED = _env_bool("LDAP_ENABLED")
    LDAP_HOST = os.environ.get("LDAP_HOST", "")
    LDAP_PORT = int(os.environ.get("LDAP_PORT", "389"))
    LDAP_USE_SSL = _env_bool("LDAP_USE_SSL")
    LDAP_REQUIRE_TLS = _env_bool("LDAP_REQUIRE_TLS")
    LDAP_TIMEOUT_SECONDS = int(os.environ.get("LDAP_TIMEOUT_SECONDS", "10"))
    LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "")
    LDAP_BIND_DN = os.environ.get("LDAP_BIND_DN", "")
    LDAP_BIND_PASSWORD = os.environ.get("LDAP_BIND_PASSWORD", "")
    LDAP_USER_FILTER = os.environ.get("LDAP_USER_FILTER", "(sAMAccountName={username})")
    LDAP_DEFAULT_ROLE = os.environ.get("LDAP_DEFAULT_ROLE", "lecteur")
    LDAP_GROUP_MAPPING = os.environ.get("LDAP_GROUP_MAPPING", "")
    LDAP_SYNC_GROUPS = _env_bool("LDAP_SYNC_GROUPS")

    # Sources locales : liste de racines autorisées séparées par os.pathsep.
    LOCAL_SOURCE_ALLOWED_ROOTS = os.environ.get("LOCAL_SOURCE_ALLOWED_ROOTS", "")

    # Jobs de fond
    JOB_WORKERS = int(os.environ.get("JOB_WORKERS", "2"))
    JOBS_RUN_INLINE = _env_bool("JOBS_RUN_INLINE")

    # Corbeille (période de grâce avant suppression définitive)
    CORBEILLE_RETENTION_JOURS = int(os.environ.get("CORBEILLE_RETENTION_JOURS", "30"))

    # Cookies de session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Déploiement HTTP derrière reverse proxy TLS par défaut en Docker
    FORCE_HTTPS = _env_bool("FORCE_HTTPS")
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE")
    TRUST_PROXY = _env_bool("TRUST_PROXY")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    FORCE_HTTPS = _env_bool("FORCE_HTTPS", "true")
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", "true")
    PREFERRED_URL_SCHEME = "https"
    LDAP_REQUIRE_TLS = _env_bool("LDAP_REQUIRE_TLS", "true")


def validate_production_config():
    """Vérifie que les secrets requis sont configurés en production."""
    if not os.environ.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY doit être définie en production")
    encryption_key = os.environ.get("ENCRYPTION_KEY")
    if not encryption_key:
        raise RuntimeError("ENCRYPTION_KEY doit être définie en production")
    from cryptography.fernet import Fernet, InvalidToken
    try:
        Fernet(encryption_key.encode())
    except (ValueError, InvalidToken) as e:
        raise RuntimeError(f"ENCRYPTION_KEY invalide (doit être une clé Fernet valide) : {e}")
    if _env_bool("LDAP_ENABLED") and _env_bool("LDAP_REQUIRE_TLS", "true") and not _env_bool("LDAP_USE_SSL"):
        raise RuntimeError("LDAP_REQUIRE_TLS impose LDAP_USE_SSL=true en production")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # StaticPool : une seule connexion partagée → la BD :memory: survit entre les appels
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    WTF_CSRF_ENABLED = False
    STORAGE_DIR = os.path.join(BASE_DIR, "tests", "_tmp_storage")
    JOBS_RUN_INLINE = True
    LDAP_REQUIRE_TLS = False
    # ENCRYPTION_KEY injectée par conftest.py via Fernet.generate_key()


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
