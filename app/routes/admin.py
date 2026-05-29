"""
Routes d'administration.

Phase 2 - CDC §8.2 : gestion des rôles et API REST.
"""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import login_required

from app.extensions import db
from app.models.role import Role, PERMISSIONS_DISPONIBLES
from app.models.user import User
from app.models.api_token import APIToken
from app.models.notification_config import NotificationConfig
from app.models.setting import Setting, SETTINGS_DEFAUT
from app.utils.decorators import require_permission

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/utilisateurs")
@login_required
@require_permission("admin.users")
def utilisateurs():
    users = User.query.order_by(User.username).all()
    return render_template("admin/utilisateurs.html", users=users)


@admin_bp.route("/utilisateurs/nouveau", methods=["GET", "POST"])
@login_required
@require_permission("admin.users")
def utilisateur_nouveau():
    roles = Role.query.order_by(Role.nom).all()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role_id = request.form.get("role_id", type=int)

        if not username:
            flash("Le nom d'utilisateur est obligatoire.", "danger")
            return render_template("admin/utilisateur_form.html", user=None, roles=roles)

        if not password:
            flash("Le mot de passe est obligatoire.", "danger")
            return render_template("admin/utilisateur_form.html", user=None, roles=roles)

        if len(password) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.", "danger")
            return render_template("admin/utilisateur_form.html", user=None, roles=roles)

        if User.query.filter_by(username=username).first():
            flash(f"L'utilisateur « {username} » existe déjà.", "danger")
            return render_template("admin/utilisateur_form.html", user=None, roles=roles)

        user = User(username=username, role_id=role_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f"Utilisateur « {username} » créé avec succès.", "success")
        return redirect(url_for("admin.utilisateurs"))

    return render_template("admin/utilisateur_form.html", user=None, roles=roles)


@admin_bp.route("/utilisateurs/<int:user_id>/modifier", methods=["GET", "POST"])
@login_required
@require_permission("admin.users")
def utilisateur_modifier(user_id):
    user = db.get_or_404(User, user_id)
    roles = Role.query.order_by(Role.nom).all()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role_id = request.form.get("role_id", type=int)

        if not username:
            flash("Le nom d'utilisateur est obligatoire.", "danger")
            return render_template("admin/utilisateur_form.html", user=user, roles=roles)

        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != user.id:
            flash(f"L'utilisateur « {username} » existe déjà.", "danger")
            return render_template("admin/utilisateur_form.html", user=user, roles=roles)

        user.username = username
        user.role_id = role_id

        if password:
            if len(password) < 8:
                flash("Le mot de passe doit contenir au moins 8 caractères.", "danger")
                return render_template("admin/utilisateur_form.html", user=user, roles=roles)
            user.set_password(password)

        db.session.commit()
        flash(f"Utilisateur « {username} » modifié.", "success")
        return redirect(url_for("admin.utilisateurs"))

    return render_template("admin/utilisateur_form.html", user=user, roles=roles)


@admin_bp.route("/utilisateurs/<int:user_id>/activer", methods=["POST"])
@login_required
@require_permission("admin.users")
def utilisateur_activer(user_id):
    user = db.get_or_404(User, user_id)
    user.is_active = True
    db.session.commit()
    flash(f"Utilisateur « {user.username} » activé.", "success")
    return redirect(url_for("admin.utilisateurs"))


@admin_bp.route("/utilisateurs/<int:user_id>/desactiver", methods=["POST"])
@login_required
@require_permission("admin.users")
def utilisateur_desactiver(user_id):
    user = db.get_or_404(User, user_id)
    user.is_active = False
    db.session.commit()
    flash(f"Utilisateur « {user.username} » désactivé.", "info")
    return redirect(url_for("admin.utilisateurs"))


@admin_bp.route("/tokens")
@login_required
@require_permission("admin.tokens")
def tokens():
    tokens_list = APIToken.query.order_by(APIToken.created_at.desc()).all()
    now = datetime.now(timezone.utc)
    return render_template("admin/tokens.html", tokens=tokens_list, now=now)


@admin_bp.route("/tokens/nouveau", methods=["GET", "POST"])
@login_required
@require_permission("admin.tokens")
def token_nouveau():
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    if request.method == "POST":
        user_id = request.form.get("user_id", type=int)
        nom = request.form.get("nom", "").strip()
        duree_jours = request.form.get("duree_jours", type=int)

        if not user_id:
            flash("L'utilisateur est obligatoire.", "danger")
            return render_template("admin/token_form.html", users=users)

        if not nom:
            flash("Le nom du token est obligatoire.", "danger")
            return render_template("admin/token_form.html", users=users)

        expires_at = None
        if duree_jours and duree_jours > 0:
            expires_at = datetime.now(timezone.utc) + timedelta(days=duree_jours)

        api_token, token_clair = APIToken.create(user_id, nom, expires_at)
        db.session.add(api_token)
        db.session.commit()

        return render_template(
            "admin/token_created.html",
            token=token_clair,
            nom=nom
        )

    return render_template("admin/token_form.html", users=users)


