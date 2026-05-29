"""Modèle des travaux de fond déclenchés par l'API ou l'interface."""
from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class BackgroundJob(db.Model):
    __tablename__ = "background_jobs"

    id = db.Column(db.Integer, primary_key=True)
    operation = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="queued")
    payload = db.Column(db.JSON, nullable=False, default=dict)
    result = db.Column(db.JSON, nullable=True)
    error = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    finished_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User", backref=db.backref("background_jobs", lazy="dynamic"))

    def status_url(self) -> str:
        return f"/api/v1/jobs/{self.id}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "operation": self.operation,
            "status": self.status,
            "status_url": self.status_url(),
            "payload": self.payload or {},
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
