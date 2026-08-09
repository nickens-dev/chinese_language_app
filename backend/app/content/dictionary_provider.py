import hashlib
import re
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files

from opencc import OpenCC
from pypinyin import Style, lazy_pinyin

_CJK_PATTERN = re.compile(r"[\u3400-\u9fff]")
_ENTRY_PATTERN = re.compile(
    r"^(?P<traditional>\S+) (?P<simplified>\S+) \[(?P<pinyin>[^]]+)] /(?P<definitions>.*)/$"
)
_SPLIT_QUERY = re.compile(r"\s+")
_TONE_VOWELS = {
    "a": "\u0101\u00e1\u01ce\u00e0",
    "e": "\u0113\u00e9\u011b\u00e8",
    "i": "\u012b\u00ed\u01d0\u00ec",
    "o": "\u014d\u00f3\u01d2\u00f2",
    "u": "\u016b\u00fa\u01d4\u00f9",
    "\u00fc": "\u01d6\u01d8\u01da\u01dc",
}
_NORMAL_VOWELS = {
    marked: ("v" if base == "ü" else base)
    for base, marks in _TONE_VOWELS.items()
    for marked in marks
}


@dataclass(frozen=True)
class DictionaryEntry:
    simplified: str
    traditional: str
    pinyin_numbered: str
    pinyin_normalized: str
    definitions: tuple[str, ...]
    definitions_normalized: tuple[str, ...]
    source_entry_id: str


@dataclass(frozen=True)
class DictionaryCandidate:
    simplified: str
    traditional: str
    pinyin: str
    definitions: tuple[str, ...]
    source_name: str
    source_entry_id: str | None


