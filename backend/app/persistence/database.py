import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.core.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS decks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    item_count INTEGER NOT NULL DEFAULT 0 CHECK (item_count >= 0),
    due_count INTEGER NOT NULL DEFAULT 0 CHECK (due_count >= 0),
    weak_count INTEGER NOT NULL DEFAULT 0 CHECK (weak_count >= 0),
    last_studied_at TEXT,
    accent TEXT NOT NULL DEFAULT 'jade' CHECK (accent IN ('jade', 'coral', 'gold', 'ink')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    archived_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS active_deck_name
ON decks(name COLLATE NOCASE)
WHERE archived_at IS NULL;

CREATE TABLE IF NOT EXISTS language_items (
    id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL CHECK (item_type IN ('word', 'phrase', 'sentence')),
    simplified TEXT NOT NULL,
    traditional TEXT NOT NULL DEFAULT '',
    pinyin TEXT NOT NULL DEFAULT '',
    english TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    source_name TEXT NOT NULL DEFAULT 'user',
    source_entry_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    archived_at TEXT
);

CREATE TABLE IF NOT EXISTS deck_memberships (
    deck_id TEXT NOT NULL REFERENCES decks(id),
    item_id TEXT NOT NULL REFERENCES language_items(id),
    position INTEGER NOT NULL CHECK (position >= 0),
    added_at TEXT NOT NULL,
    PRIMARY KEY (deck_id, item_id)
);
CREATE INDEX IF NOT EXISTS deck_memberships_position
ON deck_memberships(deck_id, position);
"""

def open_connection(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    connection = open_connection(settings.database_path)
    try:
        yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    """Create the current schema while preserving all existing deck data."""
    with connect() as connection:
        connection.executescript(SCHEMA)
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(language_items)")}
        if "traditional" not in columns:
            connection.execute("ALTER TABLE language_items ADD COLUMN traditional TEXT NOT NULL DEFAULT ''")
        if "source_name" not in columns:
            connection.execute("ALTER TABLE language_items ADD COLUMN source_name TEXT NOT NULL DEFAULT 'user'")
        if "source_entry_id" not in columns:
            connection.execute("ALTER TABLE language_items ADD COLUMN source_entry_id TEXT")
