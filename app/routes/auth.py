"""
Routes d'authentification.

Section 2.6 du CDC — accès protégé par mot de passe.
Phase 2 — authentification LDAP/AD avec fallback local.
"""
import logging
from datetime import datetime, timezone

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db, limiter
from app.models.user import User
from app.models.role import Role

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def _authentifier_utilisateur(username: str, password: str):
    """
    Tente d'authentifier l'utilisateur via LDAP puis en local.

    Returns:
        User ou None
    """
    if current_app.config.get("LDAP_ENABLED"):
        from app.services.ldap_service import authentifier_ldap, get_ldap_config
        if authentifier_ldap(username, password):
            user = User.query.filter_by(username=username).first()
            if not user:
                config = get_ldap_config()
                default_role = Role.query.filter_by(nom=config.default_role).first()
                user = User(username=username, role=default_role, auth_provider="ldap")
                user.set_unusable_password()
                db.session.add(user)
                db.session.commit()
                logger.info("Utilisateur LDAP cree localement : %s", username)
            elif user.auth_provider != "ldap":
                user.auth_provider = "ldap"
                db.session.commit()
            return user

    user = User.query.filter_by(username=username).first()
    if user and user.auth_provider == "ldap":
        logger.warning("Fallback local refuse pour le compte LDAP : %s", username)
        return None

    if user and user.is_active and user.check_password(password):
        return user

    return None


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = _authentifier_utilisateur(username, password)

        if user and user.is_active:
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            login_user(user, remember=request.form.get("remember"))
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))

        flash("Identifiants incorrects.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login"))
