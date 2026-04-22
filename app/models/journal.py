import enum
import json
from datetime import datetime, timezone
from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class TypeEvenement(enum.Enum):
    SYNC = "sync"
    PURGE = "purge"
    ERREUR = "erreur"
    CONNEXION = "connexion"
    ACCES = "acces"


class Journal(db.Model):
    __tablename__ = "journaux"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(
        db.Integer, db.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True
    )
    type_evenement = db.Column(db.Enum(TypeEvenement), nullable=False)
    message = db.Column(db.Text, nullable=False)
    # JSON sérialisé manuellement — les mots de passe ne doivent jamais figurer ici
    _details = db.Column("details", db.Text, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)

    source = db.relationship("Source", back_populates="journaux")

    @property
    def details(self) -> dict | None:
        if self._details is None:
            return None
        try:
            return json.loads(self._details)
        except (json.JSONDecodeError, TypeError):
            return None

    @details.setter
    def details(self, valeur: dict | None) -> None:
        self._details = json.dumps(valeur, ensure_ascii=False) if valeur is not None else None

    def __repr__(self) -> str:
        return (
            f"<Journal id={self.id} type={self.type_evenement.value} "
            f"source_id={self.source_id}>"
        )
