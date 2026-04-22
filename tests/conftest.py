import os
import pytest
from cryptography.fernet import Fernet
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    application.config["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    os.makedirs(application.config["STORAGE_DIR"], exist_ok=True)

    # Un seul contexte applicatif pour toute la session de tests
    ctx = application.app_context()
    ctx.push()
    yield application
    ctx.pop()


@pytest.fixture(scope="function")
def db(app):
    """Tables fraîches pour chaque test ; drop_all après garantit l'isolation."""
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()
