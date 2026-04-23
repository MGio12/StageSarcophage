"""
Connecteur SMB/CIFS pour l'accès aux partages réseau Windows.

Section 3.4 du CDC — protocole SMB/CIFS via smbprotocol/smbclient.
Chemin distant attendu : chemin UNC complet (\\\\serveur\\partage\\sous-dossier)
ou chemin relatif au partage (partage\\sous-dossier) combiné avec source.adresse.
"""
from __future__ import annotations

import fnmatch
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

import smbclient
from smbprotocol.exceptions import SMBException

logger = logging.getLogger(__name__)

TIMEOUT_SECONDES = 10


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


def _construire_chemin_unc(source) -> str:
    """Retourne le chemin UNC complet depuis les paramètres de la source."""
    chemin = source.chemin_distant or ""
    if chemin.startswith("\\\\") or chemin.startswith("//"):
        return chemin
    adresse = source.adresse or ""
    return f"\\\\{adresse}\\{chemin.lstrip('/\\')}"


def lister_fichiers(source) -> list[FichierDistant]:
    """Liste les fichiers correspondant au filtre de la source sur le partage SMB."""
    chemin_unc = _construire_chemin_unc(source)
    serveur = source.adresse or chemin_unc.lstrip("\\").split("\\")[0]
    port = source.port or 445
    filtre = source.filtre_fichiers or "*.pdf"
    fichiers: list[FichierDistant] = []

    try:
        smbclient.register_session(
            serveur,
            username=source.login,
            password=source.mot_de_passe,
            port=port,
        )
        for entry in smbclient.scandir(chemin_unc):
            if not entry.is_file():
                continue
            if not fnmatch.fnmatch(entry.name, filtre):
                continue
            stat = entry.stat()
            fichiers.append(
                FichierDistant(
                    nom=entry.name,
                    chemin=f"{chemin_unc}\\{entry.name}",
                    taille=stat.st_size,
                    date_modification=datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ),
                )
            )
    finally:
        try:
            smbclient.reset_connection_cache()
        except Exception:
            pass

    return fichiers


def tester_connexion(source) -> ResultatConnexion:
    """Vérifie l'accessibilité d'un partage SMB et retourne les fichiers trouvés."""
    chemin_unc = _construire_chemin_unc(source)
    try:
        fichiers = lister_fichiers(source)
        return ResultatConnexion(
            succes=True,
            message=f"Connexion réussie — {len(fichiers)} fichier(s) trouvé(s)",
            nb_fichiers=len(fichiers),
            fichiers=fichiers,
        )
    except SMBException as exc:
        logger.warning("SMB : échec connexion à %s — %s", chemin_unc, exc)
        return ResultatConnexion(succes=False, message=str(exc))
    except Exception as exc:
        logger.exception("SMB : erreur inattendue pour %s", chemin_unc)
        return ResultatConnexion(succes=False, message=str(exc))
