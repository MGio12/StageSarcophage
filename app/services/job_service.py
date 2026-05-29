"""Service d'exécution des travaux de fond."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Callable

from flask import current_app

from app.extensions import db
from app.models.background_job import BackgroundJob

logger = logging.getLogger(__name__)

_executors: dict[int, ThreadPoolExecutor] = {}


def _utcnow():
    return datetime.now(timezone.utc)


def _executor_for_app(app) -> ThreadPoolExecutor:
    key = id(app)
    executor = _executors.get(key)
    if executor is None:
        executor = ThreadPoolExecutor(max_workers=app.config.get("JOB_WORKERS", 2))
        _executors[key] = executor
    return executor


def creer_job(operation: str, payload: dict, user_id: int | None = None) -> BackgroundJob:
    job = BackgroundJob(operation=operation, payload=payload, user_id=user_id)
    db.session.add(job)
    db.session.commit()
    return job


def lancer_job(
    operation: str,
    payload: dict,
    runner: Callable[[], dict | None],
    user_id: int | None = None,
) -> BackgroundJob:
    """Crée un job et le lance en ligne ou en pool selon la configuration."""
    job = creer_job(operation=operation, payload=payload, user_id=user_id)
    app = current_app._get_current_object()
    if app.config.get("JOBS_RUN_INLINE"):
        _executer_job(app, job.id, runner)
        db.session.expire_all()
        return db.session.get(BackgroundJob, job.id)

    _executor_for_app(app).submit(_executer_job, app, job.id, runner)
    return job


def _executer_job(app, job_id: int, runner: Callable[[], dict | None]) -> None:
    with app.app_context():
        job = db.session.get(BackgroundJob, job_id)
        if not job:
            return
        job.status = "running"
        job.started_at = _utcnow()
        db.session.commit()
        try:
            result = runner() or {}
        except Exception:
            logger.exception("Job %s failed", job_id)
            job.status = "failed"
            job.error = "Erreur interne pendant le traitement du job."
        else:
            job.status = "succeeded"
            job.result = result
        finally:
            job.finished_at = _utcnow()
            db.session.commit()


def permissions_pour_operation(operation: str) -> tuple[str, ...]:
    mapping = {
        "source_sync": ("sources.sync",),
        "source_purge": ("sources.purge",),
        "sources_sync_all": ("sources.sync",),
    }
    return mapping.get(operation, ())
