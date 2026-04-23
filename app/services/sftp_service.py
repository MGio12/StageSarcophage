"""
Connecteur SFTP pour l'accès aux serveurs Linux via SSH.

Section 3.4 du CDC — protocole SFTP via paramiko.
Chemin distant attendu : chemin Unix absolu (ex : /home/partage/modes-degrades).
"""
from __future__ import annotations

import fnmatch
import logging
import stat as stat_module
from dataclasses import dataclass, field
from datetime import datetime, timezone

import paramiko

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


def lister_fichiers(source) -> list[FichierDistant]:
    """Liste les fichiers correspondant au filtre de la source via SFTP."""
    port = source.port or 22
    filtre = source.filtre_fichiers or "*.pdf"
    fichiers: list[FichierDistant] = []

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=source.adresse,
            port=port,
            username=source.login,
            password=source.mot_de_passe,
            timeout=TIMEOUT_SECONDES,
            allow_agent=False,
            look_for_keys=False,
        )
        sftp = client.open_sftp()
        try:
            for attr in sftp.listdir_attr(source.chemin_distant):
                if not stat_module.S_ISREG(attr.st_mode):
                    continue
                if not fnmatch.fnmatch(attr.filename, filtre):
                    continue
                fichiers.append(
                    FichierDistant(
                        nom=attr.filename,
                        chemin=f"{source.chemin_distant.rstrip('/')}/{attr.filename}",
                        taille=attr.st_size,
                        date_modification=datetime.fromtimestamp(
                            attr.st_mtime, tz=timezone.utc
                        ),
                    )
                )
        finally:
            sftp.close()
    finally:
        client.close()

    return fichiers


def telecharger_fichier(source, fichier_distant: FichierDistant, chemin_local: str) -> None:
    """Télécharge un fichier distant vers chemin_local via SFTP."""
    port = source.port or 22
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=source.adresse,
            port=port,
            username=source.login,
            password=source.mot_de_passe,
            timeout=TIMEOUT_SECONDES,
            allow_agent=False,
            look_for_keys=False,
        )
        sftp = client.open_sftp()
        try:
            sftp.get(fichier_distant.chemin, chemin_local)
        finally:
            sftp.close()
    finally:
        client.close()


def tester_connexion(source) -> ResultatConnexion:
    """Vérifie l'accessibilité d'un hôte SFTP et retourne les fichiers trouvés."""
    try:
        fichiers = lister_fichiers(source)
        return ResultatConnexion(
            succes=True,
            message=f"Connexion réussie — {len(fichiers)} fichier(s) trouvé(s)",
            nb_fichiers=len(fichiers),
            fichiers=fichiers,
        )
    except paramiko.AuthenticationException as exc:
        logger.warning(
            "SFTP : authentification refusée pour %s@%s", source.login, source.adresse
        )
        return ResultatConnexion(
            succes=False, message=f"Authentification refusée : {exc}"
        )
    except paramiko.SSHException as exc:
        logger.warning("SFTP : erreur SSH pour %s — %s", source.adresse, exc)
        return ResultatConnexion(succes=False, message=str(exc))
    except OSError as exc:
        logger.warning("SFTP : hôte inaccessible %s — %s", source.adresse, exc)
        return ResultatConnexion(succes=False, message=str(exc))
    except Exception as exc:
        logger.exception("SFTP : erreur inattendue pour %s", source.adresse)
        return ResultatConnexion(succes=False, message=str(exc))
