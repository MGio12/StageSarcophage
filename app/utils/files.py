"""Helpers de validation des chemins de fichiers locaux."""
from __future__ import annotations

import os

from flask import current_app


def chemin_dans_storage(chemin_local: str, storage_dir: str | None = None) -> str:
    """
    Résout un chemin local et vérifie qu'il appartient strictement à STORAGE_DIR.

    Retourne le chemin réel à utiliser pour les opérations disque.
    """
    storage = os.path.realpath(storage_dir or current_app.config["STORAGE_DIR"])
    cible = os.path.realpath(chemin_local)
    if os.path.commonpath([storage, cible]) != storage:
        raise ValueError(f"Chemin hors stockage : {chemin_local!r}")
    return cible


def nom_archive_zip(nom_fichier: str) -> str:
    """Retourne un nom sûr à utiliser dans une archive ZIP."""
    nom = nom_fichier.replace("\x00", "").replace("\\", "/")
    nom = os.path.basename(nom)
    if not nom or nom in {".", ".."} or nom.startswith("."):
        raise ValueError(f"Nom de fichier ZIP invalide : {nom_fichier!r}")
    return nom
