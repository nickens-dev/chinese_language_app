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

def create_deck(client: TestClient, name: str = 'Travel') -> dict[str, object]:
    response = client.post('/api/decks', json={'name': name, 'description': '', 'accent': 'jade'})
    assert response.status_code == 201
    return response.json()


def add_card(client: TestClient, deck_id: str, simplified: str, pinyin: str, english: str, traditional: str = "") -> None:
    response = client.post(f"/api/decks/{deck_id}/cards", json={"itemType": "word", "simplified": simplified, "traditional": traditional, "pinyin": pinyin, "english": english})
    assert response.status_code == 201


def test_complete_study_session_persists_attempts(client: TestClient) -> None:
    deck = create_deck(client)
    add_card(client, deck["id"], "你好", "nǐ hǎo", "hello", "你好")
    add_card(client, deck["id"], "谢谢", "xièxie", "thanks", "謝謝")
    created = client.post("/api/study/sessions", json={"deckIds": [deck["id"]], "requestedCount": 1, "promptChannel": "characters", "responseChannel": "english"})
    assert created.status_code == 201
    session = created.json()
    assert session["actualCount"] == 1
    assert session["currentPrompt"]["promptText"] == "你好"
    assert "expectedAnswers" not in session["currentPrompt"]
    attempt = client.post(f"/api/study/sessions/{session['id']}/attempts", json={"answer": "Hello!"})
    assert attempt.status_code == 201
    assert attempt.json()["verdict"] == "correct"
    assert attempt.json()["expectedAnswers"] == ["hello"]
    assert client.post(f"/api/study/sessions/{session['id']}/attempts", json={"answer": "hello"}).status_code == 409
    completed = client.post(f"/api/study/sessions/{session['id']}/advance")
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["currentPrompt"] is None


def test_pinyin_tone_feedback_and_advance_guard(client: TestClient) -> None:
    deck = create_deck(client)
    add_card(client, deck["id"], "你好", "nǐ hǎo", "hello")
    session = client.post("/api/study/sessions", json={"deckIds": [deck["id"]], "requestedCount": 5, "promptChannel": "characters", "responseChannel": "pinyin"}).json()
    assert client.post(f"/api/study/sessions/{session['id']}/advance").status_code == 409
    result = client.post(f"/api/study/sessions/{session['id']}/attempts", json={"answer": "ni hao"}).json()
    assert result["verdict"] == "mostly_correct"


def test_session_validates_modes_and_available_content(client: TestClient) -> None:
    deck = create_deck(client)
    empty = client.post("/api/study/sessions", json={"deckIds": [deck["id"]], "requestedCount": 10, "promptChannel": "characters", "responseChannel": "english"})
    invalid = client.post("/api/study/sessions", json={"deckIds": [deck["id"]], "requestedCount": 10, "promptChannel": "english", "responseChannel": "pinyin"})
    assert empty.status_code == 409
    assert invalid.status_code == 422