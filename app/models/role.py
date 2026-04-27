"""
Modèle de rôles pour la gestion des permissions.

Section 8.2 du CDC — Phase 2 : gestion des rôles.
"""
from datetime import datetime, timezone

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False, unique=True)
    permissions = db.Column(db.JSON, nullable=False, default=dict)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)

    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def has_permission(self, permission: str) -> bool:
        """Vérifie si le rôle possède une permission donnée."""
        if self.permissions.get("*"):
            return True
        return self.permissions.get(permission, False)

    def __repr__(self) -> str:
        return f"<Role id={self.id} nom={self.nom!r}>"


PERMISSIONS_DISPONIBLES = {
    "sources.view": "Voir les sources",
    "sources.edit": "Creer et modifier les sources",
    "sources.delete": "Supprimer les sources",
    "sources.sync": "Declencher la synchronisation",
    "documents.view": "Voir les documents",
    "documents.download": "Telecharger les documents",
    "journal.view": "Voir les journaux",
    "rapports.generer": "Generer les rapports",
    "admin.users": "Gerer les utilisateurs",
    "admin.roles": "Gerer les roles",
    "admin.tokens": "Gerer les tokens API",
    "admin.notifications": "Configurer les notifications",
    "admin.settings": "Modifier les parametres globaux",
}


ROLES_INITIAUX = {
    "admin": {
        "description": "Administrateur avec tous les droits",
        "permissions": {"*": True}
    },
    "operateur": {
        "description": "Operateur avec droits de modification",
        "permissions": {
            "sources.view": True,
            "sources.edit": True,
            "sources.sync": True,
            "documents.view": True,
            "documents.download": True,
            "journal.view": True,
            "rapports.generer": True
        }
    },
    "lecteur": {
        "description": "Consultation seule, sans modification",
        "permissions": {
            "sources.view": True,
            "documents.view": True,
            "documents.download": True,
            "journal.view": True
        }
    }
}


def init_roles():
    """Crée les rôles initiaux s'ils n'existent pas."""
    for nom, config in ROLES_INITIAUX.items():
        if not Role.query.filter_by(nom=nom).first():
            role = Role(
                nom=nom,
                description=config["description"],
                permissions=config["permissions"]
            )
            db.session.add(role)
    db.session.commit()
