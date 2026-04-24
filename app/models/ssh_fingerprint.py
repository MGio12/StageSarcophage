"""
Modèle pour stocker les empreintes SSH des serveurs sources.

Permet une vérification stricte des host keys SFTP (RejectPolicy).
"""
from datetime import datetime, timezone

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class SSHFingerprint(db.Model):
    __tablename__ = "ssh_fingerprints"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(
        db.Integer, db.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    hostname = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False, default=22)
    key_type = db.Column(db.String(50), nullable=False)
    fingerprint = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)

    source = db.relationship("Source", backref="ssh_fingerprints")

    __table_args__ = (
        db.UniqueConstraint("source_id", "hostname", "port", name="uq_source_host_port"),
    )

    def __repr__(self) -> str:
        return f"<SSHFingerprint source_id={self.source_id} {self.key_type}>"