class CedictProvider:
    """UTF-8-safe search adapter over the CC-CEDICT data bundled by the lookup package."""

    source_name = "CC-CEDICT"

    def __init__(self, entries: tuple[DictionaryEntry, ...] | None = None) -> None:
        self._simplified_to_traditional = OpenCC("s2t")
        self._traditional_to_simplified = OpenCC("t2s")
        self.entries = entries if entries is not None else self._load_entries()

    @staticmethod
    def _load_entries() -> tuple[DictionaryEntry, ...]:
        resource = files("chinese_english_lookup").joinpath("cedict/cedict_1_0_ts_utf-8_mdbg.txt")
        entries: list[DictionaryEntry] = []
        with resource.open("r", encoding="utf-8") as dictionary_file:
            for line in dictionary_file:
                if line.startswith("#"):
                    continue
                match = _ENTRY_PATTERN.match(line.strip())
                if match is None:
                    continue
                numbered = match.group("pinyin").lower()
                definitions = tuple(match.group("definitions").split("/"))
                identity = "|".join(
                    (
                        match.group("traditional"),
                        match.group("simplified"),
                        numbered,
                        *definitions,
                    )
                )
                entries.append(
                    DictionaryEntry(
                        simplified=match.group("simplified"),
                        traditional=match.group("traditional"),
                        pinyin_numbered=numbered,
                        pinyin_normalized=CedictProvider._normalize_numbered_pinyin(numbered),
                        definitions=definitions,
                        definitions_normalized=tuple(
                            definition.lower() for definition in definitions
                        ),
                        source_entry_id=hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20],
                    )
                )
        return tuple(entries)

    @staticmethod
    def _tone_mark_syllable(value: str) -> str:
        match = re.search(r"([1-5])$", value)
        syllable = value[:-1] if match else value
        tone = int(match.group(1)) if match else 5
        syllable = syllable.replace("u:", "ü").replace("v", "ü")
        if tone == 5:
            return syllable
        lowered = syllable.lower()
        if "a" in lowered:
            index = lowered.index("a")
        elif "e" in lowered:
            index = lowered.index("e")
        elif "ou" in lowered:
            index = lowered.index("o")
        else:
            indexes = [
                index for index, character in enumerate(lowered) if character in _TONE_VOWELS
            ]
            if not indexes:
                return syllable
            index = indexes[-1]
        vowel = lowered[index]
        marked = _TONE_VOWELS[vowel][tone - 1]
        return syllable[:index] + marked + syllable[index + 1 :]

    @classmethod
    def _tone_mark_phrase(cls, value: str) -> str:
        return " ".join(cls._tone_mark_syllable(syllable) for syllable in value.split())

    @staticmethod
    def _normalize_numbered_pinyin(value: str) -> str:
        return re.sub(r"[1-5]", "", value.lower()).replace("u:", "v")

    @staticmethod
    def _normalize_pinyin(value: str) -> str:
        normalized = value.lower().replace("u:", "v").replace("ü", "v")
        for marked, base in _NORMAL_VOWELS.items():
            normalized = normalized.replace(marked, base)
        return re.sub(r"[1-5]", "", normalized)

    @staticmethod
    def _normalize_latin(value: str) -> str:
        return _SPLIT_QUERY.sub(" ", value.lower()).strip()

    def search(self, query: str, limit: int = 10) -> list[DictionaryCandidate]:
        query = query.strip()
        if not query:
            return []
        normalized_query = self._normalize_latin(query)
        normalized_pinyin_query = self._normalize_pinyin(query)
        contains_chinese = _CJK_PATTERN.search(query) is not None
        ranked: list[tuple[int, DictionaryEntry]] = []

        for entry in self.entries:
            score = self._score(
                entry, query, normalized_query, normalized_pinyin_query, contains_chinese
            )
            if score is not None:
                ranked.append((score, entry))

        ranked.sort(key=lambda match: (match[0], len(match[1].simplified), match[1].simplified))
        candidates = [self._candidate(entry) for _, entry in ranked[:limit]]
        if not candidates and contains_chinese:
            candidates.append(self._generated_candidate(query))
        return candidates

    @staticmethod
    def _starts_at_word(value: str, query: str) -> bool:
        return re.search(rf"(?<![a-z]){re.escape(query)}", value) is not None

    def _score(
        self,
        entry: DictionaryEntry,
        query: str,
        normalized_query: str,
        normalized_pinyin_query: str,
        contains_chinese: bool,
    ) -> int | None:
        if contains_chinese:
            if query in (entry.simplified, entry.traditional):
                return 0
            if entry.simplified.startswith(query) or entry.traditional.startswith(query):
                return 10
            if query in entry.simplified or query in entry.traditional:
                return 20
            return None

        pinyin = entry.pinyin_normalized
        definitions = entry.definitions_normalized
        if normalized_pinyin_query == pinyin:
            return 0
        if any(normalized_query == definition for definition in definitions):
            return 1
        if pinyin.startswith(normalized_pinyin_query):
            return 10
        if any(definition.startswith(normalized_query) for definition in definitions):
            return 11
        if normalized_pinyin_query in pinyin:
            return 20
        if any(self._starts_at_word(definition, normalized_query) for definition in definitions):
            return 21
        return None

    def _candidate(self, entry: DictionaryEntry) -> DictionaryCandidate:
        return DictionaryCandidate(
            simplified=entry.simplified,
            traditional=entry.traditional,
            pinyin=self._tone_mark_phrase(entry.pinyin_numbered),
            definitions=entry.definitions,
            source_name=self.source_name,
            source_entry_id=entry.source_entry_id,
        )

    def _generated_candidate(self, query: str) -> DictionaryCandidate:
        simplified = self._traditional_to_simplified.convert(query)
        traditional = self._simplified_to_traditional.convert(simplified)
        pronunciation = " ".join(
            lazy_pinyin(simplified, style=Style.TONE, neutral_tone_with_five=False)
        )
        return DictionaryCandidate(
            simplified=simplified,
            traditional=traditional,
            pinyin=pronunciation,
            definitions=(),
            source_name="OpenCC + pypinyin fallback",
            source_entry_id=None,
        )


@lru_cache(maxsize=1)
def get_dictionary_provider() -> CedictProvider:
    return CedictProvider()
