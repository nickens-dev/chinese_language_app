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


def create_content(client: TestClient) -> tuple[str, str]:
    deck = client.post(
        "/api/decks", json={"name": "Core", "description": "", "accent": "jade"}
    ).json()
    card = client.post(
        f"/api/decks/{deck['id']}/cards",
        json={
            "itemType": "word", "simplified": "好", "pinyin": "hǎo",
            "english": "good",
        },
    ).json()
    return deck["id"], card["id"]


def complete_session(
    client: TestClient, deck_id: str, prompt: str, response: str, answer: str
) -> None:
    session = client.post(
        "/api/study/sessions",
        json={
            "deckIds": [deck_id], "requestedCount": 1,
            "promptChannel": prompt, "responseChannel": response,
        },
    ).json()
    client.post(
        f"/api/study/sessions/{session['id']}/attempts", json={"answer": answer}
    )
    client.post(f"/api/study/sessions/{session['id']}/advance")


def test_empty_progress_report(client: TestClient) -> None:
    report = client.get("/api/progress").json()
    assert report["overview"]["attempts"] == 0
    assert report["overview"]["accuracyPercent"] == 0
    assert report["trend"] == []
    assert report["cards"] == []


def test_progress_aggregates_and_filters_by_direction(client: TestClient) -> None:
    deck_id, _ = create_content(client)
    complete_session(client, deck_id, "characters", "english", "good")
    complete_session(client, deck_id, "english", "characters", "坏")

    response = client.get("/api/progress?days=30")
    assert response.status_code == 200, response.text
    report = response.json()
    assert report["overview"]["attempts"] == 2
    assert report["overview"]["completedSessions"] == 2
    assert report["overview"]["uniqueCards"] == 1
    assert report["overview"]["accuracyPercent"] == 50
    assert report["overview"]["studyDays"] == 1
    assert len(report["directions"]) == 2
    assert len(report["cards"]) == 2
    assert len(report["recentSessions"]) == 2

    filtered = client.get(
        "/api/progress",
        params={
            "days": 0, "deckId": deck_id,
            "promptChannel": "characters", "responseChannel": "english",
        },
    ).json()
    assert filtered["overview"]["attempts"] == 1
    assert filtered["overview"]["accuracyPercent"] == 100
    assert filtered["cards"][0]["promptChannel"] == "characters"
    assert filtered["recentSessions"][0]["deckNames"] == ["Core"]


def test_progress_rejects_unsupported_ranges(client: TestClient) -> None:
    assert client.get("/api/progress?days=14").status_code == 422