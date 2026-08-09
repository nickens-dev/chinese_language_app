from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.persistence import database


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(database, "settings", Settings(database_path=tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def test_create_update_and_archive_deck(client: TestClient) -> None:
    created = client.post(
        "/api/decks",
        json={
            "name": "  Travel Basics  ",
            "description": "  Trains, hotels, and directions.  ",
            "accent": "ink",
        },
    )

    assert created.status_code == 201
    deck = created.json()
    assert deck["name"] == "Travel Basics"
    assert deck["description"] == "Trains, hotels, and directions."
    assert deck["accent"] == "ink"
    assert deck["itemCount"] == 0

    updated = client.patch(
        f"/api/decks/{deck['id']}",
        json={"name": "Travel & Transit", "accent": "gold"},
    )

    assert updated.status_code == 200
    assert updated.json()["name"] == "Travel & Transit"
    assert updated.json()["accent"] == "gold"

    archived = client.delete(f"/api/decks/{deck['id']}")
    assert archived.status_code == 204
    assert client.get(f"/api/decks/{deck['id']}").status_code == 404
    assert all(item["id"] != deck["id"] for item in client.get("/api/decks").json())


def test_new_database_starts_with_an_empty_library(client: TestClient) -> None:
    assert client.get("/api/decks").json() == []


def test_active_deck_names_are_case_insensitively_unique(client: TestClient) -> None:
    first = client.post(
        "/api/decks",
        json={"name": "Travel", "description": "", "accent": "jade"},
    )
    response = client.post(
        "/api/decks",
        json={"name": "travel", "description": "", "accent": "jade"},
    )

    assert first.status_code == 201
    assert response.status_code == 409
    assert response.json()["detail"] == "An active deck already uses that name."


def test_deck_inputs_are_validated(client: TestClient) -> None:
    blank_name = client.post(
        "/api/decks",
        json={"name": "   ", "description": "", "accent": "jade"},
    )
    empty_update = client.patch("/api/decks/hsk-1-core", json={})

    assert blank_name.status_code == 422
    assert empty_update.status_code == 422
