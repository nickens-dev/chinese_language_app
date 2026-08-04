import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.core.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS deck_summaries (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    item_count INTEGER NOT NULL DEFAULT 0 CHECK (item_count >= 0),
    due_count INTEGER NOT NULL DEFAULT 0 CHECK (due_count >= 0),
    weak_count INTEGER NOT NULL DEFAULT 0 CHECK (weak_count >= 0),
    last_studied_at TEXT,
    accent TEXT NOT NULL DEFAULT 'jade' CHECK (accent IN ('jade', 'coral', 'gold', 'ink')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    archived_at TEXT
);
"""

DEMO_DECKS = (
    (
        "hsk-1-core",
        "HSK 1 Core",
        "Foundational words for everyday listening and reading.",
        148,
        18,
        12,
        "2026-07-31T09:30:00",
        "jade",
    ),
    (
        "food-restaurants",
        "Food & Restaurants",
        "Ordering, ingredients, meals, and useful restaurant phrases.",
        42,
        6,
        4,
        "2026-07-28T18:10:00",
        "coral",
    ),
    (
        "introductions",
        "Introductions",
        "Names, origins, occupations, and first conversations.",
        25,
        3,
        2,
        None,
        "gold",
    ),
)


def open_connection(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
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
    """Create the first local schema and clearly labeled demonstration decks."""
    with connect() as connection:
        connection.executescript(SCHEMA)
        count = connection.execute("SELECT COUNT(*) FROM deck_summaries").fetchone()[0]
        if count == 0:
            connection.executemany(
                """
                INSERT INTO deck_summaries (
                    id, name, description, item_count, due_count, weak_count,
                    last_studied_at, accent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                DEMO_DECKS,
            )
        connection.commit()
