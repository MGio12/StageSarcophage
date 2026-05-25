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
    documents_devenus_critiques = []
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
            if nouveau == StatutDocument.CRITIQUE:
                documents_devenus_critiques.append(doc)
            doc.statut = nouveau

    db.session.commit()

    if documents_devenus_critiques:
        try:
            from app.services.notification_service import notifier_documents_critiques
            notifier_documents_critiques(source, documents_devenus_critiques)
        except Exception:
            logger.exception("Erreur notification documents critiques source %d", source.id)


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


def nettoyer_corbeille() -> int:
    """
    Supprime definitivement les fichiers en corbeille dont la periode de grace est depassee.

    La periode de grace est configuree via le parametre 'corbeille_retention_jours'
    ou la variable d'environnement CORBEILLE_RETENTION_JOURS (defaut: 30 jours).

    Returns:
        Nombre de fichiers supprimes
    """
    from app.models.setting import Setting

    retention_jours = Setting.get("corbeille_retention_jours", None)
    if retention_jours is None:
        retention_jours = current_app.config.get("CORBEILLE_RETENTION_JOURS", 30)

    storage_dir = current_app.config["STORAGE_DIR"]
    corbeille_dir = os.path.join(storage_dir, _CORBEILLE)

    if not os.path.exists(corbeille_dir):
        return 0

    seuil = datetime.now(timezone.utc) - timedelta(days=retention_jours)
    nb_supprimes = 0

    for source_dir in os.listdir(corbeille_dir):
        source_path = os.path.join(corbeille_dir, source_dir)
        if not os.path.isdir(source_path):
            continue

        for fichier in os.listdir(source_path):
            chemin = os.path.join(source_path, fichier)
            if not os.path.isfile(chemin):
                continue

            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(chemin), tz=timezone.utc)
                if mtime < seuil:
                    os.remove(chemin)
                    nb_supprimes += 1
                    logger.info("Corbeille : fichier supprime definitivement : %s", chemin)
            except Exception as e:
                logger.warning("Erreur suppression fichier corbeille %s : %s", chemin, e)

        if os.path.isdir(source_path) and not os.listdir(source_path):
            try:
                os.rmdir(source_path)
            except Exception:
                pass

    if nb_supprimes > 0:
        entree = Journal(
            type_evenement=TypeEvenement.PURGE,
            message=f"Nettoyage corbeille : {nb_supprimes} fichier(s) supprime(s) definitivement"
        )
        db.session.add(entree)
        db.session.commit()

    return nb_supprimes


def lister_corbeille() -> list:
    """
    Liste les fichiers actuellement en corbeille.

    Returns:
        Liste de dict avec source_id, nom_fichier, date_suppression, taille
    """
    storage_dir = current_app.config["STORAGE_DIR"]
    corbeille_dir = os.path.join(storage_dir, _CORBEILLE)

    if not os.path.exists(corbeille_dir):
        return []

    fichiers = []
    for source_dir in os.listdir(corbeille_dir):
        source_path = os.path.join(corbeille_dir, source_dir)
        if not os.path.isdir(source_path):
            continue

        try:
            source_id = int(source_dir)
        except ValueError:
            continue

        for fichier in os.listdir(source_path):
            chemin = os.path.join(source_path, fichier)
            if not os.path.isfile(chemin):
                continue

            try:
                stat = os.stat(chemin)
                fichiers.append({
                    "source_id": source_id,
                    "nom_fichier": fichier,
                    "date_suppression": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                    "taille": stat.st_size
                })
            except Exception:
                pass

    return sorted(fichiers, key=lambda f: f["date_suppression"], reverse=True)


def restaurer_fichier_corbeille(source_id: int, nom_fichier: str) -> bool:
    """
    Restaure un fichier de la corbeille vers son emplacement d'origine.

    Args:
        source_id: ID de la source
        nom_fichier: Nom du fichier a restaurer

    Returns:
        True si la restauration a reussi
    """
    storage_dir = current_app.config["STORAGE_DIR"]
    corbeille_path = os.path.join(storage_dir, _CORBEILLE, str(source_id), nom_fichier)

    if not os.path.exists(corbeille_path):
        return False

    from app.models.source import Source
    source = db.session.get(Source, source_id)
    if not source:
        return False

    from app.services.sync_service import _slugify
    dossier_dest = os.path.join(storage_dir, f"{source.id}_{_slugify(source.nom)}")
    os.makedirs(dossier_dest, exist_ok=True)

    base_nom = nom_fichier
    if "_202" in nom_fichier and nom_fichier.endswith(".pdf"):
        parts = nom_fichier.rsplit("_", 2)
        if len(parts) >= 3:
            base_nom = parts[0] + ".pdf"

    chemin_dest = os.path.join(dossier_dest, base_nom)

    try:
        shutil.move(corbeille_path, chemin_dest)

        doc = Document.query.filter_by(source_id=source_id, nom_fichier=base_nom).first()
        if doc and doc.statut == StatutDocument.PURGE:
            doc.statut = StatutDocument.CRITIQUE
            doc.chemin_local = chemin_dest
            db.session.commit()

        logger.info("Fichier restaure : %s -> %s", corbeille_path, chemin_dest)
        return True

    except Exception as e:
        logger.error("Erreur restauration %s : %s", corbeille_path, e)
        return False
