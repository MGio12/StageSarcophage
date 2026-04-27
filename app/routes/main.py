from datetime import datetime, timezone

from flask import Blueprint, render_template, request, Response
from flask_login import login_required

from app.extensions import db
from app.models.document import Document, StatutDocument
from app.models.source import Source
from app.models.journal import Journal, TypeEvenement
from app.utils.decorators import require_permission

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    total = Document.query.filter(Document.statut != StatutDocument.PURGE).count()
    nb_ok = Document.query.filter_by(statut=StatutDocument.OK).count()
    nb_avertissement = Document.query.filter_by(statut=StatutDocument.AVERTISSEMENT).count()
    nb_critique = Document.query.filter_by(statut=StatutDocument.CRITIQUE).count()

    sources = Source.query.order_by(Source.nom).all()
    stats_sources = []
    for source in sources:
        nb_docs = Document.query.filter(
            Document.source_id == source.id,
            Document.statut != StatutDocument.PURGE,
        ).count()
        derniere_sync = (
            Journal.query.filter(
                Journal.source_id == source.id,
                Journal.type_evenement == TypeEvenement.SYNC,
            )
            .order_by(Journal.created_at.desc())
            .first()
        )
        stats_sources.append(
            {"source": source, "nb_docs": nb_docs, "derniere_sync": derniere_sync}
        )

    erreurs_recentes = (
        Journal.query.filter_by(type_evenement=TypeEvenement.ERREUR)
        .order_by(Journal.created_at.desc())
        .limit(5)
        .all()
    )
    docs_critiques = (
        Document.query.filter_by(statut=StatutDocument.CRITIQUE)
        .order_by(Document.updated_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "main/dashboard.html",
        total=total,
        nb_ok=nb_ok,
        nb_avertissement=nb_avertissement,
        nb_critique=nb_critique,
        stats_sources=stats_sources,
        erreurs_recentes=erreurs_recentes,
        docs_critiques=docs_critiques,
    )


@main_bp.route("/rapport.xlsx")
@login_required
@require_permission("documents.view")
def rapport_excel():
    source_id = request.args.get("source_id", type=int)
    from app.services.export_service import generer_rapport_excel
    contenu = generer_rapport_excel(source_id)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"rapport_conformite_{date_str}.xlsx"
    return Response(
        contenu,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@main_bp.route("/rapport.pdf")
@login_required
@require_permission("documents.view")
def rapport_pdf():
    source_id = request.args.get("source_id", type=int)
    from app.services.export_service import generer_rapport_pdf
    contenu = generer_rapport_pdf(source_id)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"rapport_conformite_{date_str}.pdf"
    return Response(
        contenu,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
