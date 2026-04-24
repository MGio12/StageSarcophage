"""
Modèle utilisateur pour l'authentification.

Section 2.6 du CDC — authentification par mot de passe.
"""
from datetime import datetime, timezone

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
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)

    def set_password(self, password: str) -> None:
        """Hache le mot de passe avec bcrypt."""
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe contre le hash stocké."""
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
