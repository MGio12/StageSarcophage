import os
import pytest
from cryptography.fernet import Fernet
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    # Clé Fernet valide générée pour la session de test
    application.config["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    os.makedirs(application.config["STORAGE_DIR"], exist_ok=True)

    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Base de données propre pour chaque test (rollback après)."""
    yield _db
    _db.session.rollback()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()
