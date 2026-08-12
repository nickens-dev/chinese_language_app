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


def test_initialization_repairs_null_final_verdicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "nullable-final-verdict.db"
    connection = open_connection(path)
    connection.execute(
        """CREATE TABLE study_attempts (
            id TEXT PRIMARY KEY, prompt_id TEXT NOT NULL UNIQUE,
            raw_answer TEXT NOT NULL, normalized_answer TEXT NOT NULL,
            score REAL NOT NULL, verdict TEXT NOT NULL, final_verdict TEXT,
            feedback TEXT NOT NULL, evaluator_version TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    connection.execute(
        """INSERT INTO study_attempts (
            id, prompt_id, raw_answer, normalized_answer, score, verdict,
            final_verdict, feedback, evaluator_version, created_at
        ) VALUES ('attempt-1', 'prompt-1', 'dragon', 'dragon', 1, 'correct',
                  NULL, 'Correct.', 'typed-v1', '2026-08-01T00:00:00+00:00')"""
    )
    connection.commit()
    connection.close()
    monkeypatch.setattr(database, "settings", Settings(database_path=path))

    database.initialize_database()

    connection = open_connection(path)
    verdict = connection.execute(
        "SELECT final_verdict FROM study_attempts WHERE id = 'attempt-1'"
    ).fetchone()[0]
    connection.close()
    assert verdict == "correct"

def test_initialization_migrates_early_deck_accent_constraint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "early-accents.db"
    connection = database.open_connection(path)
    connection.execute(
        """CREATE TABLE decks (
            id TEXT PRIMARY KEY, name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            item_count INTEGER NOT NULL DEFAULT 0 CHECK (item_count >= 0),
            due_count INTEGER NOT NULL DEFAULT 0 CHECK (due_count >= 0),
            weak_count INTEGER NOT NULL DEFAULT 0 CHECK (weak_count >= 0),
            last_studied_at TEXT,
            accent TEXT NOT NULL DEFAULT 'jade'
                CHECK (accent IN ('jade', 'coral', 'gold', 'ink')),
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL, archived_at TEXT
        )"""
    )
    connection.execute(
        """INSERT INTO decks (id, name, accent, created_at, updated_at)
        VALUES ('deck-1', 'Existing', 'coral', '2026-01-01', '2026-01-01')"""
    )
    connection.commit()
    connection.close()
    monkeypatch.setattr(database, "settings", Settings(database_path=path))

    database.initialize_database()

    connection = database.open_connection(path)
    connection.execute("UPDATE decks SET accent = 'plum' WHERE id = 'deck-1'")
    row = connection.execute("SELECT name, accent FROM decks WHERE id = 'deck-1'").fetchone()
    connection.close()
    assert dict(row) == {"name": "Existing", "accent": "plum"}
