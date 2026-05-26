"""
Modele pour les parametres globaux de l'application.

Phase 2 - F1 : Page parametres globaux.
"""
from datetime import datetime, timezone

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class Setting(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    cle = db.Column(db.String(100), nullable=False, unique=True, index=True)
    valeur = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    type_valeur = db.Column(db.String(20), nullable=False, default="string")
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    @classmethod
    def get(cls, cle: str, default=None):
        """Recupere la valeur d'un parametre."""
        setting = cls.query.filter_by(cle=cle).first()
        if not setting or setting.valeur is None:
            return default
        if setting.type_valeur == "int":
            return int(setting.valeur)
        if setting.type_valeur == "bool":
            return setting.valeur.lower() in ("true", "1", "yes", "oui")
        return setting.valeur

    @classmethod
    def set(cls, cle: str, valeur, description: str = None, type_valeur: str = "string"):
        """Definit la valeur d'un parametre."""
        setting = cls.query.filter_by(cle=cle).first()
        if not setting:
            setting = cls(cle=cle, description=description, type_valeur=type_valeur)
            db.session.add(setting)
        setting.valeur = str(valeur) if valeur is not None else None
        if description:
            setting.description = description
        db.session.commit()
        return setting

    def __repr__(self) -> str:
        return f"<Setting {self.cle}={self.valeur!r}>"


SETTINGS_DEFAUT = {
    "fuseau_horaire": {
        "valeur": "Europe/Paris",
        "description": "Fuseau horaire pour l'affichage des dates",
        "type": "string"
    },
    "rapport_auto_active": {
        "valeur": "false",
        "description": "Activer l'envoi automatique des rapports",
        "type": "bool"
    },
    "rapport_auto_frequence": {
        "valeur": "weekly",
        "description": "Frequence des rapports (daily, weekly, monthly)",
        "type": "string"
    },
    "rapport_auto_jour": {
        "valeur": "1",
        "description": "Jour d'envoi (1=lundi pour weekly, 1-28 pour monthly)",
        "type": "int"
    },
    "rapport_auto_heure": {
        "valeur": "8",
        "description": "Heure d'envoi des rapports (0-23)",
        "type": "int"
    },
    "corbeille_retention_jours": {
        "valeur": "30",
        "description": "Jours de retention en corbeille avant suppression definitive",
        "type": "int"
    }
}


def init_settings():
    """Initialise les parametres par defaut s'ils n'existent pas."""
    for cle, config in SETTINGS_DEFAUT.items():
        if not Setting.query.filter_by(cle=cle).first():
            setting = Setting(
                cle=cle,
                valeur=config["valeur"],
                description=config["description"],
                type_valeur=config["type"]
            )
            db.session.add(setting)
    db.session.commit()
