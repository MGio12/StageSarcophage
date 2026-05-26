"""
Tâches planifiées APScheduler.

Un job par source active pour la synchronisation (fréquence configurable par source).
Un job global quotidien pour la mise à jour des statuts et la purge.
Un job pour l'envoi automatique des rapports de conformité.
Un job pour le nettoyage de la corbeille.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

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

        _scheduler.add_job(
            func=_job_nettoyage_corbeille,
            trigger=CronTrigger(hour=3, minute=0),
            id="nettoyage_corbeille",
            args=[app],
            replace_existing=True,
        )

        planifier_job_rapport(app)

        if app.config.get("LDAP_SYNC_GROUPS"):
            _scheduler.add_job(
                func=_job_sync_groupes_ldap,
                trigger=CronTrigger(hour=4, minute=0),
                id="sync_groupes_ldap",
                args=[app],
                replace_existing=True,
            )

    _scheduler.start()
    logger.info("Scheduler démarré - %d job(s)", len(_scheduler.get_jobs()))


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


def _job_nettoyage_corbeille(app) -> None:
    """Nettoie les fichiers en corbeille après la période de grâce."""
    with app.app_context():
        from app.services.purge_service import nettoyer_corbeille
        try:
            nb_supprimes = nettoyer_corbeille()
            if nb_supprimes > 0:
                logger.info("Corbeille nettoyee : %d fichier(s) supprime(s)", nb_supprimes)
        except Exception:
            logger.exception("Erreur nettoyage corbeille")


def _job_rapport_automatique(app) -> None:
    """Génère et envoie les rapports de conformité selon la planification."""
    with app.app_context():
        from app.models.setting import Setting
        from app.services.report_service import generer_et_envoyer_rapport

        if not Setting.get("rapport_auto_active", False):
            return

        frequence = Setting.get("rapport_auto_frequence", "weekly")
        jour_config = Setting.get("rapport_auto_jour", 1)
        maintenant = datetime.now(timezone.utc)

        doit_envoyer = False
        if frequence == "daily":
            doit_envoyer = True
        elif frequence == "weekly":
            if maintenant.weekday() == (jour_config - 1) % 7:
                doit_envoyer = True
        elif frequence == "monthly":
            if maintenant.day == jour_config:
                doit_envoyer = True

        if doit_envoyer:
            try:
                nb_envois = generer_et_envoyer_rapport()
                logger.info("Rapport automatique envoye a %d destinataire(s)", nb_envois)
            except Exception:
                logger.exception("Erreur envoi rapport automatique")


def planifier_job_rapport(app) -> None:
    """Configure le job d'envoi de rapports selon les paramètres."""
    with app.app_context():
        heure = 8
        try:
            from app.models.setting import Setting
            heure = Setting.get("rapport_auto_heure", 8) or 8
        except Exception:
            logger.warning("Scheduler: table settings absente, rapport planifie a 8h")

        _scheduler.add_job(
            func=_job_rapport_automatique,
            trigger=CronTrigger(hour=heure, minute=0),
            id="rapport_automatique",
            args=[app],
            replace_existing=True,
        )


def _job_sync_groupes_ldap(app) -> None:
    """Synchronise les groupes LDAP vers les rôles applicatifs."""
    with app.app_context():
        from app.services.ldap_service import synchroniser_groupes_utilisateurs
        try:
            stats = synchroniser_groupes_utilisateurs()
            if stats["synced"] > 0:
                logger.info("Sync LDAP : %d role(s) mis a jour", stats["synced"])
        except Exception:
            logger.exception("Erreur sync groupes LDAP")
