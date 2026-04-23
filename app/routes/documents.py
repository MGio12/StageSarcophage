import io
import os
import zipfile
from datetime import datetime, timezone

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
    flash,
)

from app.extensions import db
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement
from app.models.source import Source

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")


@documents_bp.route("/")
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
        query = query.filter(Document.nom_fichier.ilike(f"%{q}%"))

    docs = query.order_by(Document.nom_fichier).all()

    maintenant = datetime.now(timezone.utc)
    docs_avec_age = []
    for doc in docs:
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
    )


@documents_bp.route("/<int:doc_id>/voir")
def voir(doc_id):
    doc = db.get_or_404(Document, doc_id)
    if not os.path.exists(doc.chemin_local):
        abort(404)
    entree = Journal(
        source_id=doc.source_id,
        type_evenement=TypeEvenement.ACCES,
        message=f"Consultation : {doc.nom_fichier}",
    )
    db.session.add(entree)
    db.session.commit()
    return render_template("documents/viewer.html", doc=doc)


@documents_bp.route("/<int:doc_id>/telecharger")
def telecharger(doc_id):
    doc = db.get_or_404(Document, doc_id)
    if not os.path.exists(doc.chemin_local):
        abort(404)
    entree = Journal(
        source_id=doc.source_id,
        type_evenement=TypeEvenement.ACCES,
        message=f"Téléchargement : {doc.nom_fichier}",
    )
    db.session.add(entree)
    db.session.commit()
    return send_file(
        doc.chemin_local,
        as_attachment=True,
        download_name=doc.nom_fichier,
        mimetype="application/pdf",
    )


@documents_bp.route("/pdf/<int:doc_id>")
def pdf_inline(doc_id):
    """Sert le PDF en ligne pour l'affichage dans l'iframe du viewer."""
    doc = db.get_or_404(Document, doc_id)
    _verifier_chemin(doc.chemin_local)
    return send_file(
        doc.chemin_local,
        mimetype="application/pdf",
        as_attachment=False,
    )


@documents_bp.route("/telecharger-zip", methods=["POST"])
def telecharger_zip():
    ids = request.form.getlist("doc_ids", type=int)
    if not ids:
        flash("Aucun document sélectionné.", "warning")
        return redirect(url_for("documents.index"))

    docs = Document.query.filter(Document.id.in_(ids)).all()
    docs_valides = [d for d in docs if os.path.exists(d.chemin_local)]

    if not docs_valides:
        flash("Aucun fichier disponible pour le téléchargement.", "warning")
        return redirect(url_for("documents.index"))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        noms_vus: dict[str, int] = {}
        for doc in docs_valides:
            nom = doc.nom_fichier
            if nom in noms_vus:
                base, ext = os.path.splitext(nom)
                nom = f"{base}_{doc.source_id}{ext}"
            noms_vus[nom] = 1
            zf.write(doc.chemin_local, nom)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name="modes_degrades.zip",
        mimetype="application/zip",
    )


def _verifier_chemin(chemin_local: str) -> None:
    """Vérifie que le fichier est bien dans STORAGE_DIR (anti path-traversal)."""
    storage = os.path.realpath(current_app.config["STORAGE_DIR"])
    cible = os.path.realpath(chemin_local)
    if not cible.startswith(storage):
        abort(403)
    if not os.path.exists(cible):
        abort(404)
