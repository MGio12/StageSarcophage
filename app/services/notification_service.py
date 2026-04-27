"""
Service de notifications pour les alertes.

Phase 2 — CDC §8.2 : Notifications par email.
"""
import logging
from typing import List

from flask import current_app

from app.extensions import db
from app.models.notification_config import NotificationConfig
from app.models.document import Document, StatutDocument
from app.models.source import Source
from app.services.email_service import envoyer_email

logger = logging.getLogger(__name__)

SEUIL_ECHECS_NOTIFICATION = 3


def notifier_documents_critiques(source: Source, documents: List[Document]) -> int:
    """
    Envoie une notification groupée pour les documents passés en statut critique.

    Args:
        source: La source concernée
        documents: Liste des documents passés en critique

    Returns:
        Nombre d'emails envoyés
    """
    if not documents:
        return 0

    destinataires = NotificationConfig.query.filter_by(
        actif=True, notif_critiques=True
    ).all()

    if not destinataires:
        logger.debug("Pas de destinataires pour les notifications critiques")
        return 0

    sujet = f"[ALERTE] {len(documents)} document(s) critique(s) — {source.nom}"

    docs_list = "\n".join(
        f"<li>{doc.nom_fichier}</li>" for doc in documents[:20]
    )
    if len(documents) > 20:
        docs_list += f"<li><em>... et {len(documents) - 20} autre(s)</em></li>"

    corps_html = f"""
    <html>
    <body>
        <h2>Alerte documents critiques</h2>
        <p>Les documents suivants de la source <strong>{source.nom}</strong>
        ont atteint le seuil critique ({source.seuil_critique_jours} jours) :</p>
        <ul>{docs_list}</ul>
        <p>Ces documents n'ont pas été mis à jour depuis plus de {source.seuil_critique_jours} jours.</p>
        <hr>
        <p><em>Application Modes Dégradés — CLCC</em></p>
    </body>
    </html>
    """

    envois = 0
    for config in destinataires:
        if envoyer_email(config.email, sujet, corps_html):
            envois += 1

    logger.info("Notification critiques envoyée à %d destinataire(s) pour %s", envois, source.nom)
    return envois


def notifier_erreur_connexion(source: Source) -> int:
    """
    Envoie une notification d'erreur de connexion si le seuil est atteint.

    Args:
        source: La source en erreur

    Returns:
        Nombre d'emails envoyés
    """
    if source.echecs_consecutifs < SEUIL_ECHECS_NOTIFICATION:
        return 0

    destinataires = NotificationConfig.query.filter_by(
        actif=True, notif_erreurs=True
    ).all()

    if not destinataires:
        logger.debug("Pas de destinataires pour les notifications d'erreurs")
        return 0

    sujet = f"[ERREUR] Échec de connexion répété — {source.nom}"

    corps_html = f"""
    <html>
    <body>
        <h2>Erreur de connexion</h2>
        <p>La source <strong>{source.nom}</strong> a échoué {source.echecs_consecutifs} fois consécutives.</p>
        <p><strong>Détails de la source :</strong></p>
        <ul>
            <li>Protocole : {source.protocole}</li>
            <li>Adresse : {source.adresse or 'N/A'}</li>
            <li>Port : {source.port or 'N/A'}</li>
        </ul>
        <p>Veuillez vérifier la configuration et la connectivité.</p>
        <hr>
        <p><em>Application Modes Dégradés — CLCC</em></p>
    </body>
    </html>
    """

    envois = 0
    for config in destinataires:
        if envoyer_email(config.email, sujet, corps_html):
            envois += 1

    logger.info("Notification erreur envoyée à %d destinataire(s) pour %s", envois, source.nom)
    return envois


def enregistrer_succes_sync(source: Source) -> None:
    """Réinitialise le compteur d'échecs après une synchronisation réussie."""
    if source.echecs_consecutifs > 0:
        source.echecs_consecutifs = 0
        db.session.commit()


def enregistrer_echec_sync(source: Source) -> None:
    """Incrémente le compteur d'échecs et envoie une notification si seuil atteint."""
    source.echecs_consecutifs += 1
    db.session.commit()
    if source.echecs_consecutifs == SEUIL_ECHECS_NOTIFICATION:
        notifier_erreur_connexion(source)
