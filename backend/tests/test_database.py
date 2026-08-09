import sqlite3
from pathlib import Path

import pytest

from app.core.config import Settings
from app.persistence import database
from app.persistence.database import SCHEMA, open_connection


def test_schema_enforces_non_negative_item_counts(tmp_path: Path) -> None:
    connection = open_connection(tmp_path / "test.db")
    connection.executescript(SCHEMA)

    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        connection.execute(
            """
            INSERT INTO decks (id, name, item_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("invalid", "Invalid deck", -1, "2026-08-06T00:00:00", "2026-08-06T00:00:00"),
        )

    connection.close()


def test_initialization_adds_traditional_form_to_early_card_table(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "early.db"
    connection = open_connection(path)
    connection.execute(
        """
        CREATE TABLE language_items (
            id TEXT PRIMARY KEY,
            item_type TEXT NOT NULL,
            simplified TEXT NOT NULL,
            pinyin TEXT NOT NULL DEFAULT '',
            english TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        )
        """
    )
    connection.close()
    monkeypatch.setattr(database, "settings", Settings(database_path=path))

    database.initialize_database()

    connection = open_connection(path)
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(language_items)")}
    connection.close()
    assert {"traditional", "source_name", "source_entry_id"} <= columns