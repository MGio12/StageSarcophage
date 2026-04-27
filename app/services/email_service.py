"""
Service d'envoi d'emails pour les notifications.

Phase 2 — CDC §8.2 : Notifications par email.
"""
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dataclasses import dataclass
from typing import Optional

from flask import current_app

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    host: str
    port: int
    user: str
    password: str
    from_addr: str
    use_tls: bool = True


def get_email_config() -> Optional[EmailConfig]:
    host = current_app.config.get("SMTP_HOST")
    if not host:
        return None
    return EmailConfig(
        host=host,
        port=int(current_app.config.get("SMTP_PORT", 587)),
        user=current_app.config.get("SMTP_USER", ""),
        password=current_app.config.get("SMTP_PASSWORD", ""),
        from_addr=current_app.config.get("SMTP_FROM", "noreply@example.com"),
        use_tls=current_app.config.get("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    )


def envoyer_email(destinataire: str, sujet: str, corps_html: str, corps_texte: str = None) -> bool:
    """
    Envoie un email.

    Args:
        destinataire: Adresse email du destinataire
        sujet: Sujet de l'email
        corps_html: Corps de l'email en HTML
        corps_texte: Corps de l'email en texte brut (optionnel)

    Returns:
        True si l'envoi a réussi, False sinon
    """
    config = get_email_config()
    if not config:
        logger.warning("Configuration SMTP non définie, email non envoyé")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = config.from_addr
    msg["To"] = destinataire

    if corps_texte:
        msg.attach(MIMEText(corps_texte, "plain", "utf-8"))
    msg.attach(MIMEText(corps_html, "html", "utf-8"))

    try:
        if config.use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(config.host, config.port, timeout=30) as server:
                server.starttls(context=context)
                if config.user and config.password:
                    server.login(config.user, config.password)
                server.sendmail(config.from_addr, destinataire, msg.as_string())
        else:
            with smtplib.SMTP(config.host, config.port, timeout=30) as server:
                if config.user and config.password:
                    server.login(config.user, config.password)
                server.sendmail(config.from_addr, destinataire, msg.as_string())

        logger.info("Email envoyé à %s : %s", destinataire, sujet)
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error("Erreur d'authentification SMTP : %s", e)
        return False
    except smtplib.SMTPException as e:
        logger.error("Erreur SMTP lors de l'envoi à %s : %s", destinataire, e)
        return False
    except Exception as e:
        logger.exception("Erreur inattendue lors de l'envoi d'email : %s", e)
        return False


def envoyer_email_test(destinataire: str) -> bool:
    """Envoie un email de test pour vérifier la configuration SMTP."""
    sujet = "[Test] Configuration SMTP — Modes Dégradés"
    corps_html = """
    <html>
    <body>
        <h2>Test de configuration SMTP</h2>
        <p>Cet email confirme que la configuration SMTP est fonctionnelle.</p>
        <p><em>Application Modes Dégradés — CLCC</em></p>
    </body>
    </html>
    """
    corps_texte = "Test de configuration SMTP\n\nCet email confirme que la configuration SMTP est fonctionnelle."
    return envoyer_email(destinataire, sujet, corps_html, corps_texte)


def envoyer_email_avec_piece_jointe(
    destinataire: str,
    sujet: str,
    corps_html: str,
    piece_jointe: bytes,
    nom_fichier: str,
    type_mime: str = "application/octet-stream"
) -> bool:
    """
    Envoie un email avec une piece jointe.

    Args:
        destinataire: Adresse email du destinataire
        sujet: Sujet de l'email
        corps_html: Corps de l'email en HTML
        piece_jointe: Contenu binaire de la piece jointe
        nom_fichier: Nom du fichier joint
        type_mime: Type MIME de la piece jointe

    Returns:
        True si l'envoi a reussi, False sinon
    """
    config = get_email_config()
    if not config:
        logger.warning("Configuration SMTP non definie, email non envoye")
        return False

    msg = MIMEMultipart("mixed")
    msg["Subject"] = sujet
    msg["From"] = config.from_addr
    msg["To"] = destinataire

    corps_part = MIMEMultipart("alternative")
    corps_part.attach(MIMEText(corps_html, "html", "utf-8"))
    msg.attach(corps_part)

    maintype, subtype = type_mime.split("/", 1) if "/" in type_mime else ("application", "octet-stream")
    part = MIMEBase(maintype, subtype)
    part.set_payload(piece_jointe)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={nom_fichier}")
    msg.attach(part)

    try:
        if config.use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(config.host, config.port, timeout=30) as server:
                server.starttls(context=context)
                if config.user and config.password:
                    server.login(config.user, config.password)
                server.sendmail(config.from_addr, destinataire, msg.as_string())
        else:
            with smtplib.SMTP(config.host, config.port, timeout=30) as server:
                if config.user and config.password:
                    server.login(config.user, config.password)
                server.sendmail(config.from_addr, destinataire, msg.as_string())

        logger.info("Email avec piece jointe envoye a %s : %s", destinataire, sujet)
        return True

    except smtplib.SMTPException as e:
        logger.error("Erreur SMTP lors de l'envoi a %s : %s", destinataire, e)
        return False
    except Exception as e:
        logger.exception("Erreur inattendue lors de l'envoi d'email : %s", e)
        return False
