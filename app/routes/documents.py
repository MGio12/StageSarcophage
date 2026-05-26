import os
import tempfile
import zipfile
from datetime import datetime, timezone

from flask import (
    Blueprint,
    abort,
    after_this_request,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
    flash,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.utils.decorators import require_permission
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement
from app.models.source import Source
from app.utils.files import chemin_dans_storage, nom_archive_zip

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")


@documents_bp.route("/")
@login_required
@require_permission("documents.view")
def index():
    sources = Source.query.order_by(Source.nom).all()

    query = Document.query.filter(Document.statut != StatutDocument.PURGE)

    source_id = request.args.get("source_id", type=int)
    if source_id:
        query = query.filter(Document.source_id == source_id)

    statut = request.args.get("statut", "").strip()
    if statut:
        try:
            query = query.filter(Document.statut == StatutDocument(statut))
        except ValueError:
            pass

    q = request.args.get("q", "").strip()
    if q:
        q_escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(Document.nom_fichier.ilike(f"%{q_escaped}%", escape="\\"))

    depuis = request.args.get("depuis", "").strip()
    if depuis:
        try:
            query = query.filter(Document.date_modification_source >= datetime.fromisoformat(depuis))
        except ValueError:
            pass

    jusqua = request.args.get("jusqua", "").strip()
    if jusqua:
        try:
            query = query.filter(
                Document.date_modification_source <= datetime.fromisoformat(f"{jusqua}T23:59:59")
            )
        except ValueError:
            pass

    sort = request.args.get("sort", "nom").strip()
    direction = request.args.get("direction", "asc").strip().lower()
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = request.args.get("per_page", 50, type=int)
    per_page = max(10, min(per_page, 100))

    colonnes_tri = {
        "nom": Document.nom_fichier,
        "source": Source.nom,
        "modification": Document.date_modification_source,
        "age": Document.date_modification_source,
        "taille": Document.taille_octets,
        "statut": Document.statut,
    }
    if sort not in colonnes_tri:
        sort = "nom"
    if direction not in {"asc", "desc"}:
        direction = "asc"

    if sort == "source":
        query = query.outerjoin(Source)

    colonne_tri = colonnes_tri[sort]
    ordre = colonne_tri.desc() if direction == "desc" else colonne_tri.asc()
    pagination = query.order_by(ordre, Document.nom_fichier.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    maintenant = datetime.now(timezone.utc)
    docs_avec_age = []
    for doc in pagination.items:
        age_jours = None
        if doc.date_modification_source:
            mtime = doc.date_modification_source
            if mtime.tzinfo is None:
                mtime = mtime.replace(tzinfo=timezone.utc)
            age_jours = (maintenant - mtime).days
        docs_avec_age.append({"doc": doc, "age_jours": age_jours})

    return render_template(
        "documents/index.html",
        docs_avec_age=docs_avec_age,
        sources=sources,
        source_id_filtre=source_id,
        statut_filtre=statut,
        q_filtre=q,
        depuis_filtre=depuis,
        jusqua_filtre=jusqua,
        pagination=pagination,
        sort=sort,
        direction=direction,
        per_page=per_page,
    )


@documents_bp.route("/<int:doc_id>/voir")
@login_required
@require_permission("documents.view")
def voir(doc_id):
    doc = _document_actif_or_404(doc_id)
    _verifier_chemin(doc.chemin_local)
    entree = Journal(
        source_id=doc.source_id,
        user_id=current_user.id,
        type_evenement=TypeEvenement.ACCES,
        message=f"Consultation : {doc.nom_fichier}",
    )
    db.session.add(entree)
    db.session.commit()
    return render_template("documents/viewer.html", doc=doc)


@documents_bp.route("/<int:doc_id>/telecharger")
@login_required
@require_permission("documents.download")
def telecharger(doc_id):
    doc = _document_actif_or_404(doc_id)
    chemin = _verifier_chemin(doc.chemin_local)
    entree = Journal(
        source_id=doc.source_id,
        user_id=current_user.id,
        type_evenement=TypeEvenement.ACCES,
        message=f"Téléchargement : {doc.nom_fichier}",
    )
    db.session.add(entree)
    db.session.commit()
    return send_file(
        chemin,
        as_attachment=True,
        download_name=doc.nom_fichier,
        mimetype="application/pdf",
    )


@documents_bp.route("/pdf/<int:doc_id>")
@login_required
@require_permission("documents.view")
def pdf_inline(doc_id):
    """Sert le PDF en ligne pour l'affichage dans l'iframe du viewer."""
    doc = _document_actif_or_404(doc_id)
    chemin = _verifier_chemin(doc.chemin_local)
    return send_file(
        chemin,
        mimetype="application/pdf",
        as_attachment=False,
    )


MAX_ZIP_DOCS = 100
MAX_ZIP_OCTETS = 500 * 1024 * 1024  # 500 Mo


@documents_bp.route("/telecharger-zip", methods=["POST"])
@login_required
@require_permission("documents.download")
def telecharger_zip():
    ids = request.form.getlist("doc_ids", type=int)
    if not ids:
        flash("Aucun document sélectionné.", "warning")
        return redirect(url_for("documents.index"))

    if len(ids) > MAX_ZIP_DOCS:
        flash(f"Maximum {MAX_ZIP_DOCS} documents par téléchargement.", "warning")
        return redirect(url_for("documents.index"))

    docs = Document.query.filter(
        Document.id.in_(ids),
        Document.statut != StatutDocument.PURGE,
    ).all()
    docs_valides = []
    for doc in docs:
        try:
            chemin = chemin_dans_storage(doc.chemin_local)
        except ValueError:
            abort(403)
        if os.path.isfile(chemin):
            docs_valides.append((doc, chemin))

    if not docs_valides:
        flash("Aucun fichier disponible pour le téléchargement.", "warning")
        return redirect(url_for("documents.index"))

    taille_totale = sum(d.taille_octets or 0 for d, _chemin in docs_valides)
    if taille_totale > MAX_ZIP_OCTETS:
        flash(f"Taille totale trop importante (max 500 Mo).", "warning")
        return redirect(url_for("documents.index"))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        noms_vus: dict[str, int] = {}
        for doc, chemin in docs_valides:
            nom = nom_archive_zip(doc.nom_fichier)
            if nom in noms_vus:
                base, ext = os.path.splitext(nom)
                nom = f"{base}_{doc.source_id}{ext}"
            noms_vus[nom] = 1
            zf.write(chemin, nom)
    tmp.close()

    @after_this_request
    def _cleanup(response):
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        return response

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name="modes_degrades.zip",
        mimetype="application/zip",
    )


def _document_actif_or_404(doc_id: int) -> Document:
    doc = db.session.get(Document, doc_id)
    if not doc or doc.statut == StatutDocument.PURGE:
        abort(404)
    return doc


def _verifier_chemin(chemin_local: str) -> str:
    """Vérifie que le fichier est bien dans STORAGE_DIR (anti path-traversal)."""
    try:
        cible = chemin_dans_storage(chemin_local)
    except ValueError:
        abort(403)
    if not os.path.isfile(cible):
        abort(404)
    return cible
