"""
Service de generation et envoi automatique des rapports.

Phase 2 — D3 : Planification rapports.
"""
import logging
from datetime import datetime, timezone

from app.models.notification_config import NotificationConfig
from app.services.export_service import generer_rapport_pdf
from app.services.email_service import envoyer_email_avec_piece_jointe

logger = logging.getLogger(__name__)


def generer_et_envoyer_rapport() -> int:
    """
    Genere un rapport PDF et l'envoie aux destinataires configures.

    Returns:
        Nombre d'emails envoyes
    """
    destinataires = NotificationConfig.query.filter_by(
        actif=True, notif_critiques=True
    ).all()

    if not destinataires:
        logger.debug("Pas de destinataires pour le rapport automatique")
        return 0

    try:
        pdf_content = generer_rapport_pdf()
    except Exception as e:
        logger.error("Erreur generation rapport PDF : %s", e)
        return 0

    maintenant = datetime.now(timezone.utc)
    date_str = maintenant.strftime("%Y-%m-%d")
    nom_fichier = f"rapport_conformite_{date_str}.pdf"

    sujet = f"[RAPPORT] Conformite documents — {date_str}"
    corps_html = f"""
    <html>
    <body>
        <h2>Rapport de conformite</h2>
        <p>Veuillez trouver ci-joint le rapport de conformite des documents
        genere le {maintenant.strftime('%d/%m/%Y a %H:%M')} UTC.</p>
        <p>Ce rapport contient la liste des documents par source avec leur statut actuel.</p>
        <hr>
        <p><em>Application Modes Degrades — CLCC</em></p>
    </body>
    </html>
    """

    envois = 0
    for config in destinataires:
        try:
            if envoyer_email_avec_piece_jointe(
                config.email, sujet, corps_html, pdf_content, nom_fichier, "application/pdf"
            ):
                envois += 1
        except Exception as e:
            logger.warning("Erreur envoi rapport a %s : %s", config.email, e)

    logger.info("Rapport envoye a %d destinataire(s)", envois)
    return envois
