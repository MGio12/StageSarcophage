import os
import sqlite3
import click
from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine
from config import config, validate_production_config
from app.extensions import db, csrf, login_manager, limiter


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

    # Validation des secrets en production
    if config_name == "production":
        validate_production_config()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["STORAGE_DIR"], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    if not app.config.get("TESTING"):
        from flask_talisman import Talisman
        Talisman(
            app,
            force_https=config_name == "production",
            content_security_policy={
                "default-src": "'self'",
                "script-src": "'self' 'unsafe-inline'",
                "style-src": "'self' 'unsafe-inline'",
                "img-src": "'self' data:",
                "frame-src": "'self'",
            },
        )

    # Enregistrement des modèles pour que SQLAlchemy les connaisse
    from app.models import source, document, journal, user, ssh_fingerprint, role, api_token, notification_config, setting  # noqa: F401
    from app.models.user import User
    from app.models.role import Role, init_roles
    from app.models.setting import init_settings

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.sources import sources_bp
    from app.routes.documents import documents_bp
    from app.routes.journaux import journaux_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(sources_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(journaux_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.template_filter("format_taille")
    def format_taille(taille):
        if not taille:
            return "—"
        if taille < 1024:
            return f"{taille} o"
        if taille < 1024 * 1024:
            return f"{taille / 1024:.1f} Ko"
        return f"{taille / 1024 / 1024:.1f} Mo"

    @app.cli.command("init-db")
    def init_db_command():
        """Crée toutes les tables de la base de données."""
        db.create_all()
        init_roles()
        init_settings()
        click.echo("Base de données initialisée.")
        click.echo("Rôles par défaut créés (admin, operateur, lecteur).")
        click.echo("Paramètres par défaut initialisés.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True, help="Nom d'utilisateur admin")
    @click.option(
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="Mot de passe admin",
    )
    def create_admin_command(username, password):
        """Crée un utilisateur administrateur."""
        if User.query.filter_by(username=username).first():
            click.echo(f"Erreur : l'utilisateur '{username}' existe déjà.")
            return
        admin_role = Role.query.filter_by(nom="admin").first()
        if not admin_role:
            init_roles()
            admin_role = Role.query.filter_by(nom="admin").first()
        admin = User(username=username, role=admin_role)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Administrateur '{username}' créé avec succès (rôle: admin).")

    if not app.config.get("TESTING"):
        from app.scheduler.tasks import demarrer_scheduler
        demarrer_scheduler(app)

    return app
