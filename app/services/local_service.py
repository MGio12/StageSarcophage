"""Connecteur local avec allowlist de racines."""
from __future__ import annotations

import fnmatch
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.services.connectors.base import FichierDistant, ResultatConnexion
from app.utils.files import chemin_dans_racines_autorisees, nom_fichier_sur


def _dossier_source(source) -> Path:
    return Path(chemin_dans_racines_autorisees(source.chemin_distant))


def lister_fichiers(source) -> list[FichierDistant]:
    filtre = source.filtre_fichiers or "*.pdf"
    dossier = _dossier_source(source)
    fichiers: list[FichierDistant] = []
    for path in dossier.iterdir():
        chemin_reel = chemin_dans_racines_autorisees(str(path))
        path = Path(chemin_reel)
        if path.is_file() and fnmatch.fnmatch(path.name, filtre):
            nom = nom_fichier_sur(path.name)
            stat = path.stat()
            fichiers.append(
                FichierDistant(
                    nom=nom,
                    chemin=str(path),
                    taille=stat.st_size,
                    date_modification=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                )
            )
    return fichiers


def telecharger_fichier(source, fichier_distant: FichierDistant, chemin_local: str) -> None:
    chemin_source = chemin_dans_racines_autorisees(fichier_distant.chemin)
    shutil.copy2(chemin_source, chemin_local)


def tester_connexion(source) -> ResultatConnexion:
    try:
        fichiers = lister_fichiers(source)
        return ResultatConnexion(
            succes=True,
            message=f"Connexion locale réussie - {len(fichiers)} fichier(s) trouvé(s)",
            nb_fichiers=len(fichiers),
            fichiers=fichiers,
        )
    except ValueError:
        return ResultatConnexion(
            succes=False,
            message="Source locale hors racines autorisées.",
        )
    except OSError:
        return ResultatConnexion(
            succes=False,
            message="Source locale inaccessible.",
        )
