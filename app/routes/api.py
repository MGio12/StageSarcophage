"""
API REST pour intégration avec d'autres outils internes.

Phase 2 - CDC §8.2 : API REST.
Préfixe : /api/v1
Authentification : Bearer token (header Authorization)
Documentation : /api/docs
"""
from functools import wraps
from datetime import datetime, timezone
import logging

from flask import Blueprint, jsonify, request, abort, send_file, render_template

from app.extensions import db
from app.models.api_token import APIToken
from app.models.source import Source
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement
from app.utils.files import chemin_dans_storage

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


def require_api_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Authorization header required"}), 401
        token = auth[7:]
        api_token = APIToken.verify(token)
        if not api_token:
            return jsonify({"error": "Invalid or expired token"}), 401
        if not api_token.user.is_active:
            return jsonify({"error": "User account is disabled"}), 403
        request.api_token = api_token
        request.api_user = api_token.user
        return f(*args, **kwargs)
    return decorated


def require_api_permissions(*permissions):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, "api_user", None)
            if not user:
                return jsonify({"error": "Authorization required"}), 401
            missing = [perm for perm in permissions if not user.has_permission(perm)]
            if missing:
                return jsonify({
                    "error": "Permission denied",
                    "missing_permissions": missing,
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


@api_bp.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@api_bp.route("/stats")
@require_api_token
@require_api_permissions("sources.view", "documents.view")
def stats():
    total_sources = Source.query.filter(Source.deleted_at.is_(None)).count()
    sources_actives = Source.query.filter(
        Source.actif == True, Source.deleted_at.is_(None)
    ).count()
    total_docs = Document.query.filter(Document.statut != StatutDocument.PURGE).count()
    docs_ok = Document.query.filter(Document.statut == StatutDocument.OK).count()
    docs_avertissement = Document.query.filter(
        Document.statut == StatutDocument.AVERTISSEMENT
    ).count()
    docs_critique = Document.query.filter(
        Document.statut == StatutDocument.CRITIQUE
    ).count()
    return jsonify({
        "sources": {
            "total": total_sources,
            "actives": sources_actives
        },
        "documents": {
            "total": total_docs,
            "ok": docs_ok,
            "avertissement": docs_avertissement,
            "critique": docs_critique
        }
    })


@api_bp.route("/sources")
@require_api_token
@require_api_permissions("sources.view")
def sources_list():
    sources = Source.query.filter(Source.deleted_at.is_(None)).order_by(Source.nom).all()
    return jsonify({
        "sources": [_source_to_dict(s) for s in sources]
    })


@api_bp.route("/sources/<int:source_id>")
@require_api_token
@require_api_permissions("sources.view")
def source_detail(source_id):
    source = Source.query.filter_by(id=source_id).first()
    if not source or source.deleted_at:
        return jsonify({"error": "Source not found"}), 404
    return jsonify(_source_to_dict(source, detail=True))


@api_bp.route("/sources/<int:source_id>/sync", methods=["POST"])
@require_api_token
@require_api_permissions("sources.sync")
def source_sync(source_id):
    source = Source.query.filter_by(id=source_id).first()
    if not source or source.deleted_at:
        return jsonify({"error": "Source not found"}), 404
    if not source.actif:
        return jsonify({"error": "Source is not active"}), 400
    try:
        from app.services.sync_service import synchroniser_source
        from app.services.purge_service import mettre_a_jour_statuts
        resultat = synchroniser_source(source)
        mettre_a_jour_statuts(source)
        return jsonify({
            "success": True,
            "fichiers_copies": resultat.fichiers_copies,
            "fichiers_ignores": resultat.fichiers_ignores,
            "erreurs": resultat.erreurs
        })
    except Exception as exc:
        logger.error(
            "Erreur synchronisation API source %s (%s)",
            source_id,
            type(exc).__name__,
        )
        return jsonify({"error": "Synchronization failed"}), 500


@api_bp.route("/sources/<int:source_id>/status")
@require_api_token
@require_api_permissions("sources.view")
def source_status(source_id):
    source = Source.query.filter_by(id=source_id).first()
    if not source or source.deleted_at:
        return jsonify({"error": "Source not found"}), 404
    derniere_sync = Journal.query.filter(
        Journal.source_id == source_id,
        Journal.type_evenement == TypeEvenement.SYNC
    ).order_by(Journal.created_at.desc()).first()
    nb_docs = Document.query.filter(
        Document.source_id == source_id,
        Document.statut != StatutDocument.PURGE
    ).count()
    return jsonify({
        "source_id": source.id,
        "nom": source.nom,
        "actif": source.actif,
        "derniere_sync": derniere_sync.created_at.isoformat() if derniere_sync else None,
        "nb_documents": nb_docs
    })


@api_bp.route("/documents")
@require_api_token
@require_api_permissions("documents.view")
def documents_list():
    page = request.args.get("page", 1, type=int)
    page = max(page, 1)
    per_page = request.args.get("per_page", 50, type=int)
    per_page = max(1, min(per_page, 100))
    source_id = request.args.get("source_id", type=int)
    statut = request.args.get("statut", "").strip()

    query = Document.query.filter(Document.statut != StatutDocument.PURGE)
    if source_id:
        query = query.filter(Document.source_id == source_id)
    if statut:
        try:
            query = query.filter(Document.statut == StatutDocument(statut))
        except ValueError:
            pass

    pagination = query.order_by(Document.nom_fichier).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "documents": [_document_to_dict(d) for d in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages
    })


@api_bp.route("/documents/<int:doc_id>")
@require_api_token
@require_api_permissions("documents.view")
def document_detail(doc_id):
    doc = db.session.get(Document, doc_id)
    if not doc or doc.statut == StatutDocument.PURGE:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(_document_to_dict(doc, detail=True))


@api_bp.route("/documents/<int:doc_id>/download")
@require_api_token
@require_api_permissions("documents.download")
def document_download(doc_id):
    import os
    doc = db.session.get(Document, doc_id)
    if not doc or doc.statut == StatutDocument.PURGE:
        return jsonify({"error": "Document not found"}), 404
    try:
        chemin = chemin_dans_storage(doc.chemin_local)
    except ValueError:
        abort(403)
    if not os.path.isfile(chemin):
        return jsonify({"error": "File not found on disk"}), 404
    entree = Journal(
        source_id=doc.source_id,
        user_id=request.api_user.id,
        type_evenement=TypeEvenement.ACCES,
        message=f"Telechargement API : {doc.nom_fichier}"
    )
    db.session.add(entree)
    db.session.commit()
    return send_file(
        chemin,
        as_attachment=True,
        download_name=doc.nom_fichier,
        mimetype="application/pdf"
    )


def _source_to_dict(source, detail=False):
    d = {
        "id": source.id,
        "nom": source.nom,
        "protocole": source.protocole,
        "actif": source.actif,
        "frequence_sync_minutes": source.frequence_sync_minutes
    }
    if detail:
        d.update({
            "description": source.description,
            "type_serveur": source.type_serveur,
            "adresse": source.adresse,
            "port": source.port,
            "chemin_distant": source.chemin_distant,
            "filtre_fichiers": source.filtre_fichiers,
            "retention_jours": source.retention_jours,
            "seuil_avertissement_jours": source.seuil_avertissement_jours,
            "seuil_critique_jours": source.seuil_critique_jours,
            "created_at": source.created_at.isoformat() if source.created_at else None
        })
    return d


def _document_to_dict(doc, detail=False):
    d = {
        "id": doc.id,
        "nom_fichier": doc.nom_fichier,
        "source_id": doc.source_id,
        "statut": doc.statut.value,
        "taille_octets": doc.taille_octets
    }
    if detail:
        d.update({
            "hash_sha256": doc.hash_sha256,
            "date_modification_source": doc.date_modification_source.isoformat() if doc.date_modification_source else None,
            "date_collecte": doc.date_collecte.isoformat() if doc.date_collecte else None,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        })
    return d


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Modes Degrades API",
        "description": "API REST pour l'integration avec les outils internes. Permet de gerer les sources, documents et acceder aux statistiques.",
        "version": "1.0.0",
        "contact": {"name": "CLCC", "email": "support@clcc.local"}
    },
    "servers": [{"url": "/api/v1", "description": "API v1"}],
    "security": [{"bearerAuth": []}],
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Token API genere depuis l'interface d'administration"
            }
        },
        "schemas": {
            "Source": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "nom": {"type": "string"},
                    "protocole": {"type": "string", "enum": ["sftp", "smb"]},
                    "actif": {"type": "boolean"},
                    "frequence_sync_minutes": {"type": "integer"}
                }
            },
            "Document": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "nom_fichier": {"type": "string"},
                    "source_id": {"type": "integer"},
                    "statut": {"type": "string", "enum": ["ok", "avertissement", "critique", "purge"]},
                    "taille_octets": {"type": "integer"}
                }
            },
            "Error": {
                "type": "object",
                "properties": {"error": {"type": "string"}}
            }
        }
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Etat de sante de l'API",
                "tags": ["Monitoring"],
                "security": [],
                "responses": {
                    "200": {
                        "description": "API fonctionnelle",
                        "content": {"application/json": {"schema": {"type": "object", "properties": {"status": {"type": "string"}, "timestamp": {"type": "string"}}}}}
                    }
                }
            }
        },
        "/stats": {
            "get": {
                "summary": "Statistiques globales",
                "tags": ["Monitoring"],
                "responses": {
                    "200": {
                        "description": "Statistiques",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/sources": {
            "get": {
                "summary": "Liste des sources",
                "tags": ["Sources"],
                "responses": {
                    "200": {
                        "description": "Liste des sources",
                        "content": {"application/json": {"schema": {"type": "object", "properties": {"sources": {"type": "array", "items": {"$ref": "#/components/schemas/Source"}}}}}}
                    }
                }
            }
        },
        "/sources/{id}": {
            "get": {
                "summary": "Detail d'une source",
                "tags": ["Sources"],
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {
                    "200": {"description": "Source trouvee", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Source"}}}},
                    "404": {"description": "Source non trouvee", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                }
            }
        },
        "/sources/{id}/sync": {
            "post": {
                "summary": "Declencher la synchronisation d'une source",
                "tags": ["Sources"],
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {
                    "200": {"description": "Synchronisation effectuee"},
                    "400": {"description": "Source inactive"},
                    "404": {"description": "Source non trouvee"}
                }
            }
        },
        "/sources/{id}/status": {
            "get": {
                "summary": "Etat d'une source",
                "tags": ["Sources"],
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Etat de la source"}, "404": {"description": "Source non trouvee"}}
            }
        },
        "/documents": {
            "get": {
                "summary": "Liste des documents (paginee)",
                "tags": ["Documents"],
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 50, "maximum": 100}},
                    {"name": "source_id", "in": "query", "schema": {"type": "integer"}},
                    {"name": "statut", "in": "query", "schema": {"type": "string", "enum": ["ok", "avertissement", "critique"]}}
                ],
                "responses": {"200": {"description": "Liste paginee de documents"}}
            }
        },
        "/documents/{id}": {
            "get": {
                "summary": "Detail d'un document",
                "tags": ["Documents"],
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Document trouve"}, "404": {"description": "Document non trouve"}}
            }
        },
        "/documents/{id}/download": {
            "get": {
                "summary": "Telecharger un document",
                "tags": ["Documents"],
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {
                    "200": {"description": "Fichier PDF", "content": {"application/pdf": {}}},
                    "404": {"description": "Document non trouve"}
                }
            }
        }
    }
}


@api_bp.route("/openapi.json")
def openapi_spec():
    return jsonify(OPENAPI_SPEC)


@api_bp.route("/docs")
def swagger_ui():
    return render_template("api/docs.html")
