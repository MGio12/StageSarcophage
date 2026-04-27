import csv
import io
from datetime import datetime

from flask import Blueprint, Response, render_template, request
from flask_login import login_required

from app.extensions import db
from app.utils.decorators import require_permission
from app.models.journal import Journal, TypeEvenement
from app.models.source import Source
from app.models.user import User

journaux_bp = Blueprint("journaux", __name__, url_prefix="/journaux")


def _appliquer_filtres(query):
    type_evt = request.args.get("type", "").strip()
    if type_evt:
        try:
            query = query.filter(Journal.type_evenement == TypeEvenement(type_evt))
        except ValueError:
            pass

    source_id = request.args.get("source_id", type=int)
    if source_id:
        query = query.filter(Journal.source_id == source_id)

    depuis = request.args.get("depuis", "").strip()
    if depuis:
        try:
            query = query.filter(Journal.created_at >= datetime.fromisoformat(depuis))
        except ValueError:
            pass

    jusqua = request.args.get("jusqua", "").strip()
    if jusqua:
        try:
            query = query.filter(
                Journal.created_at <= datetime.fromisoformat(f"{jusqua}T23:59:59")
            )
        except ValueError:
            pass

    return query


@journaux_bp.route("/")
@login_required
@require_permission("journal.view")
def index():
    sources = Source.query.order_by(Source.nom).all()
    query = _appliquer_filtres(Journal.query)
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Journal.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template(
        "journaux/index.html",
        pagination=pagination,
        journaux=pagination.items,
        sources=sources,
        type_filtre=request.args.get("type", ""),
        source_id_filtre=request.args.get("source_id", type=int),
        depuis_filtre=request.args.get("depuis", ""),
        jusqua_filtre=request.args.get("jusqua", ""),
        TypeEvenement=TypeEvenement,
    )


@journaux_bp.route("/export.csv")
@login_required
@require_permission("journal.view")
def export_csv():
    sources = Source.query.order_by(Source.nom).all()
    source_map = {s.id: s.nom for s in sources}

    users = User.query.all()
    user_map = {u.id: u.username for u in users}

    query = _appliquer_filtres(Journal.query)
    journaux = query.order_by(Journal.created_at.desc()).limit(10000).all()

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["Date", "Type", "Source", "Utilisateur", "Message"])
    for j in journaux:
        writer.writerow([
            j.created_at.strftime("%Y-%m-%d %H:%M:%S") if j.created_at else "",
            j.type_evenement.value,
            source_map.get(j.source_id, "") if j.source_id else "",
            user_map.get(j.user_id, "") if j.user_id else "",
            j.message,
        ])

    return Response(
        buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=journaux.csv"},
    )
