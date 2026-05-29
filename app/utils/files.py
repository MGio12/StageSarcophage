"""Helpers de validation des chemins de fichiers locaux."""
from __future__ import annotations

import os
import re
from pathlib import Path

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


def nom_fichier_sur(nom_fichier: str) -> str:
    """Retourne un nom de fichier sûr, sans composant de chemin."""
    nom = nom_fichier.replace("\x00", "").replace("\\", "/")
    nom = os.path.basename(nom)
    if not nom or nom in {".", ".."} or nom.startswith(".") or set(nom) == {"."}:
        raise ValueError(f"Nom de fichier invalide : {nom_fichier!r}")
    return nom


def nom_archive_zip(nom_fichier: str) -> str:
    """Retourne un nom sûr à utiliser dans une archive ZIP."""
    return nom_fichier_sur(nom_fichier)


def racines_sources_locales(raw_roots: str | list[str] | tuple[str, ...] | None = None) -> list[str]:
    """Parse et normalise LOCAL_SOURCE_ALLOWED_ROOTS."""
    if raw_roots is None:
        raw_roots = current_app.config.get("LOCAL_SOURCE_ALLOWED_ROOTS", "")
    if isinstance(raw_roots, str):
        pieces = re.split(r"[,;{}]+".format(re.escape(os.pathsep)), raw_roots)
    else:
        pieces = list(raw_roots)
    return [os.path.realpath(piece) for piece in pieces if str(piece).strip()]


def chemin_dans_racines_autorisees(chemin: str, roots: list[str] | None = None) -> str:
    """Résout un chemin et vérifie qu'il appartient à une racine locale autorisée."""
    cible = os.path.realpath(chemin)
    roots = roots if roots is not None else racines_sources_locales()
    if not roots:
        raise ValueError("Aucune racine autorisee pour les sources locales")
    for root in roots:
        try:
            if os.path.commonpath([root, cible]) == root:
                return cible
        except ValueError:
            continue
    raise ValueError(f"Chemin hors racines autorisees : {chemin!r}")


def fichier_enfant_sur(parent: str | Path, nom_fichier: str) -> str:
    """Construit un chemin enfant sûr sous parent."""
    parent_reel = os.path.realpath(str(parent))
    cible = os.path.realpath(os.path.join(parent_reel, nom_fichier_sur(nom_fichier)))
    if os.path.commonpath([parent_reel, cible]) != parent_reel:
        raise ValueError(f"Chemin enfant invalide : {nom_fichier!r}")
    return cible
