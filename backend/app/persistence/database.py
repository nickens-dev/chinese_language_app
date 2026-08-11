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
    accent TEXT NOT NULL DEFAULT 'jade' CHECK (accent IN ('jade', 'coral', 'gold', 'ink', 'sky', 'plum', 'rose', 'tangerine', 'moss', 'slate')),
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

CREATE TABLE IF NOT EXISTS study_sessions (
    id TEXT PRIMARY KEY,
    requested_count INTEGER NOT NULL CHECK (requested_count > 0),
    prompt_channel TEXT NOT NULL CHECK (prompt_channel IN ('characters', 'english', 'pinyin')),
    response_channel TEXT NOT NULL CHECK (response_channel IN ('characters', 'english', 'pinyin')),
    current_index INTEGER NOT NULL DEFAULT 0 CHECK (current_index >= 0),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed')),
    selection_policy TEXT NOT NULL DEFAULT 'deck-order-v1',
    created_at TEXT NOT NULL,
    completed_at TEXT
);
CREATE TABLE IF NOT EXISTS study_session_decks (
    session_id TEXT NOT NULL REFERENCES study_sessions(id),
    deck_id TEXT NOT NULL REFERENCES decks(id),
    PRIMARY KEY (session_id, deck_id)
);
CREATE TABLE IF NOT EXISTS study_prompts (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES study_sessions(id),
    item_id TEXT NOT NULL REFERENCES language_items(id),
    position INTEGER NOT NULL CHECK (position >= 0),
    simplified TEXT NOT NULL,
    traditional TEXT NOT NULL,
    pinyin TEXT NOT NULL,
    english TEXT NOT NULL,
    UNIQUE (session_id, position)
);
CREATE TABLE IF NOT EXISTS study_attempts (
    id TEXT PRIMARY KEY,
    prompt_id TEXT NOT NULL UNIQUE REFERENCES study_prompts(id),
    raw_answer TEXT NOT NULL,
    normalized_answer TEXT NOT NULL,
    score REAL NOT NULL CHECK (score >= 0 AND score <= 1),
    verdict TEXT NOT NULL CHECK (verdict IN ('correct', 'mostly_correct', 'incorrect')),
    final_verdict TEXT NOT NULL CHECK (final_verdict IN ('correct', 'mostly_correct', 'incorrect')),
    feedback TEXT NOT NULL,
    override_reason TEXT,
    overridden_at TEXT,
    evaluator_version TEXT NOT NULL DEFAULT 'typed-v1',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS study_prompts_session_position
ON study_prompts(session_id, position);

CREATE TABLE IF NOT EXISTS accepted_answers (
    id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL REFERENCES language_items(id),
    channel TEXT NOT NULL CHECK (channel IN ('characters', 'english', 'pinyin')),
    answer TEXT NOT NULL,
    normalized_answer TEXT NOT NULL,
    source_attempt_id TEXT REFERENCES study_attempts(id),
    created_at TEXT NOT NULL,
    UNIQUE (item_id, channel, normalized_answer)
);
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


def _migrate_deck_accents(connection: sqlite3.Connection) -> None:
    """Rebuild the early four-accent deck table without losing relationships."""
    table_sql = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'decks'"
    ).fetchone()[0]
    if "'slate'" in table_sql:
        return
    connection.executescript(
        """
        CREATE TABLE decks_with_current_accents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            item_count INTEGER NOT NULL DEFAULT 0 CHECK (item_count >= 0),
            due_count INTEGER NOT NULL DEFAULT 0 CHECK (due_count >= 0),
            weak_count INTEGER NOT NULL DEFAULT 0 CHECK (weak_count >= 0),
            last_studied_at TEXT,
            accent TEXT NOT NULL DEFAULT 'jade' CHECK (
                accent IN ('jade', 'coral', 'gold', 'ink', 'sky', 'plum',
                           'rose', 'tangerine', 'moss', 'slate')
            ),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        );
        INSERT INTO decks_with_current_accents SELECT * FROM decks;
        DROP TABLE decks;
        ALTER TABLE decks_with_current_accents RENAME TO decks;
        CREATE UNIQUE INDEX active_deck_name
        ON decks(name COLLATE NOCASE)
        WHERE archived_at IS NULL;
        """
    )

def initialize_database() -> None:
    """Create the current schema while preserving all existing deck data."""
    with connect() as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.executescript(SCHEMA)
        _migrate_deck_accents(connection)
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(language_items)")}
        if "traditional" not in columns:
            connection.execute("ALTER TABLE language_items ADD COLUMN traditional TEXT NOT NULL DEFAULT ''")
        if "source_name" not in columns:
            connection.execute("ALTER TABLE language_items ADD COLUMN source_name TEXT NOT NULL DEFAULT 'user'")
        if "source_entry_id" not in columns:
            connection.execute("ALTER TABLE language_items ADD COLUMN source_entry_id TEXT")
        attempt_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(study_attempts)")
        }
        if "final_verdict" not in attempt_columns:
            connection.execute("ALTER TABLE study_attempts ADD COLUMN final_verdict TEXT")
            connection.execute(
                "UPDATE study_attempts SET final_verdict = verdict WHERE final_verdict IS NULL"
            )
        if "override_reason" not in attempt_columns:
            connection.execute("ALTER TABLE study_attempts ADD COLUMN override_reason TEXT")
        if "overridden_at" not in attempt_columns:
            connection.execute("ALTER TABLE study_attempts ADD COLUMN overridden_at TEXT")
