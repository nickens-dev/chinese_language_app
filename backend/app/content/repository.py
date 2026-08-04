from app.content.schemas import DeckSummary
from app.persistence.database import connect


def list_decks() -> list[DeckSummary]:
    """Read active deck summaries without exposing SQLite rows to the API."""
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, name, description, item_count, due_count, weak_count,
                   last_studied_at, accent
            FROM deck_summaries
            WHERE archived_at IS NULL
            ORDER BY created_at
            """
        ).fetchall()
    return [DeckSummary.model_validate(dict(row)) for row in rows]