@admin_bp.route("/tokens/<int:token_id>/revoquer", methods=["POST"])
@login_required
@require_permission("admin.tokens")
def token_revoquer(token_id):
    api_token = db.get_or_404(APIToken, token_id)
    api_token.is_active = False
    db.session.commit()
    flash(f"Token « {api_token.nom} » revoque.", "info")
    return redirect(url_for("admin.tokens"))


@admin_bp.route("/notifications")
@login_required
@require_permission("admin.notifications")
def notifications():
    configs = NotificationConfig.query.order_by(NotificationConfig.email).all()
    return render_template("admin/notifications.html", configs=configs)


@admin_bp.route("/notifications/nouveau", methods=["GET", "POST"])
@login_required
@require_permission("admin.notifications")
def notification_nouvelle():
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user_id = request.form.get("user_id", type=int) or None
        notif_erreurs = "notif_erreurs" in request.form
        notif_critiques = "notif_critiques" in request.form

        if not email:
            flash("L'adresse email est obligatoire.", "danger")
            return render_template("admin/notification_form.html", config=None, users=users)

        if NotificationConfig.query.filter_by(email=email).first():
            flash(f"L'adresse « {email} » est deja configuree.", "danger")
            return render_template("admin/notification_form.html", config=None, users=users)

        config = NotificationConfig(
            email=email,
            user_id=user_id,
            notif_erreurs=notif_erreurs,
            notif_critiques=notif_critiques
        )
        db.session.add(config)
        db.session.commit()
        flash(f"Destinataire « {email} » ajoute.", "success")
        return redirect(url_for("admin.notifications"))

    return render_template("admin/notification_form.html", config=None, users=users)


@admin_bp.route("/notifications/<int:config_id>/modifier", methods=["GET", "POST"])
@login_required
@require_permission("admin.notifications")
def notification_modifier(config_id):
    config = db.get_or_404(NotificationConfig, config_id)
    users = User.query.filter_by(is_active=True).order_by(User.username).all()

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user_id = request.form.get("user_id", type=int) or None
        config.notif_erreurs = "notif_erreurs" in request.form
        config.notif_critiques = "notif_critiques" in request.form
        config.actif = "actif" in request.form

        if not email:
            flash("L'adresse email est obligatoire.", "danger")
            return render_template("admin/notification_form.html", config=config, users=users)

        existing = NotificationConfig.query.filter_by(email=email).first()
        if existing and existing.id != config.id:
            flash(f"L'adresse « {email} » est deja utilisee.", "danger")
            return render_template("admin/notification_form.html", config=config, users=users)

        config.email = email
        config.user_id = user_id
        db.session.commit()
        flash(f"Configuration modifiee.", "success")
        return redirect(url_for("admin.notifications"))

    return render_template("admin/notification_form.html", config=config, users=users)


@admin_bp.route("/notifications/<int:config_id>/supprimer", methods=["POST"])
@login_required
@require_permission("admin.notifications")
def notification_supprimer(config_id):
    config = db.get_or_404(NotificationConfig, config_id)
    email = config.email
    db.session.delete(config)
    db.session.commit()
    flash(f"Destinataire « {email} » supprime.", "info")
    return redirect(url_for("admin.notifications"))


@admin_bp.route("/notifications/test", methods=["POST"])
@login_required
@require_permission("admin.notifications")
def notification_test():
    email = request.form.get("email", "").strip()
    if not email:
        flash("Adresse email requise.", "danger")
        return redirect(url_for("admin.notifications"))

    from app.services.email_service import envoyer_email_test
    if envoyer_email_test(email):
        flash(f"Email de test envoye a {email}.", "success")
    else:
        flash("Echec de l'envoi. Verifiez la configuration SMTP.", "danger")
    return redirect(url_for("admin.notifications"))


@admin_bp.route("/roles")
@login_required
@require_permission("admin.roles")
def roles():
    roles_list = Role.query.order_by(Role.nom).all()
    return render_template("admin/roles.html", roles=roles_list)


