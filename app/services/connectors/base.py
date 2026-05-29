"""Types communs des connecteurs de sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass
class FichierDistant:
    nom: str
    chemin: str
    taille: int
    date_modification: datetime


@dataclass
class ResultatConnexion:
    succes: bool
    message: str
    nb_fichiers: int = 0
    fichiers: list[FichierDistant] = field(default_factory=list)
    fingerprint_nouveau: str | None = None
    fingerprint_key_type: str | None = None


class SourceConnector(Protocol):
    def lister_fichiers(self, source) -> list[FichierDistant]:
        ...

    def telecharger_fichier(self, source, fichier_distant: FichierDistant, chemin_local: str) -> None:
        ...
