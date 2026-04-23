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
from app.extensions import db
from app.models.source import Source
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement

sources_bp = Blueprint("sources", __name__, url_prefix="/sources")


@sources_bp.route("/")
def index():
    sources = Source.query.order_by(Source.nom).all()
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


@sources_bp.route("/nouvelle", methods=["GET", "POST"])
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
        flash(f"Source « {source.nom} » créée avec succès.", "success")
        return redirect(url_for("sources.detail", source_id=source.id))
    return render_template("sources/form.html", source=None, titre="Nouvelle source")


@sources_bp.route("/<int:source_id>")
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
def supprimer(source_id):
    source = db.get_or_404(Source, source_id)
    nom = source.nom
    if not current_app.config.get("TESTING"):
        from app.scheduler.tasks import supprimer_job_source
        supprimer_job_source(source_id)
    db.session.delete(source)
    db.session.commit()
    flash(f"Source « {nom} » supprimée.", "info")
    return redirect(url_for("sources.index"))


@sources_bp.route("/<int:source_id>/synchroniser", methods=["POST"])
def synchroniser(source_id):
    source = db.get_or_404(Source, source_id)
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
    return redirect(request.referrer or url_for("sources.detail", source_id=source_id))


@sources_bp.route("/synchroniser-toutes", methods=["POST"])
def synchroniser_toutes():
    sources = Source.query.filter_by(actif=True).all()
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
            total_erreurs += 1
    flash(
        f"Synchronisation globale : {total_copies} fichier(s) copié(s), "
        f"{total_erreurs} erreur(s).",
        "success" if total_erreurs == 0 else "warning",
    )
    return redirect(url_for("main.dashboard"))


@sources_bp.route("/tester-parametres", methods=["POST"])
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
        return jsonify(
            {"succes": resultat.succes, "message": resultat.message, "nb_fichiers": resultat.nb_fichiers}
        )
    except Exception as exc:
        return jsonify({"succes": False, "message": str(exc)})


# ---------------------------------------------------------------------------

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
    source.frequence_sync_minutes = int(request.form.get("frequence_sync_minutes") or 60)
    source.retention_jours = int(request.form.get("retention_jours") or 90)
    source.seuil_avertissement_jours = int(request.form.get("seuil_avertissement_jours") or 30)
    source.seuil_critique_jours = int(request.form.get("seuil_critique_jours") or 60)
    source.actif = "actif" in request.form

    login_val = request.form.get("login", "").strip()
    if login_val:
        source.login = login_val

    mdp_val = request.form.get("mot_de_passe", "").strip()
    if mdp_val:
        source.mot_de_passe = mdp_val

    return source
