import sqlite3
from pathlib import Path

import pytest

from app.persistence.database import SCHEMA, open_connection


def test_schema_enforces_non_negative_item_counts(tmp_path: Path) -> None:
    connection = open_connection(tmp_path / "test.db")
    connection.executescript(SCHEMA)

    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        connection.execute(
            "INSERT INTO deck_summaries (id, name, item_count) VALUES (?, ?, ?)",
            ("invalid", "Invalid deck", -1),
        )

    connection.close()
