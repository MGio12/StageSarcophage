from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet

from app import create_app


def test_development_secret_key_is_generated_without_hardcoded_default(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    app = create_app("development")

    assert app.config["SECRET_KEY"]
    assert app.config["SECRET_KEY"] != "dev-secret-change-in-production"


def test_production_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_production_requires_encryption_key(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "prod-secret")
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ENCRYPTION_KEY"):
        create_app("production")


def test_production_uses_secret_key_from_environment(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "prod-secret-from-env")
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())

    with patch("app.scheduler.tasks.demarrer_scheduler"):
        app = create_app("production")

    assert app.config["SECRET_KEY"] == "prod-secret-from-env"
