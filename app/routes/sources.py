import logging

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from flask_login import login_required

from app.extensions import db, limiter
from app.utils.decorators import require_permission

logger = logging.getLogger(__name__)
from app.models.source import Source
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement

sources_bp = Blueprint("sources", __name__, url_prefix="/sources")


@sources_bp.route("/")
@login_required
@require_permission("sources.view")
def index():
    sources = Source.query.filter(Source.deleted_at.is_(None)).order_by(Source.nom).all()
    stats = {}
    for s in sources:
        nb = Document.query.filter(
            Document.source_id == s.id, Document.statut != StatutDocument.PURGE
        ).count()
        derniere_sync = (
            Journal.query.filter(
                Journal.source_id == s.id,
                Journal.type_evenement == TypeEvenement.SYNC,
            )
            .order_by(Journal.created_at.desc())
            .first()
        )
        stats[s.id] = {"nb_docs": nb, "derniere_sync": derniere_sync}
    return render_template("sources/index.html", sources=sources, stats=stats)


@sources_bp.route("/archivees")
@login_required
@require_permission("sources.view")
def archivees():
    sources = Source.query.filter(Source.deleted_at.isnot(None)).order_by(Source.nom).all()
    stats = {}
    for s in sources:
        nb = Document.query.filter(
            Document.source_id == s.id, Document.statut != StatutDocument.PURGE
        ).count()
        stats[s.id] = {"nb_docs": nb}
    return render_template("sources/archivees.html", sources=sources, stats=stats)


@sources_bp.route("/nouvelle", methods=["GET", "POST"])
@login_required
@require_permission("sources.edit")
def nouvelle():
    if request.method == "POST":
        source = _source_depuis_formulaire(None)
        if source is None:
            return redirect(url_for("sources.nouvelle"))
        db.session.add(source)
        db.session.commit()
        if not current_app.config.get("TESTING"):
            from app.scheduler.tasks import planifier_sync_source
            planifier_sync_source(source, current_app._get_current_object())
        if source.actif and request.form.get("sync_apres_creation"):
            _synchroniser_source_maintenant(source)
        flash(f"Source « {source.nom} » créée avec succès.", "success")
        return redirect(url_for("sources.detail", source_id=source.id))
    return render_template("sources/form.html", source=None, titre="Nouvelle source")


@sources_bp.route("/<int:source_id>")
@login_required
@require_permission("sources.view")
def detail(source_id):
    source = db.get_or_404(Source, source_id)
    docs = (
        Document.query.filter(
            Document.source_id == source_id,
            Document.statut != StatutDocument.PURGE,
        )
        .order_by(Document.nom_fichier)
        .all()
    )
    journaux = (
        Journal.query.filter_by(source_id=source_id)
        .order_by(Journal.created_at.desc())
        .limit(20)
        .all()
    )
    return render_template(
        "sources/detail.html", source=source, docs=docs, journaux=journaux
    )


@sources_bp.route("/<int:source_id>/modifier", methods=["GET", "POST"])
@login_required
@require_permission("sources.edit")
def modifier(source_id):
    source = db.get_or_404(Source, source_id)
    if request.method == "POST":
        source = _source_depuis_formulaire(source)
        if source is None:
            return redirect(url_for("sources.modifier", source_id=source_id))
        db.session.commit()
        if not current_app.config.get("TESTING"):
            from app.scheduler.tasks import planifier_sync_source
            planifier_sync_source(source, current_app._get_current_object())
        flash(f"Source « {source.nom} » modifiée.", "success")
        return redirect(url_for("sources.detail", source_id=source.id))
    return render_template(
        "sources/form.html", source=source, titre=f"Modifier — {source.nom}"
    )


@sources_bp.route("/<int:source_id>/supprimer", methods=["POST"])
@login_required
@require_permission("sources.delete")
def supprimer(source_id):
    from datetime import datetime, timezone
    source = db.get_or_404(Source, source_id)
    nom = source.nom
    if not current_app.config.get("TESTING"):
        from app.scheduler.tasks import supprimer_job_source
        supprimer_job_source(source_id)
    source.actif = False
    source.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    flash(f"Source « {nom} » archivée.", "info")
    return redirect(url_for("sources.index"))


@sources_bp.route("/<int:source_id>/restaurer", methods=["POST"])
@login_required
@require_permission("sources.edit")
def restaurer(source_id):
    source = db.get_or_404(Source, source_id)
    if not source.deleted_at:
        flash("Cette source n'est pas archivée.", "warning")
        return redirect(url_for("sources.detail", source_id=source_id))
    source.deleted_at = None
    source.actif = True
    db.session.commit()
    if not current_app.config.get("TESTING"):
        from app.scheduler.tasks import planifier_sync_source
        planifier_sync_source(source, current_app._get_current_object())
    flash(f"Source « {source.nom} » restaurée.", "success")
    return redirect(url_for("sources.detail", source_id=source_id))


