from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.routes import dictionary as dictionary_routes
from app.content.dictionary_provider import CedictProvider, DictionaryEntry
from app.core.config import Settings
from app.main import app
from app.persistence import database


@pytest.fixture
def provider() -> CedictProvider:
    entries = (
        DictionaryEntry(
            simplified="你好",
            traditional="你好",
            pinyin_numbered="ni3 hao3",
            pinyin_normalized="ni hao",
            definitions=("hello", "hi"),
            definitions_normalized=("hello", "hi"),
            source_entry_id="hello-entry",
        ),
        DictionaryEntry(
            simplified="银行",
            traditional="銀行",
            pinyin_numbered="yin2 hang2",
            pinyin_normalized="yin hang",
            definitions=("bank",),
            definitions_normalized=("bank",),
            source_entry_id="bank-entry",
        ),
    )
    return CedictProvider(entries=entries)


def test_dictionary_searches_english_characters_and_pinyin(provider: CedictProvider) -> None:
    english = provider.search("hello", 3)
    characters = provider.search("銀行", 3)
    numbered = provider.search("ni3 hao3", 3)
    marked = provider.search("nǐ hǎo", 3)

    assert english[0].simplified == "你好"
    assert english[0].pinyin == "nǐ hǎo"
    assert "hello" in english[0].definitions
    assert characters[0].simplified == "银行"
    assert numbered[0].simplified == "你好"
    assert marked[0].simplified == "你好"
    assert english[0].source_name == "CC-CEDICT"
    assert english[0].source_entry_id == "hello-entry"


def test_unknown_characters_use_conversion_and_pronunciation_fallback(
    provider: CedictProvider,
) -> None:
    candidate = provider.search("不存在詞", 3)[0]

    assert candidate.simplified == "不存在词"
    assert candidate.traditional == "不存在詞"
    assert candidate.pinyin
    assert candidate.definitions == ()
    assert candidate.source_name == "OpenCC + pypinyin fallback"
    assert candidate.source_entry_id is None



def test_dictionary_search_endpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    provider: CedictProvider,
) -> None:
    monkeypatch.setattr(database, "settings", Settings(database_path=tmp_path / "test.db"))
    monkeypatch.setattr(dictionary_routes, "get_dictionary_provider", lambda: provider)

    with TestClient(app) as client:
        response = client.get("/api/dictionary/search", params={"q": "hello", "limit": 1})

    assert response.status_code == 200
    assert response.json() == [
        {
            "simplified": "你好",
            "traditional": "你好",
            "pinyin": "nǐ hǎo",
            "definitions": ["hello", "hi"],
            "sourceName": "CC-CEDICT",
            "sourceEntryId": "hello-entry",
        }
    ]
@pytest.mark.parametrize(
    ("numbered", "marked"),
    (("ni3 hao3", "nǐ hǎo"), ("lv4", "lǜ"), ("liu2", "liú"), ("gui4", "guì")),
)
def test_numbered_pinyin_uses_standard_tone_placement(numbered: str, marked: str) -> None:
    assert CedictProvider._tone_mark_phrase(numbered) == marked