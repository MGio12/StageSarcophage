"""Rotation contrôlée de la clé Fernet pour les identifiants de sources."""
from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.extensions import db
from app.models.source import Source


def _fernet_from_key(key: str, label: str) -> Fernet:
    try:
        raw = key.encode("ascii")
        return Fernet(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{label} n'est pas une clé Fernet valide") from exc


def _rotate_token(token: str | None, old_fernet: Fernet, new_fernet: Fernet) -> str | None:
    if not token:
        return token
    try:
        plaintext = old_fernet.decrypt(token.encode("ascii"))
    except (InvalidToken, UnicodeEncodeError) as exc:
        raise ValueError("Déchiffrement impossible avec OLD_ENCRYPTION_KEY") from exc
    return new_fernet.encrypt(plaintext).decode("ascii")


def rotate_source_credentials(old_key: str, new_key: str) -> int:
    """Ré-encrypte Source._login et Source._mot_de_passe dans une transaction."""
    old_fernet = _fernet_from_key(old_key, "OLD_ENCRYPTION_KEY")
    new_fernet = _fernet_from_key(new_key, "NEW_ENCRYPTION_KEY")

    updated_fields = 0
    try:
        for source in Source.query.all():
            rotated_login = _rotate_token(source._login, old_fernet, new_fernet)
            rotated_password = _rotate_token(source._mot_de_passe, old_fernet, new_fernet)
            if rotated_login != source._login:
                source._login = rotated_login
                updated_fields += 1
            if rotated_password != source._mot_de_passe:
                source._mot_de_passe = rotated_password
                updated_fields += 1
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return updated_fields