@sources_bp.route("/<int:source_id>/tester", methods=["POST"])
@login_required
@require_permission("sources.view")
@limiter.limit("5 per minute")
def tester(source_id):
    source = db.get_or_404(Source, source_id)
    try:
        resultat = _tester_connexion_source(source)
    except Exception as exc:
        logger.exception("Erreur test source %s", source.nom)
        resultat = {"succes": False, "message": str(exc)}

    if request.accept_mimetypes.best == "application/json" or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(resultat)

    if resultat["succes"]:
        flash(resultat["message"], "success")
    else:
        flash(resultat["message"], "danger")
    return redirect(url_for("sources.detail", source_id=source_id))


@sources_bp.route("/<int:source_id>/synchroniser", methods=["POST"])
@login_required
@require_permission("sources.sync")
@limiter.limit("10 per minute")
def synchroniser(source_id):
    source = db.get_or_404(Source, source_id)
    _synchroniser_source_maintenant(source)
    return redirect(request.referrer or url_for("sources.detail", source_id=source_id))


def _synchroniser_source_maintenant(source: Source) -> None:
    try:
        from app.services.sync_service import synchroniser_source
        from app.services.purge_service import mettre_a_jour_statuts
        resultat = synchroniser_source(source)
        mettre_a_jour_statuts(source)
        flash(
            f"Synchronisation terminée : {resultat.fichiers_copies} copié(s), "
            f"{resultat.fichiers_ignores} ignoré(s), {resultat.erreurs} erreur(s).",
            "success" if resultat.erreurs == 0 else "warning",
        )
    except Exception as exc:
        flash(f"Erreur lors de la synchronisation : {exc}", "danger")


@sources_bp.route("/<int:source_id>/purger", methods=["POST"])
@login_required
@require_permission("sources.purge")
def purger(source_id):
    """Déclenche manuellement la purge des fichiers expirés pour une source."""
    source = db.get_or_404(Source, source_id)
    try:
        from app.services.purge_service import purger_source
        resultat = purger_source(source)
        flash(
            f"Purge terminée : {resultat.fichiers_purges} fichier(s) purgé(s), "
            f"{resultat.erreurs} erreur(s).",
            "success" if resultat.erreurs == 0 else "warning",
        )
    except Exception as exc:
        logger.exception("Erreur purge source %s", source.nom)
        flash(f"Erreur lors de la purge : {exc}", "danger")
    return redirect(url_for("sources.detail", source_id=source_id))


@sources_bp.route("/<int:source_id>/accepter-fingerprint", methods=["POST"])
@login_required
@require_permission("sources.edit")
def accepter_fingerprint(source_id):
    """Accepte et enregistre le fingerprint SSH d'une source SFTP."""
    source = db.get_or_404(Source, source_id)
    if source.protocole != "sftp":
        flash("Cette action n'est disponible que pour les sources SFTP.", "warning")
        return redirect(url_for("sources.detail", source_id=source_id))

    from app.services.sftp_service import accepter_fingerprint as sftp_accept
    if sftp_accept(source):
        flash("Fingerprint SSH accepté et enregistré.", "success")
    else:
        flash("Impossible d'accepter le fingerprint.", "danger")

    return redirect(url_for("sources.detail", source_id=source_id))


@sources_bp.route("/synchroniser-toutes", methods=["POST"])
@login_required
@require_permission("sources.sync")
def synchroniser_toutes():
    sources = Source.query.filter(
        Source.actif == True,
        Source.deleted_at.is_(None)
    ).all()
    total_copies = 0
    total_erreurs = 0
    for source in sources:
        try:
            from app.services.sync_service import synchroniser_source
            from app.services.purge_service import mettre_a_jour_statuts
            resultat = synchroniser_source(source)
            mettre_a_jour_statuts(source)
            total_copies += resultat.fichiers_copies
            total_erreurs += resultat.erreurs
        except Exception:
            logger.exception("Erreur sync source %s", source.nom)
            total_erreurs += 1
    flash(
        f"Synchronisation globale : {total_copies} fichier(s) copié(s), "
        f"{total_erreurs} erreur(s).",
        "success" if total_erreurs == 0 else "warning",
    )
    return redirect(url_for("main.dashboard"))


