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


def create_deck(client: TestClient, name: str = "Travel") -> dict[str, object]:
    response = client.post(
        "/api/decks", json={"name": name, "description": "", "accent": "jade"}
    )
    assert response.status_code == 201
    return response.json()


def test_create_update_and_remove_card(client: TestClient) -> None:
    deck = create_deck(client)
    created = client.post(
        f"/api/decks/{deck['id']}/cards",
        json={
            "itemType": "phrase",
            "simplified": "  多少钱？ ",
            "pinyin": " duōshao qián? ",
            "english": " How much does it cost? ",
            "notes": " Useful while shopping. ",
            "sourceName": "CC-CEDICT",
            "sourceEntryId": "entry-123",
        },
    )

    assert created.status_code == 201
    card = created.json()
    assert card["itemType"] == "phrase"
    assert card["simplified"] == "多少钱？"
    assert card["pinyin"] == "duōshao qián?"
    assert card["english"] == "How much does it cost?"
    assert card["sourceName"] == "CC-CEDICT"
    assert card["sourceEntryId"] == "entry-123"
    assert client.get(f"/api/decks/{deck['id']}").json()["itemCount"] == 1

    updated = client.patch(
        f"/api/cards/{card['id']}", json={"english": "How much is it?", "notes": ""}
    )
    assert updated.status_code == 200
    assert updated.json()["english"] == "How much is it?"

    removed = client.delete(f"/api/decks/{deck['id']}/cards/{card['id']}")
    assert removed.status_code == 204
    assert client.get(f"/api/decks/{deck['id']}/cards").json() == []
    assert client.get(f"/api/decks/{deck['id']}").json()["itemCount"] == 0
    assert client.patch(f"/api/cards/{card['id']}", json={"notes": "orphan"}).status_code == 404


def test_cards_are_listed_in_creation_order(client: TestClient) -> None:
    deck = create_deck(client)
    for simplified, english in (("你", "you"), ("好", "good")):
        response = client.post(
            f"/api/decks/{deck['id']}/cards",
            json={"itemType": "word", "simplified": simplified, "english": english},
        )
        assert response.status_code == 201

    cards = client.get(f"/api/decks/{deck['id']}/cards").json()
    assert [card["simplified"] for card in cards] == ["你", "好"]


def test_card_inputs_and_missing_resources_are_validated(client: TestClient) -> None:
    deck = create_deck(client)
    blank = client.post(
        f"/api/decks/{deck['id']}/cards",
        json={"itemType": "word", "simplified": " ", "english": "you"},
    )
    invalid_type = client.post(
        f"/api/decks/{deck['id']}/cards",
        json={"itemType": "paragraph", "simplified": "你好", "english": "hello"},
    )

    assert blank.status_code == 422
    assert invalid_type.status_code == 422
    assert client.get("/api/decks/missing/cards").status_code == 404
    assert client.patch("/api/cards/missing", json={"notes": "x"}).status_code == 404