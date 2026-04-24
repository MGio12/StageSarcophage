"""
Service de synchronisation des documents depuis les sources distantes.

Section 2.2 du CDC : collecte périodique, déduplication SHA-256, journalisation.
"""
from __future__ import annotations

import fnmatch
import hashlib
import logging
import os
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement

logger = logging.getLogger(__name__)


@dataclass
class ResultatSync:
    source_id: int
    fichiers_copies: int = 0
    fichiers_ignores: int = 0
    erreurs: int = 0
    messages_erreurs: list[str] = field(default_factory=list)


def _slugify(texte: str) -> str:
    texte = re.sub(r"[^\w]", "_", texte.lower())
    return re.sub(r"_+", "_", texte).strip("_") or "source"


def _safe_filename(nom: str) -> str:
    """Nettoie un nom de fichier pour éviter les attaques path traversal."""
    # Supprime les caractères nuls
    nom = nom.replace("\x00", "")
    # Normalise les séparateurs Windows en /
    nom = nom.replace("\\", "/")
    # Extrait uniquement le nom de fichier (supprime tout chemin)
    nom = os.path.basename(nom)
    # Refuse les fichiers cachés ou vides
    if not nom or nom.startswith("."):
        raise ValueError(f"Nom de fichier invalide : {nom!r}")
    return nom


def _verifier_chemin_storage(chemin: str, storage_dir: str) -> None:
    """Vérifie que le chemin est bien dans le répertoire de stockage."""
    chemin_reel = os.path.realpath(chemin)
    storage_reel = os.path.realpath(storage_dir)
    if not chemin_reel.startswith(storage_reel + os.sep):
        raise ValueError(f"Tentative de path traversal détectée : {chemin!r}")


def _dossier_local_source(source) -> str:
    storage = current_app.config["STORAGE_DIR"]
    return os.path.join(storage, f"{source.id}_{_slugify(source.nom)}")


def _hash_fichier(chemin: str) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _get_connector(protocole: str):
    """Retourne (fn_lister, fn_telecharger) selon le protocole."""
    if protocole == "sftp":
        from app.services import sftp_service
        return sftp_service.lister_fichiers, sftp_service.telecharger_fichier
    if protocole == "smb":
        from app.services import smb_service
        return smb_service.lister_fichiers, smb_service.telecharger_fichier
    if protocole == "local":
        return _lister_local, _telecharger_local
    raise ValueError(f"Protocole non supporté : {protocole!r}")


def _lister_local(source):
    from app.services.sftp_service import FichierDistant
    filtre = source.filtre_fichiers or "*.pdf"
    fichiers = []
    for path in Path(source.chemin_distant).iterdir():
        if path.is_file() and fnmatch.fnmatch(path.name, filtre):
            stat = path.stat()
            fichiers.append(FichierDistant(
                nom=path.name,
                chemin=str(path),
                taille=stat.st_size,
                date_modification=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            ))
    return fichiers


def _telecharger_local(source, fichier_distant, chemin_local: str) -> None:
    shutil.copy2(fichier_distant.chemin, chemin_local)


def synchroniser_source(source) -> ResultatSync:
    """Synchronise tous les fichiers d'une source distante vers le stockage local."""
    result = ResultatSync(source_id=source.id)
    dossier_local = _dossier_local_source(source)
    os.makedirs(dossier_local, exist_ok=True)

    try:
        fn_lister, fn_telecharger = _get_connector(source.protocole)
        fichiers_distants = fn_lister(source)
    except Exception as exc:
        msg = f"Connexion impossible : {exc}"
        logger.error("Sync source %d : %s", source.id, msg)
        result.erreurs += 1
        result.messages_erreurs.append(msg)
        _journaliser_sync(source, result)
        return result

    for f_distant in fichiers_distants:
        try:
            action = _traiter_fichier(source, f_distant, dossier_local, fn_telecharger)
            if action == "copie":
                result.fichiers_copies += 1
            else:
                result.fichiers_ignores += 1
        except Exception as exc:
            msg = f"{f_distant.nom} : {exc}"
            logger.error("Sync source %d, fichier %s : %s", source.id, f_distant.nom, exc)
            result.erreurs += 1
            result.messages_erreurs.append(msg)

    _journaliser_sync(source, result)
    return result


def _traiter_fichier(source, f_distant, dossier_local: str, fn_telecharger) -> str:
    """Copie le fichier si nécessaire. Retourne 'copie' ou 'ignore'."""
    # Sanitize le nom de fichier pour éviter les path traversal
    nom_safe = _safe_filename(f_distant.nom)
    chemin_local = os.path.join(dossier_local, nom_safe)
    # Vérifie que le chemin final est bien dans le storage
    _verifier_chemin_storage(chemin_local, current_app.config["STORAGE_DIR"])

    doc: Document | None = Document.query.filter_by(
        source_id=source.id, nom_fichier=nom_safe
    ).first()

    # Optimisation : même date de modification + même taille → pas de téléchargement
    if doc and doc.taille_octets == f_distant.taille:
        doc_mtime = _as_utc(doc.date_modification_source)
        if doc_mtime and abs((doc_mtime - f_distant.date_modification).total_seconds()) < 2:
            return "ignore"

    # Téléchargement dans un fichier temporaire pour éviter les écritures partielles
    fd, chemin_tmp = tempfile.mkstemp(dir=dossier_local, prefix=f".tmp_{nom_safe}_")
    os.close(fd)
    try:
        fn_telecharger(source, f_distant, chemin_tmp)
        hash_nouveau = _hash_fichier(chemin_tmp)

        if doc and doc.hash_sha256 == hash_nouveau:
            os.unlink(chemin_tmp)
            return "ignore"

        shutil.move(chemin_tmp, chemin_local)
    except Exception:
        if os.path.exists(chemin_tmp):
            os.unlink(chemin_tmp)
        raise

    maintenant = datetime.now(timezone.utc)
    if doc is None:
        doc = Document(source_id=source.id, nom_fichier=nom_safe, chemin_local=chemin_local)
        db.session.add(doc)

    doc.chemin_local = chemin_local
    doc.hash_sha256 = hash_nouveau
    doc.taille_octets = f_distant.taille
    doc.date_modification_source = f_distant.date_modification
    doc.date_collecte = maintenant
    doc.statut = StatutDocument.OK
    db.session.commit()
    return "copie"


def _journaliser_sync(source, result: ResultatSync) -> None:
    type_evt = TypeEvenement.ERREUR if result.erreurs > 0 else TypeEvenement.SYNC
    msg = (
        f"Sync '{source.nom}' : "
        f"{result.fichiers_copies} copié(s), "
        f"{result.fichiers_ignores} ignoré(s), "
        f"{result.erreurs} erreur(s)"
    )
    entree = Journal(source_id=source.id, type_evenement=type_evt, message=msg)
    entree.details = {
        "fichiers_copies": result.fichiers_copies,
        "fichiers_ignores": result.fichiers_ignores,
        "erreurs": result.erreurs,
        "messages_erreurs": result.messages_erreurs[:10],
    }
    db.session.add(entree)
    db.session.commit()
