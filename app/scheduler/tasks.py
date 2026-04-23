"""
Tâches planifiées APScheduler.

Un job par source active pour la synchronisation (fréquence configurable par source).
Un job global quotidien pour la mise à jour des statuts et la purge.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="Europe/Paris")


def demarrer_scheduler(app) -> None:
    """Charge les sources actives depuis la BD et démarre le scheduler."""
    if _scheduler.running:
        return

    with app.app_context():
        from app.models.source import Source

        try:
            sources = Source.query.filter_by(actif=True).all()
        except Exception:
            # BD non encore initialisée (premier démarrage avant flask init-db)
            logger.warning("Scheduler: table sources absente, aucun job de sync chargé")
            sources = []

        for source in sources:
            _ajouter_job_sync(source, app)

        _scheduler.add_job(
            func=_job_purge_global,
            trigger=CronTrigger(hour=2, minute=0),
            id="purge_globale",
            args=[app],
            replace_existing=True,
        )

    _scheduler.start()
    logger.info("Scheduler démarré — %d job(s)", len(_scheduler.get_jobs()))


def arreter_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)


def planifier_sync_source(source, app) -> None:
    """Ajoute ou remplace le job de sync d'une source (appelé après création/modification)."""
    if _scheduler.running:
        _ajouter_job_sync(source, app)


def supprimer_job_source(source_id: int) -> None:
    """Supprime le job de sync d'une source (appelé après suppression)."""
    job_id = f"sync_{source_id}"
    if _scheduler.running and _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)


def _ajouter_job_sync(source, app) -> None:
    _scheduler.add_job(
        func=_job_sync_source,
        trigger=IntervalTrigger(minutes=source.frequence_sync_minutes),
        id=f"sync_{source.id}",
        args=[source.id, app],
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=60,
    )


def _job_sync_source(source_id: int, app) -> None:
    with app.app_context():
        from app.extensions import db
        from app.models.source import Source
        from app.services.sync_service import synchroniser_source
        from app.services.purge_service import mettre_a_jour_statuts

        source = db.session.get(Source, source_id)
        if source and source.actif:
            try:
                synchroniser_source(source)
                mettre_a_jour_statuts(source)
            except Exception:
                logger.exception("Erreur sync source %d", source_id)


def _job_purge_global(app) -> None:
    with app.app_context():
        from app.models.source import Source
        from app.services.purge_service import purger_source, mettre_a_jour_statuts

        for source in Source.query.filter_by(actif=True).all():
            try:
                mettre_a_jour_statuts(source)
                purger_source(source)
            except Exception:
                logger.exception("Erreur purge source %d", source.id)
