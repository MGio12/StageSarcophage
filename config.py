import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
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


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
