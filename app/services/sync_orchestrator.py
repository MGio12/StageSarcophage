"""Orchestration des synchronisations/purges déclenchées hors requête."""
from __future__ import annotations

from app.extensions import db
from app.models.source import Source
from app.services.job_service import lancer_job


def synchroniser_source_job(source_id: int, user_id: int | None = None):
    return lancer_job(
        "source_sync",
        {"source_id": source_id},
        lambda: _executer_sync_source(source_id),
        user_id=user_id,
    )


def purger_source_job(source_id: int, user_id: int | None = None):
    return lancer_job(
        "source_purge",
        {"source_id": source_id},
        lambda: _executer_purge_source(source_id),
        user_id=user_id,
    )


def synchroniser_toutes_sources_job(user_id: int | None = None):
    return lancer_job(
        "sources_sync_all",
        {},
        _executer_sync_toutes_sources,
        user_id=user_id,
    )


def _executer_sync_source(source_id: int) -> dict:
    from app.services.purge_service import mettre_a_jour_statuts
    from app.services.sync_service import synchroniser_source

    source = db.session.get(Source, source_id)
    if not source or source.deleted_at:
        raise ValueError("Source introuvable")
    if not source.actif:
        raise ValueError("Source inactive")
    resultat = synchroniser_source(source)
    mettre_a_jour_statuts(source)
    return {
        "source_id": source_id,
        "fichiers_copies": resultat.fichiers_copies,
        "fichiers_ignores": resultat.fichiers_ignores,
        "erreurs": resultat.erreurs,
    }


def _executer_purge_source(source_id: int) -> dict:
    from app.services.purge_service import purger_source

    source = db.session.get(Source, source_id)
    if not source or source.deleted_at:
        raise ValueError("Source introuvable")
    resultat = purger_source(source)
    return {
        "source_id": source_id,
        "fichiers_purges": resultat.fichiers_purges,
        "erreurs": resultat.erreurs,
    }


def _executer_sync_toutes_sources() -> dict:
    sources = Source.query.filter(Source.actif == True, Source.deleted_at.is_(None)).all()
    total_copies = 0
    total_erreurs = 0
    for source in sources:
        try:
            resultat = _executer_sync_source(source.id)
            total_copies += resultat["fichiers_copies"]
            total_erreurs += resultat["erreurs"]
        except Exception:
            total_erreurs += 1
    return {"sources": len(sources), "fichiers_copies": total_copies, "erreurs": total_erreurs}
