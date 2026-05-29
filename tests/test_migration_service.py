import pytest
from sqlalchemy import text

from app.services import migration_service


def test_schema_migration_rejects_unsafe_column_identifier(db, monkeypatch):
    monkeypatch.setattr(
        migration_service,
        "SQLITE_COLUMNS",
        {"sources": {"bad; DROP TABLE users;--": "TEXT"}},
    )

    with pytest.raises(ValueError, match="identifiant"):
        migration_service.run_schema_migrations()


def test_schema_migration_quotes_identifiers_and_remains_idempotent(db, monkeypatch):
    db.drop_all()
    with db.engine.begin() as conn:
        conn.execute(text("CREATE TABLE sources (id INTEGER PRIMARY KEY)"))
    monkeypatch.setattr(
        migration_service,
        "SQLITE_COLUMNS",
        {"sources": {"deleted_at": "DATETIME"}},
    )

    assert migration_service.run_schema_migrations() == ["sources.deleted_at"]
    assert migration_service.run_schema_migrations() == []
