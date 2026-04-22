import os
import sqlite3
import click
from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine
from config import config
from app.extensions import db


@event.listens_for(Engine, "connect")
def _configure_sqlite(dbapi_conn, _record):
    if isinstance(dbapi_conn, sqlite3.Connection):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["STORAGE_DIR"], exist_ok=True)

    db.init_app(app)

    # Enregistrement des modèles pour que SQLAlchemy les connaisse
    from app.models import source, document, journal  # noqa: F401

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    @app.cli.command("init-db")
    def init_db_command():
        """Crée toutes les tables de la base de données."""
        db.create_all()
        click.echo("Base de données initialisée.")

    return app
