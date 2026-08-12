from datetime import UTC, datetime
from sqlite3 import Connection, Row
from uuid import uuid4

from app.content.schemas import Card, CardCreate, CardUpdate
from app.persistence.database import connect
from app.study.scheduler import sync_deck_schedule_counts


class CardNotFoundError(LookupError):
    """Raised when a language-item ID does not identify an active card."""


class CardMembershipNotFoundError(LookupError):
    """Raised when an active card is not a member of the requested deck."""


CARD_COLUMNS = """
    items.id, items.item_type, items.simplified, items.traditional, items.pinyin,
    items.english, items.notes, items.source_name, items.source_entry_id,
    items.created_at, items.updated_at
"""


def _to_card(row: Row) -> Card:
    return Card.model_validate(dict(row))


def _assert_active_deck(connection: Connection, deck_id: str) -> None:
    row = connection.execute(
        "SELECT 1 FROM decks WHERE id = ? AND archived_at IS NULL", (deck_id,)
    ).fetchone()
    if row is None:
        raise CardMembershipNotFoundError(deck_id)


def _get_active_card(connection: Connection, card_id: str) -> Card:
    row = connection.execute(
        f"""
        SELECT {CARD_COLUMNS}
        FROM language_items AS items
        WHERE items.id = ? AND items.archived_at IS NULL
        """,
        (card_id,),
    ).fetchone()
    if row is None:
        raise CardNotFoundError(card_id)
    return _to_card(row)


def _sync_deck_count(connection: Connection, deck_id: str, now: str) -> None:
    connection.execute(
        """
        UPDATE decks
        SET item_count = (
            SELECT COUNT(*)
            FROM deck_memberships AS memberships
            JOIN language_items AS items ON items.id = memberships.item_id
            WHERE memberships.deck_id = decks.id AND items.archived_at IS NULL
        ), updated_at = ?
        WHERE id = ?
        """,
        (now, deck_id),
    )


def list_cards(deck_id: str) -> list[Card]:
    with connect() as connection:
        _assert_active_deck(connection, deck_id)
        rows = connection.execute(
            f"""
            SELECT {CARD_COLUMNS}
            FROM deck_memberships AS memberships
            JOIN language_items AS items ON items.id = memberships.item_id
            WHERE memberships.deck_id = ? AND items.archived_at IS NULL
            ORDER BY memberships.position, memberships.added_at
            """,
            (deck_id,),
        ).fetchall()
    return [_to_card(row) for row in rows]


def create_card(deck_id: str, values: CardCreate) -> Card:
    now = datetime.now(UTC).isoformat()
    card_id = str(uuid4())
    with connect() as connection:
        _assert_active_deck(connection, deck_id)
        position = connection.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM deck_memberships WHERE deck_id = ?",
            (deck_id,),
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO language_items (
                id, item_type, simplified, traditional, pinyin, english, notes, source_name,
                source_entry_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card_id,
                values.item_type,
                values.simplified,
                values.traditional,
                values.pinyin,
                values.english,
                values.notes,
                values.source_name,
                values.source_entry_id,
                now,
                now,
            ),
        )
        connection.execute(
            """
            INSERT INTO deck_memberships (deck_id, item_id, position, added_at)
            VALUES (?, ?, ?, ?)
            """,
            (deck_id, card_id, position, now),
        )
        _sync_deck_count(connection, deck_id, now)
        sync_deck_schedule_counts(connection)
        connection.commit()
        return _get_active_card(connection, card_id)


def update_card(card_id: str, values: CardUpdate) -> Card:
    changes = values.model_dump(exclude_unset=True)
    with connect() as connection:
        _get_active_card(connection, card_id)
        assignments = [f"{field} = ?" for field in changes]
        parameters = list(changes.values())
        assignments.append("updated_at = ?")
        parameters.append(datetime.now(UTC).isoformat())
        parameters.append(card_id)
        connection.execute(
            f"UPDATE language_items SET {', '.join(assignments)} WHERE id = ?",
            parameters,
        )
        connection.commit()
        return _get_active_card(connection, card_id)


def remove_card_from_deck(deck_id: str, card_id: str) -> None:
    now = datetime.now(UTC).isoformat()
    with connect() as connection:
        _assert_active_deck(connection, deck_id)
        _get_active_card(connection, card_id)
        result = connection.execute(
            "DELETE FROM deck_memberships WHERE deck_id = ? AND item_id = ?",
            (deck_id, card_id),
        )
        if result.rowcount == 0:
            raise CardMembershipNotFoundError(card_id)
        remaining = connection.execute(
            "SELECT 1 FROM deck_memberships WHERE item_id = ? LIMIT 1", (card_id,)
        ).fetchone()
        if remaining is None:
            connection.execute(
                "UPDATE language_items SET archived_at = ?, updated_at = ? WHERE id = ?",
                (now, now, card_id),
            )
        _sync_deck_count(connection, deck_id, now)
        sync_deck_schedule_counts(connection)
        connection.commit()
