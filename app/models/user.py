"""
Modèle utilisateur pour l'authentification.

Section 2.6 du CDC - authentification par mot de passe.
"""
from datetime import datetime, timezone
import secrets

import bcrypt
from flask_login import UserMixin

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    auth_provider = db.Column(db.String(20), nullable=False, default="local")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)

    role = db.relationship("Role", back_populates="users")

    def set_password(self, password: str) -> None:
        """Hache le mot de passe avec bcrypt."""
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def set_unusable_password(self) -> None:
        """Définit un mot de passe local aléatoire qui ne sera jamais communiqué."""
        self.set_password(secrets.token_urlsafe(48))

    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe contre le hash stocké."""
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def has_permission(self, permission: str) -> bool:
        """Vérifie si l'utilisateur possède une permission via son rôle."""
        if not self.role:
            return False
        return self.role.has_permission(permission)

    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur."""
        return self.role and self.role.nom == "admin"

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
