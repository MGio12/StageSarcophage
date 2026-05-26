from datetime import datetime, timezone
from app.extensions import db
from app.utils.crypto import chiffrer, dechiffrer


def _utcnow():
    return datetime.now(timezone.utc)


class Source(db.Model):
    __tablename__ = "sources"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    # linux | windows
    type_serveur = db.Column(db.String(10), nullable=False)
    # smb | sftp | local
    protocole = db.Column(db.String(10), nullable=False)

    adresse = db.Column(db.String(255), nullable=True)
    port = db.Column(db.Integer, nullable=True)
    chemin_distant = db.Column(db.Text, nullable=False)

    # Colonnes physiques chiffrées - accédées via les propriétés .login / .mot_de_passe
    _login = db.Column("login", db.Text, nullable=True)
    _mot_de_passe = db.Column("mot_de_passe", db.Text, nullable=True)

    filtre_fichiers = db.Column(db.String(50), nullable=False, default="*.pdf")
    frequence_sync_minutes = db.Column(db.Integer, nullable=False, default=60)
    retention_jours = db.Column(db.Integer, nullable=False, default=90)
    seuil_avertissement_jours = db.Column(db.Integer, nullable=False, default=30)
    seuil_critique_jours = db.Column(db.Integer, nullable=False, default=60)
    actif = db.Column(db.Boolean, nullable=False, default=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    echecs_consecutifs = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    @property
    def est_supprimee(self) -> bool:
        return self.deleted_at is not None

    documents = db.relationship(
        "Document", back_populates="source", cascade="all, delete-orphan", lazy="dynamic"
    )
    journaux = db.relationship(
        "Journal", back_populates="source", cascade="all, delete-orphan", lazy="dynamic"
    )

    # --- Propriétés chiffrées ---

    @property
    def login(self) -> str:
        return dechiffrer(self._login) if self._login else ""

    @login.setter
    def login(self, valeur: str) -> None:
        self._login = chiffrer(valeur) if valeur else None

    @property
    def mot_de_passe(self) -> str:
        return dechiffrer(self._mot_de_passe) if self._mot_de_passe else ""

    @mot_de_passe.setter
    def mot_de_passe(self, valeur: str) -> None:
        self._mot_de_passe = chiffrer(valeur) if valeur else None

    def __repr__(self) -> str:
        return f"<Source id={self.id} nom={self.nom!r} protocole={self.protocole}>"
