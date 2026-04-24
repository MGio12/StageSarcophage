"""
Connecteur SFTP pour l'accès aux serveurs Linux via SSH.

Section 3.4 du CDC — protocole SFTP via paramiko.
Chemin distant attendu : chemin Unix absolu (ex : /home/partage/modes-degrades).
"""
from __future__ import annotations

import fnmatch
import hashlib
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
    fingerprint_nouveau: str | None = None
    fingerprint_key_type: str | None = None


class HostKeyMismatchError(Exception):
    """Levée quand le fingerprint du serveur ne correspond pas à celui enregistré."""

    def __init__(self, expected: str, received: str):
        self.expected = expected
        self.received = received
        super().__init__(f"Fingerprint mismatch: expected {expected}, got {received}")


class HostKeyNewError(Exception):
    """Levée quand le serveur présente une clé inconnue (premier contact)."""

    def __init__(self, fingerprint: str, key_type: str):
        self.fingerprint = fingerprint
        self.key_type = key_type
        super().__init__(f"Unknown host key: {key_type} {fingerprint}")


def _calculer_fingerprint(key: paramiko.PKey) -> str:
    """Calcule le fingerprint SHA256 d'une clé publique SSH."""
    key_bytes = key.asbytes()
    digest = hashlib.sha256(key_bytes).hexdigest()
    return digest


def _get_stored_fingerprint(source_id: int, hostname: str, port: int) -> tuple[str, str] | None:
    """Récupère le fingerprint stocké en BDD pour une source."""
    from flask import current_app
    from app.models.ssh_fingerprint import SSHFingerprint

    if not current_app:
        return None

    fp = SSHFingerprint.query.filter_by(
        source_id=source_id,
        hostname=hostname,
        port=port,
    ).first()

    if fp:
        return (fp.fingerprint, fp.key_type)
    return None


def _save_fingerprint(source_id: int, hostname: str, port: int, fingerprint: str, key_type: str) -> None:
    """Enregistre un nouveau fingerprint en BDD."""
    from app.extensions import db
    from app.models.ssh_fingerprint import SSHFingerprint

    existing = SSHFingerprint.query.filter_by(
        source_id=source_id,
        hostname=hostname,
        port=port,
    ).first()

    if existing:
        existing.fingerprint = fingerprint
        existing.key_type = key_type
    else:
        fp = SSHFingerprint(
            source_id=source_id,
            hostname=hostname,
            port=port,
            fingerprint=fingerprint,
            key_type=key_type,
        )
        db.session.add(fp)

    db.session.commit()


class StrictHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    """Policy qui vérifie les fingerprints contre la BDD.

    - Si le fingerprint est connu et correspond : accepte
    - Si le fingerprint est connu mais différent : lève HostKeyMismatchError
    - Si le fingerprint est inconnu : lève HostKeyNewError (sauf si trust_new=True)
    """

    def __init__(self, source_id: int, trust_new: bool = False):
        self.source_id = source_id
        self.trust_new = trust_new
        self.new_fingerprint: str | None = None
        self.new_key_type: str | None = None

    def missing_host_key(self, client, hostname, key):
        port = client.get_transport().getpeername()[1] if client.get_transport() else 22
        fingerprint = _calculer_fingerprint(key)
        key_type = key.get_name()

        stored = _get_stored_fingerprint(self.source_id, hostname, port)

        if stored:
            stored_fp, stored_type = stored
            if stored_fp != fingerprint:
                logger.warning(
                    "SFTP host key mismatch for %s:%d - expected %s, got %s",
                    hostname, port, stored_fp[:16], fingerprint[:16]
                )
                raise HostKeyMismatchError(stored_fp, fingerprint)
            logger.debug("SFTP host key verified for %s:%d", hostname, port)
        else:
            self.new_fingerprint = fingerprint
            self.new_key_type = key_type
            if not self.trust_new:
                logger.info(
                    "SFTP new host key for %s:%d - %s %s",
                    hostname, port, key_type, fingerprint[:16]
                )
                raise HostKeyNewError(fingerprint, key_type)
            logger.info(
                "SFTP trusting new host key for %s:%d - %s",
                hostname, port, key_type
            )


def lister_fichiers(source, trust_new_key: bool = False) -> list[FichierDistant]:
    """Liste les fichiers correspondant au filtre de la source via SFTP."""
    port = source.port or 22
    filtre = source.filtre_fichiers or "*.pdf"
    fichiers: list[FichierDistant] = []

    client = paramiko.SSHClient()
    source_id = getattr(source, 'id', None)

    if source_id:
        policy = StrictHostKeyPolicy(source_id, trust_new=trust_new_key)
        client.set_missing_host_key_policy(policy)
    else:
        client.set_missing_host_key_policy(paramiko.WarningPolicy())

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

        if source_id and isinstance(client.get_host_keys().get(source.adresse), type(None)):
            pol = client._policy
            if hasattr(pol, 'new_fingerprint') and pol.new_fingerprint and trust_new_key:
                _save_fingerprint(source_id, source.adresse, port, pol.new_fingerprint, pol.new_key_type)

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
    source_id = getattr(source, 'id', None)

    if source_id:
        policy = StrictHostKeyPolicy(source_id, trust_new=True)
        client.set_missing_host_key_policy(policy)
    else:
        client.set_missing_host_key_policy(paramiko.WarningPolicy())

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


def tester_connexion(source, trust_new_key: bool = False) -> ResultatConnexion:
    """Vérifie l'accessibilité d'un hôte SFTP et retourne les fichiers trouvés."""
    try:
        fichiers = lister_fichiers(source, trust_new_key=trust_new_key)
        return ResultatConnexion(
            succes=True,
            message=f"Connexion réussie — {len(fichiers)} fichier(s) trouvé(s)",
            nb_fichiers=len(fichiers),
            fichiers=fichiers,
        )
    except HostKeyNewError as exc:
        logger.info(
            "SFTP : nouvelle clé hôte pour %s — %s %s",
            source.adresse, exc.key_type, exc.fingerprint[:16]
        )
        return ResultatConnexion(
            succes=False,
            message=f"Nouvelle clé SSH détectée. Vérifiez le fingerprint et acceptez-le.",
            fingerprint_nouveau=exc.fingerprint,
            fingerprint_key_type=exc.key_type,
        )
    except HostKeyMismatchError as exc:
        logger.warning(
            "SFTP : fingerprint modifié pour %s — attendu %s, reçu %s",
            source.adresse, exc.expected[:16], exc.received[:16]
        )
        return ResultatConnexion(
            succes=False,
            message="ALERTE SÉCURITÉ : Le fingerprint SSH a changé ! Possible attaque man-in-the-middle.",
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


def accepter_fingerprint(source) -> bool:
    """Accepte et enregistre le fingerprint actuel du serveur."""
    port = source.port or 22
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

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
        transport = client.get_transport()
        if transport:
            key = transport.get_remote_server_key()
            fingerprint = _calculer_fingerprint(key)
            key_type = key.get_name()
            _save_fingerprint(source.id, source.adresse, port, fingerprint, key_type)
            logger.info(
                "SFTP fingerprint accepted for %s:%d - %s",
                source.adresse, port, key_type
            )
            return True
        return False
    except Exception as exc:
        logger.error("Failed to accept fingerprint for %s: %s", source.adresse, exc)
        return False
    finally:
        client.close()
