"""
Connecteur SMB/CIFS pour l'accès aux partages réseau Windows.

Section 3.4 du CDC - protocole SMB/CIFS via smbprotocol/smbclient.
Chemin distant attendu : chemin UNC complet (\\\\serveur\\partage\\sous-dossier)
ou chemin relatif au partage (partage\\sous-dossier) combiné avec source.adresse.
"""
from __future__ import annotations

import fnmatch
import logging
import ntpath
import shutil
from datetime import datetime, timezone

import smbclient
from smbprotocol.exceptions import SMBException

from app.services.connectors.base import FichierDistant, ResultatConnexion

logger = logging.getLogger(__name__)

TIMEOUT_SECONDES = 10


def _nom_fichier_distant_sur(nom: str) -> bool:
    """Refuse les noms capables de sortir du dossier SMB configuré."""
    if not nom or nom in {".", ".."}:
        return False
    nom_normalise = nom.replace("/", "\\")
    return ntpath.basename(nom_normalise) == nom_normalise


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
            connection_timeout=TIMEOUT_SECONDES,
        )
        for entry in smbclient.scandir(chemin_unc):
            if not entry.is_file():
                continue
            if not _nom_fichier_distant_sur(entry.name):
                logger.warning(
                    "SMB : nom de fichier distant ignore pour %s : %r",
                    chemin_unc, entry.name
                )
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
        except Exception as exc:
            logger.debug("SMB : impossible de réinitialiser le cache de connexion : %s", exc)

    return fichiers


def telecharger_fichier(source, fichier_distant: FichierDistant, chemin_local: str) -> None:
    """Télécharge un fichier distant vers chemin_local via SMB."""
    serveur = source.adresse or _construire_chemin_unc(source).lstrip("\\").split("\\")[0]
    port = source.port or 445
    try:
        smbclient.register_session(
            serveur,
            username=source.login,
            password=source.mot_de_passe,
            port=port,
            connection_timeout=TIMEOUT_SECONDES,
        )
        with smbclient.open_file(fichier_distant.chemin, mode="rb") as f_src:
            with open(chemin_local, "wb") as f_dst:
                shutil.copyfileobj(f_src, f_dst)
    finally:
        try:
            smbclient.reset_connection_cache()
        except Exception as exc:
            logger.debug("SMB : impossible de réinitialiser le cache de connexion : %s", exc)


def tester_connexion(source) -> ResultatConnexion:
    """Vérifie l'accessibilité d'un partage SMB et retourne les fichiers trouvés."""
    chemin_unc = _construire_chemin_unc(source)
    try:
        fichiers = lister_fichiers(source)
        return ResultatConnexion(
            succes=True,
            message=f"Connexion réussie - {len(fichiers)} fichier(s) trouvé(s)",
            nb_fichiers=len(fichiers),
            fichiers=fichiers,
        )
    except SMBException as exc:
        logger.warning("SMB : échec connexion à %s - %s", chemin_unc, exc)
        return ResultatConnexion(succes=False, message="Connexion SMB impossible.")
    except Exception as exc:
        logger.exception("SMB : erreur inattendue pour %s", chemin_unc)
        return ResultatConnexion(succes=False, message="Connexion SMB impossible.")
