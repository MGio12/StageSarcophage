"""
Chiffrement symétrique des identifiants de connexion aux sources distantes.

Algorithme : Fernet (AES-128-CBC + HMAC-SHA256), équivalent sécuritaire à AES-256
conformément à la section 3.1 du CDC. La clé est chargée depuis ENCRYPTION_KEY
(variable d'environnement) via la config Flask - elle ne transite jamais en clair.

Générer une clé :
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


def _get_fernet() -> Fernet:
    key = current_app.config.get("ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY absente de la configuration. "
            "Définissez-la dans vos variables d'environnement."
        )
    raw = key.encode() if isinstance(key, str) else key
    return Fernet(raw)


def chiffrer(valeur: str) -> str:
    """Chiffre *valeur* et retourne la version encodée en base64 URL-safe."""
    if not valeur:
        return ""
    return _get_fernet().encrypt(valeur.encode("utf-8")).decode("ascii")


def dechiffrer(valeur_chiffree: str) -> str:
    """Déchiffre *valeur_chiffree* produite par :func:`chiffrer`."""
    if not valeur_chiffree:
        return ""
    try:
        return _get_fernet().decrypt(valeur_chiffree.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError(
            "Déchiffrement impossible : clé incorrecte ou données corrompues"
        ) from exc
