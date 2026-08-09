from datetime import UTC, datetime
from sqlite3 import Connection, Row
from uuid import uuid4

from app.content.schemas import DeckCreate, DeckSummary, DeckUpdate
from app.persistence.database import connect


class DeckNotFoundError(LookupError):
    """Raised when a deck ID does not identify an active deck."""


class DeckNameConflictError(ValueError):
    """Raised when an active deck already uses a requested name."""


DECK_COLUMNS = """
    id, name, description, item_count, due_count, weak_count,
    last_studied_at, accent, created_at, updated_at
"""


def _to_summary(row: Row) -> DeckSummary:
    return DeckSummary.model_validate(dict(row))


def _get_active_deck(connection: Connection, deck_id: str) -> DeckSummary:
    row = connection.execute(
        f"SELECT {DECK_COLUMNS} FROM decks WHERE id = ? AND archived_at IS NULL",
        (deck_id,),
    ).fetchone()
    if row is None:
        raise DeckNotFoundError(deck_id)
    return _to_summary(row)


def _assert_name_available(
    connection: Connection, name: str, excluding_id: str | None = None
) -> None:
    query = "SELECT id FROM decks WHERE name = ? COLLATE NOCASE AND archived_at IS NULL"
    parameters: tuple[str, ...] = (name,)
    if excluding_id is not None:
        query += " AND id <> ?"
        parameters = (name, excluding_id)
    if connection.execute(query, parameters).fetchone() is not None:
        raise DeckNameConflictError(name)


def list_decks() -> list[DeckSummary]:
    """Read active deck summaries without exposing SQLite rows to the API."""
    with connect() as connection:
        rows = connection.execute(
            f"""
            SELECT {DECK_COLUMNS}
            FROM decks
            WHERE archived_at IS NULL
            ORDER BY created_at
            """
        ).fetchall()
    return [_to_summary(row) for row in rows]


def get_deck(deck_id: str) -> DeckSummary:
    with connect() as connection:
        return _get_active_deck(connection, deck_id)


def create_deck(values: DeckCreate) -> DeckSummary:
    now = datetime.now(UTC).isoformat()
    deck_id = str(uuid4())
    with connect() as connection:
        _assert_name_available(connection, values.name)
        connection.execute(
            """
            INSERT INTO decks (id, name, description, accent, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (deck_id, values.name, values.description, values.accent, now, now),
        )
        connection.commit()
        return _get_active_deck(connection, deck_id)


def update_deck(deck_id: str, values: DeckUpdate) -> DeckSummary:
    changes = values.model_dump(exclude_unset=True)
    with connect() as connection:
        _get_active_deck(connection, deck_id)
        if "name" in changes:
            _assert_name_available(connection, changes["name"], excluding_id=deck_id)
        assignments = [f"{field} = ?" for field in changes]
        parameters = list(changes.values())
        assignments.append("updated_at = ?")
        parameters.append(datetime.now(UTC).isoformat())
        parameters.append(deck_id)
        connection.execute(
            f"UPDATE decks SET {', '.join(assignments)} WHERE id = ?",
            parameters,
        )
        connection.commit()
        return _get_active_deck(connection, deck_id)


def archive_deck(deck_id: str) -> None:
    now = datetime.now(UTC).isoformat()
    with connect() as connection:
        _get_active_deck(connection, deck_id)
        connection.execute(
            "UPDATE decks SET archived_at = ?, updated_at = ? WHERE id = ?",
            (now, now, deck_id),
        )
        connection.commit()
