"""Migrations SQLite idempotentes pour les déploiements existants."""
from __future__ import annotations

import re

from sqlalchemy import inspect, text

from app.extensions import db


SQLITE_COLUMNS = {
    "users": {
        "auth_provider": "VARCHAR(20) NOT NULL DEFAULT 'local'",
    },
    "sources": {
        "deleted_at": "DATETIME",
        "echecs_consecutifs": "INTEGER NOT NULL DEFAULT 0",
    },
    "journaux": {
        "user_id": "INTEGER",
    },
}

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_DDL_RE = re.compile(r"^[A-Za-z0-9_(), ']+$")


def _quote_identifier(identifier: str) -> str:
    if not _IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"identifiant SQL invalide: {identifier!r}")
    return f'"{identifier}"'


def _validate_column_ddl(ddl: str) -> str:
    if not _DDL_RE.fullmatch(ddl) or "--" in ddl or "/*" in ddl or "*/" in ddl:
        raise ValueError(f"DDL de colonne invalide: {ddl!r}")
    return ddl


def run_schema_migrations() -> list[str]:
    """
    Crée les tables manquantes et ajoute les colonnes connues manquantes.

    L'application cible SQLite; pour un autre moteur, il faut passer à Alembic.
    """
    db.create_all()
    if db.engine.dialect.name != "sqlite":
        return ["db.create_all exécuté; migrations ALTER TABLE réservées à SQLite"]

    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    operations: list[str] = []

    with db.engine.begin() as conn:
        for table, columns in SQLITE_COLUMNS.items():
            quoted_table = _quote_identifier(table)
            if table not in tables:
                continue
            existing = {col["name"] for col in inspector.get_columns(table)}
            for column, ddl in columns.items():
                quoted_column = _quote_identifier(column)
                validated_ddl = _validate_column_ddl(ddl)
                if column in existing:
                    continue
                conn.execute(
                    text(
                        f"ALTER TABLE {quoted_table} "
                        f"ADD COLUMN {quoted_column} {validated_ddl}"
                    )
                )
                operations.append(f"{table}.{column}")

    return operations
