"""
Service de purge automatique et de contrôle de fraîcheur des documents.

Section 2.4 du CDC : suppression des fichiers expirés, journalisation.
Section 2.3 du CDC : mise à jour des statuts ok/avertissement/critique.
"""
from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

from flask import current_app

from app.extensions import db
from app.models.document import Document, StatutDocument
from app.models.journal import Journal, TypeEvenement

logger = logging.getLogger(__name__)

_CORBEILLE = "_corbeille"


@dataclass
class ResultatPurge:
    source_id: int
    fichiers_purges: int = 0
    erreurs: int = 0
    messages_erreurs: list[str] = field(default_factory=list)


def mettre_a_jour_statuts(source) -> None:
    """Met à jour les statuts ok/avertissement/critique selon l'âge des documents."""
    maintenant = datetime.now(timezone.utc)
    docs = Document.query.filter(
        Document.source_id == source.id,
        Document.statut != StatutDocument.PURGE,
        Document.date_modification_source.isnot(None),
    ).all()

    for doc in docs:
        mtime = doc.date_modification_source
        if mtime.tzinfo is None:
            mtime = mtime.replace(tzinfo=timezone.utc)
        age_jours = (maintenant - mtime).days

        if age_jours >= source.seuil_critique_jours:
            nouveau = StatutDocument.CRITIQUE
        elif age_jours >= source.seuil_avertissement_jours:
            nouveau = StatutDocument.AVERTISSEMENT
        else:
            nouveau = StatutDocument.OK

        if doc.statut != nouveau:
            doc.statut = nouveau

    db.session.commit()


def purger_source(source) -> ResultatPurge:
    """Déplace vers la corbeille les documents dont l'âge dépasse retention_jours."""
    result = ResultatPurge(source_id=source.id)
    seuil = datetime.now(timezone.utc) - timedelta(days=source.retention_jours)

    docs_expires = Document.query.filter(
        Document.source_id == source.id,
        Document.statut != StatutDocument.PURGE,
        Document.date_collecte.isnot(None),
        Document.date_collecte < seuil,
    ).all()

    dossier_corbeille = os.path.join(
        current_app.config["STORAGE_DIR"], _CORBEILLE, str(source.id)
    )

    for doc in docs_expires:
        try:
            _purger_document(doc, dossier_corbeille)
            result.fichiers_purges += 1
        except Exception as exc:
            msg = f"{doc.nom_fichier} : {exc}"
            logger.error("Purge source %d, %s : %s", source.id, doc.nom_fichier, exc)
            result.erreurs += 1
            result.messages_erreurs.append(msg)

    if result.fichiers_purges > 0 or result.erreurs > 0:
        _journaliser_purge(source, result)

    return result


def _purger_document(doc: Document, dossier_corbeille: str) -> None:
    chemin_origine = doc.chemin_local
    dest = None

    if os.path.exists(chemin_origine):
        os.makedirs(dossier_corbeille, exist_ok=True)
        dest = os.path.join(dossier_corbeille, doc.nom_fichier)
        if os.path.exists(dest):
            base, ext = os.path.splitext(doc.nom_fichier)
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            dest = os.path.join(dossier_corbeille, f"{base}_{ts}{ext}")
        shutil.move(chemin_origine, dest)

    doc.statut = StatutDocument.PURGE
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        if dest and os.path.exists(dest):
            shutil.move(dest, chemin_origine)
        raise


def _journaliser_purge(source, result: ResultatPurge) -> None:
    type_evt = TypeEvenement.ERREUR if result.erreurs > 0 else TypeEvenement.PURGE
    msg = (
        f"Purge '{source.nom}' : "
        f"{result.fichiers_purges} purgé(s), "
        f"{result.erreurs} erreur(s)"
    )
    entree = Journal(source_id=source.id, type_evenement=type_evt, message=msg)
    entree.details = {
        "fichiers_purges": result.fichiers_purges,
        "erreurs": result.erreurs,
        "messages_erreurs": result.messages_erreurs[:10],
    }
    db.session.add(entree)
    db.session.commit()