@admin_bp.route("/roles/nouveau", methods=["GET", "POST"])
@login_required
@require_permission("admin.roles")
def role_nouveau():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip().lower()
        description = request.form.get("description", "").strip()

        if not nom:
            flash("Le nom du role est obligatoire.", "danger")
            return render_template("admin/role_form.html", role=None, permissions=PERMISSIONS_DISPONIBLES)

        if Role.query.filter_by(nom=nom).first():
            flash(f"Le role '{nom}' existe deja.", "danger")
            return render_template("admin/role_form.html", role=None, permissions=PERMISSIONS_DISPONIBLES)

        permissions = {}
        for perm_key in PERMISSIONS_DISPONIBLES:
            if request.form.get(f"perm_{perm_key}"):
                permissions[perm_key] = True

        role = Role(nom=nom, description=description, permissions=permissions)
        db.session.add(role)
        db.session.commit()
        flash(f"Role '{nom}' cree.", "success")
        return redirect(url_for("admin.roles"))

    return render_template("admin/role_form.html", role=None, permissions=PERMISSIONS_DISPONIBLES)


@admin_bp.route("/roles/<int:role_id>/modifier", methods=["GET", "POST"])
@login_required
@require_permission("admin.roles")
def role_modifier(role_id):
    role = db.get_or_404(Role, role_id)

    if role.nom == "admin":
        flash("Le role admin ne peut pas etre modifie.", "warning")
        return redirect(url_for("admin.roles"))

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        role.description = description

        permissions = {}
        for perm_key in PERMISSIONS_DISPONIBLES:
            if request.form.get(f"perm_{perm_key}"):
                permissions[perm_key] = True

        role.permissions = permissions
        db.session.commit()
        flash(f"Role '{role.nom}' modifie.", "success")
        return redirect(url_for("admin.roles"))

    return render_template("admin/role_form.html", role=role, permissions=PERMISSIONS_DISPONIBLES)


@admin_bp.route("/roles/<int:role_id>/supprimer", methods=["POST"])
@login_required
@require_permission("admin.roles")
def role_supprimer(role_id):
    role = db.get_or_404(Role, role_id)

    if role.nom in ("admin", "lecteur"):
        flash("Les roles systeme ne peuvent pas etre supprimes.", "danger")
        return redirect(url_for("admin.roles"))

    if role.users.count() > 0:
        flash(f"Impossible de supprimer : {role.users.count()} utilisateur(s) utilisent ce role.", "danger")
        return redirect(url_for("admin.roles"))

    nom = role.nom
    db.session.delete(role)
    db.session.commit()
    flash(f"Role '{nom}' supprime.", "info")
    return redirect(url_for("admin.roles"))


@admin_bp.route("/parametres")
@login_required
@require_permission("admin.settings")
def parametres():
    settings_list = Setting.query.order_by(Setting.cle).all()
    return render_template("admin/parametres.html", settings=settings_list, defaults=SETTINGS_DEFAUT)


@admin_bp.route("/parametres/modifier", methods=["POST"])
@login_required
@require_permission("admin.settings")
def parametres_modifier():
    for cle in SETTINGS_DEFAUT:
        valeur = request.form.get(cle, "").strip()
        setting = Setting.query.filter_by(cle=cle).first()
        if setting:
            setting.valeur = valeur
        else:
            Setting.set(cle, valeur, SETTINGS_DEFAUT[cle]["description"], SETTINGS_DEFAUT[cle]["type"])

    db.session.commit()
    flash("Parametres enregistres.", "success")
    return redirect(url_for("admin.parametres"))


@admin_bp.route("/ldap")
@login_required
@require_permission("admin.settings")
def ldap():
    ldap_enabled = current_app.config.get("LDAP_ENABLED", False)
    ldap_sync_groups = current_app.config.get("LDAP_SYNC_GROUPS", False)
    return render_template("admin/ldap.html", ldap_enabled=ldap_enabled, ldap_sync_groups=ldap_sync_groups)


@admin_bp.route("/ldap/test", methods=["POST"])
@login_required
@require_permission("admin.settings")
def ldap_test():
    from app.services.ldap_service import tester_connexion_ldap
    success, message = tester_connexion_ldap()
    if success:
        flash(f"Connexion LDAP reussie : {message}", "success")
    else:
        flash(f"Echec connexion LDAP : {message}", "danger")
    return redirect(url_for("admin.ldap"))


@admin_bp.route("/ldap/sync-groupes", methods=["POST"])
@login_required
@require_permission("admin.settings")
def ldap_sync_groupes():
    from app.services.ldap_service import synchroniser_groupes_utilisateurs

    if not current_app.config.get("LDAP_SYNC_GROUPS"):
        flash("Synchronisation des groupes LDAP desactivee.", "warning")
        return redirect(url_for("admin.ldap"))

    stats = synchroniser_groupes_utilisateurs()

    if stats["errors"]:
        for err in stats["errors"][:5]:
            flash(f"Erreur : {err}", "warning")

    flash(f"Synchronisation terminee : {stats['synced']} mis a jour, {stats['unchanged']} inchanges.", "success")
    return redirect(url_for("admin.ldap"))
