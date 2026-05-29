import os
import secrets
import sqlite3
import click
from flask import Flask, g, redirect, request
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

    if config_name == "production":
        validate_production_config()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    _apply_runtime_secrets(app)
    app.jinja_env.globals.setdefault("csp_nonce", _csp_nonce)

    _configure_proxy(app)
    _ensure_runtime_directories(app)
    _register_extensions(app)
    _register_security_headers(app)
    _register_models_and_login()
    _register_blueprints(app)
    _register_template_filters(app)
    _register_cli(app)
    _start_scheduler(app)

    return app


def _configure_proxy(app: Flask) -> None:
    if app.config.get("TRUST_PROXY"):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


def _ensure_runtime_directories(app: Flask) -> None:
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["STORAGE_DIR"], exist_ok=True)


def _apply_runtime_secrets(app: Flask) -> None:
    secret_key = os.environ.get("SECRET_KEY")
    if secret_key:
        app.config["SECRET_KEY"] = secret_key
    elif not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = secrets.token_urlsafe(32)

    encryption_key = os.environ.get("ENCRYPTION_KEY")
    if encryption_key:
        app.config["ENCRYPTION_KEY"] = encryption_key


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)


def _register_security_headers(app: Flask) -> None:
    if app.config.get("TESTING"):
        return

    app.jinja_env.globals["csp_nonce"] = _csp_nonce

    @app.before_request
    def enforce_https():
        if app.config.get("FORCE_HTTPS") and not request.is_secure:
            return redirect(request.url.replace("http://", "https://", 1), code=301)
        return None

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("Content-Security-Policy", _content_security_policy())
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        if request.is_secure or app.config.get("FORCE_HTTPS"):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31556926; includeSubDomains",
            )
        return response


def _csp_nonce() -> str:
    if not hasattr(g, "csp_nonce"):
        g.csp_nonce = secrets.token_urlsafe(16)
    return g.csp_nonce


def _content_security_policy() -> str:
    nonce = _csp_nonce()
    directives = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "https://cdn.jsdelivr.net", f"'nonce-{nonce}'"],
        "style-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        "img-src": ["'self'", "data:"],
        "font-src": ["'self'", "data:", "https://cdn.jsdelivr.net"],
        "connect-src": ["'self'"],
        "frame-src": ["'self'"],
        "frame-ancestors": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }
    return "; ".join(
        f"{directive} {' '.join(values)}" for directive, values in directives.items()
    )


def _register_models_and_login() -> None:
    from app.models import source, document, journal, user, ssh_fingerprint, role, api_token, background_job, notification_config, setting  # noqa: F401
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


def _register_blueprints(app: Flask) -> None:
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.sources import sources_bp
    from app.routes.documents import documents_bp
    from app.routes.journaux import journaux_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    csrf.exempt(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(sources_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(journaux_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)


def _register_template_filters(app: Flask) -> None:
    @app.template_filter("format_taille")
    def format_taille(taille):
        if not taille:
            return "-"
        if taille < 1024:
            return f"{taille} o"
        if taille < 1024 * 1024:
            return f"{taille / 1024:.1f} Ko"
        return f"{taille / 1024 / 1024:.1f} Mo"


def _register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command():
        """Crée ou met à jour le schéma de la base de données."""
        from app.services.migration_service import run_schema_migrations
        from app.models.role import init_roles
        from app.models.setting import init_settings

        operations = run_schema_migrations()
        init_roles()
        init_settings()
        click.echo("Base de données initialisée/mise à jour.")
        if operations:
            click.echo("Colonnes ajoutées : " + ", ".join(operations))
        click.echo("Rôles par défaut créés (admin, operateur, lecteur).")
        click.echo("Paramètres par défaut initialisés.")

    @app.cli.command("upgrade-db")
    def upgrade_db_command():
        """Applique les migrations idempotentes sur une base existante."""
        from app.services.migration_service import run_schema_migrations
        from app.models.role import init_roles
        from app.models.setting import init_settings

        operations = run_schema_migrations()
        init_roles()
        init_settings()
        if operations:
            click.echo("Colonnes ajoutées : " + ", ".join(operations))
        else:
            click.echo("Base de données déjà à jour.")

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
        from app.models.role import Role, init_roles
        from app.models.user import User

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

    @app.cli.command("rotate-encryption-key")
    def rotate_encryption_key_command():
        """Ré-encrypte les identifiants Source avec une nouvelle clé Fernet."""
        from app.services.encryption_rotation_service import rotate_source_credentials

        old_key = os.environ.get("OLD_ENCRYPTION_KEY")
        new_key = os.environ.get("NEW_ENCRYPTION_KEY")
        if not old_key:
            raise click.ClickException("OLD_ENCRYPTION_KEY doit être définie.")
        if not new_key:
            raise click.ClickException("NEW_ENCRYPTION_KEY doit être définie.")

        try:
            updated_fields = rotate_source_credentials(old_key, new_key)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo(f"Identifiants sources ré-encryptés: {updated_fields} champ(s).")


def _start_scheduler(app: Flask) -> None:
    if not app.config.get("TESTING"):
        from app.scheduler.tasks import demarrer_scheduler
        demarrer_scheduler(app)
