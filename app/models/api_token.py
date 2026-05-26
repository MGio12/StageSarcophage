"""
Modèle pour les tokens d'authentification API.

Phase 2 - CDC §8.2 : API REST pour intégration.
"""
import secrets
from datetime import datetime, timezone

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class APIToken(db.Model):
    __tablename__ = "api_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token_hash = db.Column(db.String(128), nullable=False, unique=True)
    nom = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", backref=db.backref("api_tokens", lazy="dynamic"))

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token: str) -> str:
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def create(cls, user_id: int, nom: str, expires_at=None):
        token = cls.generate_token()
        api_token = cls(
            user_id=user_id,
            token_hash=cls.hash_token(token),
            nom=nom,
            expires_at=expires_at
        )
        return api_token, token

    @classmethod
    def verify(cls, token: str):
        token_hash = cls.hash_token(token)
        api_token = cls.query.filter_by(token_hash=token_hash, is_active=True).first()
        if not api_token:
            return None
        if api_token.expires_at and api_token.expires_at < datetime.now(timezone.utc):
            return None
        api_token.last_used_at = datetime.now(timezone.utc)
        db.session.commit()
        return api_token

    def __repr__(self) -> str:
        return f"<APIToken id={self.id} nom={self.nom!r} user_id={self.user_id}>"
