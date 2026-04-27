"""
Décorateurs pour la gestion des permissions.

Phase 2 — CDC §8.2 : gestion des rôles.
"""
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def require_role(*roles):
    """
    Décorateur qui restreint l'accès aux utilisateurs ayant un des rôles spécifiés.

    Usage:
        @require_role('admin')
        def admin_only_view():
            ...

        @require_role('admin', 'moderateur')
        def admin_or_mod_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Veuillez vous connecter pour accéder à cette page.", "warning")
                return redirect(url_for("auth.login"))

            if not current_user.role:
                flash("Accès refusé : aucun rôle assigné.", "danger")
                abort(403)

            if current_user.role.nom not in roles:
                flash("Accès refusé : permissions insuffisantes.", "danger")
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_permission(permission):
    """
    Décorateur qui restreint l'accès aux utilisateurs ayant une permission spécifique.

    Usage:
        @require_permission('sources.edit')
        def edit_source_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Veuillez vous connecter pour accéder à cette page.", "warning")
                return redirect(url_for("auth.login"))

            if not current_user.has_permission(permission):
                flash("Accès refusé : permissions insuffisantes.", "danger")
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Raccourci pour @require_role('admin')."""
    return require_role("admin")(f)
