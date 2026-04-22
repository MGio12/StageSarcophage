import enum
from datetime import datetime, timezone
from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class StatutDocument(enum.Enum):
    OK = "ok"
    AVERTISSEMENT = "avertissement"
    CRITIQUE = "critique"
    PURGE = "purge"


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(
        db.Integer, db.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    nom_fichier = db.Column(db.String(255), nullable=False)
    chemin_local = db.Column(db.Text, nullable=False)
    hash_sha256 = db.Column(db.String(64), nullable=True)
    taille_octets = db.Column(db.Integer, nullable=True)
    date_modification_source = db.Column(db.DateTime(timezone=True), nullable=True)
    date_collecte = db.Column(db.DateTime(timezone=True), nullable=True)
    statut = db.Column(
        db.Enum(StatutDocument), nullable=False, default=StatutDocument.OK
    )

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    source = db.relationship("Source", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document id={self.id} fichier={self.nom_fichier!r} statut={self.statut.value}>"
