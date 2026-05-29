"""Helpers de neutralisation pour sorties tableur et HTML."""
from __future__ import annotations

import html
import re


_FORMULA_PREFIXES = ("=", "+", "-", "@")
_INVALID_SHEET_CHARS = re.compile(r"[\[\]\:\*\?\/\\]")


def neutraliser_cellule_tableur(value):
    """Neutralise les valeurs interprétables comme formules par Excel/LibreOffice."""
    if not isinstance(value, str):
        return value
    if value and value.lstrip().startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def nom_feuille_excel(value: str) -> str:
    """Retourne un nom d'onglet XLSX valide et non interprétable comme formule."""
    cleaned = _INVALID_SHEET_CHARS.sub("_", value or "Source").strip("' \t\r\n")
    if not cleaned:
        cleaned = "Source"
    if cleaned.lstrip().startswith(_FORMULA_PREFIXES):
        cleaned = "_" + cleaned
    return cleaned[:31]


def echapper_html(value) -> str:
    """Échappe une valeur destinée à un fragment HTML."""
    return html.escape("" if value is None else str(value), quote=True)


def texte_entete_email(value: str) -> str:
    """Supprime les retours de ligne interdits dans les en-têtes email."""
    return " ".join(str(value).splitlines())