@sources_bp.route("/tester-parametres", methods=["POST"])
@login_required
@limiter.limit("5 per minute")
def tester_parametres():
    """Test de connexion AJAX avec les valeurs du formulaire (sans source en BD)."""
    protocole = request.form.get("protocole", "sftp")
    try:
        if protocole == "sftp":
            from app.services.sftp_service import tester_connexion
        elif protocole == "smb":
            from app.services.smb_service import tester_connexion
        else:
            return jsonify(
                {"succes": False, "message": f"Test non disponible pour le protocole « {protocole} »"}
            )

        # Objet Source temporaire (non persisté) pour passer les valeurs au connecteur
        source_temp = Source()
        source_temp.protocole = protocole
        source_temp.adresse = request.form.get("adresse", "").strip()
        port_val = request.form.get("port", "").strip()
        source_temp.port = int(port_val) if port_val.isdigit() else None
        source_temp.chemin_distant = request.form.get("chemin_distant", "").strip()
        source_temp.login = request.form.get("login", "").strip()
        source_temp.mot_de_passe = request.form.get("mot_de_passe", "").strip()
        source_temp.filtre_fichiers = request.form.get("filtre_fichiers", "*.pdf").strip() or "*.pdf"

        resultat = tester_connexion(source_temp)
        response = {
            "succes": resultat.succes,
            "message": resultat.message,
            "nb_fichiers": resultat.nb_fichiers,
        }
        if resultat.fingerprint_nouveau:
            response["fingerprint_nouveau"] = resultat.fingerprint_nouveau
            response["fingerprint_key_type"] = resultat.fingerprint_key_type
        return jsonify(response)
    except Exception as exc:
        return jsonify({"succes": False, "message": str(exc)})


# ---------------------------------------------------------------------------


def _parse_int_borne(valeur: str | None, defaut: int, mini: int, maxi: int) -> int:
    """Parse une chaîne en entier, avec défaut et bornes min/max."""
    try:
        n = int(valeur) if valeur else defaut
    except (ValueError, TypeError):
        return defaut
    return max(mini, min(maxi, n))


def _tester_connexion_source(source: Source) -> dict:
    if source.protocole == "sftp":
        from app.services.sftp_service import tester_connexion
    elif source.protocole == "smb":
        from app.services.smb_service import tester_connexion
    elif source.protocole == "local":
        from app.services.sync_service import _lister_local

        fichiers = _lister_local(source)
        return {
            "succes": True,
            "message": f"Connexion locale réussie — {len(fichiers)} fichier(s) trouvé(s)",
            "nb_fichiers": len(fichiers),
        }
    else:
        return {
            "succes": False,
            "message": f"Test non disponible pour le protocole « {source.protocole} »",
        }

    resultat = tester_connexion(source)
    response = {
        "succes": resultat.succes,
        "message": resultat.message,
        "nb_fichiers": resultat.nb_fichiers,
    }
    if getattr(resultat, "fingerprint_nouveau", None):
        response["fingerprint_nouveau"] = resultat.fingerprint_nouveau
        response["fingerprint_key_type"] = resultat.fingerprint_key_type
        response["message"] = (
            f"{resultat.message} Fingerprint {resultat.fingerprint_key_type}: "
            f"{resultat.fingerprint_nouveau}"
        )
    return response


def _source_depuis_formulaire(source: Source | None) -> Source | None:
    nom = request.form.get("nom", "").strip()
    if not nom:
        flash("Le nom de la source est obligatoire.", "danger")
        return None

    if source is None:
        source = Source()

    source.nom = nom
    source.description = request.form.get("description", "").strip() or None
    source.type_serveur = request.form.get("type_serveur", "linux")
    source.protocole = request.form.get("protocole", "sftp")
    source.adresse = request.form.get("adresse", "").strip() or None
    port_val = request.form.get("port", "").strip()
    source.port = int(port_val) if port_val.isdigit() else None
    source.chemin_distant = request.form.get("chemin_distant", "").strip()
    source.filtre_fichiers = request.form.get("filtre_fichiers", "*.pdf").strip() or "*.pdf"
    source.frequence_sync_minutes = _parse_int_borne(
        request.form.get("frequence_sync_minutes"), defaut=60, mini=1, maxi=525600
    )
    source.retention_jours = _parse_int_borne(
        request.form.get("retention_jours"), defaut=90, mini=1, maxi=3650
    )
    source.seuil_avertissement_jours = _parse_int_borne(
        request.form.get("seuil_avertissement_jours"), defaut=30, mini=1, maxi=3650
    )
    source.seuil_critique_jours = _parse_int_borne(
        request.form.get("seuil_critique_jours"), defaut=60, mini=1, maxi=3650
    )
    source.actif = "actif" in request.form

    login_val = request.form.get("login", "").strip()
    if login_val:
        source.login = login_val

    mdp_val = request.form.get("mot_de_passe", "").strip()
    if mdp_val:
        source.mot_de_passe = mdp_val

    return source
