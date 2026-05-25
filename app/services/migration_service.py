"""Migrations SQLite idempotentes pour les déploiements existants."""
from __future__ import annotations

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
            if table not in tables:
                continue
            existing = {col["name"] for col in inspector.get_columns(table)}
            for column, ddl in columns.items():
                if column in existing:
                    continue
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
                operations.append(f"{table}.{column}")

    return operations
