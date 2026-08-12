from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.persistence import database
from app.study.scheduler import sync_deck_schedule_counts


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(database, "settings", Settings(database_path=tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def content(client: TestClient) -> tuple[str, str]:
    deck = client.post("/api/decks", json={"name":"Core", "description":"", "accent":"jade"}).json()
    card = client.post(f"/api/decks/{deck['id']}/cards", json={"itemType":"word", "simplified":"好", "pinyin":"hǎo", "english":"good"}).json()
    return deck["id"], card["id"]


def answer(client: TestClient, deck_id: str, value: str, policy: str = "balanced") -> dict:
    session = client.post("/api/study/sessions", json={"deckIds":[deck_id], "requestedCount":1, "promptChannel":"characters", "responseChannel":"english", "selectionPolicy":policy}).json()
    result = client.post(f"/api/study/sessions/{session['id']}/attempts", json={"answer":value}).json()
    client.post(f"/api/study/sessions/{session['id']}/advance")
    return {"session":session, "result":result}


def test_review_event_builds_directional_state_and_explains_selection(client: TestClient) -> None:
    deck_id, card_id = content(client)
    first = answer(client, deck_id, "good")
    assert first["session"]["currentPrompt"]["selectionBucket"] == "new"
    assert "New in this study direction" in first["session"]["currentPrompt"]["selectionReason"]
    with database.connect() as connection:
        event = connection.execute("SELECT rating FROM review_events").fetchone()
        state = connection.execute("SELECT * FROM card_skill_states WHERE item_id = ?", (card_id,)).fetchone()
    assert event["rating"] == "good"
    assert state["prompt_channel"] == "characters"
    assert state["response_channel"] == "english"
    assert state["scheduler_version"] == "transparent-v1"


def test_overdue_state_updates_deck_count_and_selection_reason(client: TestClient) -> None:
    deck_id, card_id = content(client)
    answer(client, deck_id, "good")
    with database.connect() as connection:
        connection.execute("UPDATE card_skill_states SET due_at = ? WHERE item_id = ?", ((datetime.now(UTC) - timedelta(days=2)).isoformat(), card_id))
        sync_deck_schedule_counts(connection)
        connection.commit()
    assert client.get(f"/api/decks/{deck_id}").json()["dueCount"] == 1
    session = client.post("/api/study/sessions", json={"deckIds":[deck_id], "requestedCount":1, "promptChannel":"characters", "responseChannel":"english"}).json()
    assert session["currentPrompt"]["selectionBucket"] == "due"
    assert "Overdue by 2 days" in session["currentPrompt"]["selectionReason"]


def test_weak_policy_and_override_replay_scheduler_history(client: TestClient) -> None:
    deck_id, card_id = content(client)
    answer(client, deck_id, "bad")
    second = answer(client, deck_id, "bad")
    assert client.get(f"/api/decks/{deck_id}").json()["weakCount"] == 1
    weak = client.post("/api/study/sessions", json={"deckIds":[deck_id], "requestedCount":30, "promptChannel":"characters", "responseChannel":"english", "selectionPolicy":"weak"})
    assert weak.status_code == 201
    assert weak.json()["currentPrompt"]["selectionBucket"] == "weak"
    assert "0% reviewed accuracy" in weak.json()["currentPrompt"]["selectionReason"]

    reviewed = client.post(f"/api/study/sessions/attempts/{second['result']['attemptId']}/review", json={"addToCard":False})
    assert reviewed.status_code == 200
    with database.connect() as connection:
        ratings = [row["rating"] for row in connection.execute("SELECT rating FROM review_events WHERE item_id = ? ORDER BY reviewed_at", (card_id,))]
        state = connection.execute("SELECT * FROM card_skill_states WHERE item_id = ?", (card_id,)).fetchone()
    assert ratings == ["again", "good"]
    assert state["review_count"] == 2
    assert state["scheduler_version"] == "transparent-v1"