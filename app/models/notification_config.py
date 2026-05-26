"""
Modèle de configuration des notifications.

Phase 2 - CDC §8.2 : Notifications par email.
"""
from datetime import datetime, timezone

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class NotificationConfig(db.Model):
    __tablename__ = "notification_configs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    email = db.Column(db.String(255), nullable=False)
    notif_erreurs = db.Column(db.Boolean, nullable=False, default=True)
    notif_critiques = db.Column(db.Boolean, nullable=False, default=True)
    actif = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)

    user = db.relationship("User", backref=db.backref("notification_configs", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<NotificationConfig id={self.id} email={self.email!r}>"
