import re
import unicodedata
from difflib import SequenceMatcher

from app.study.schemas import StudyAttemptResult, StudyChannel

EVALUATOR_VERSION = "typed-v1"
PINYIN_MARKS = {
    "ā": "a1", "á": "a2", "ǎ": "a3", "à": "a4", "ē": "e1", "é": "e2", "ě": "e3", "è": "e4",
    "ī": "i1", "í": "i2", "ǐ": "i3", "ì": "i4", "ō": "o1", "ó": "o2", "ǒ": "o3", "ò": "o4",
    "ū": "u1", "ú": "u2", "ǔ": "u3", "ù": "u4", "ǖ": "v1", "ǘ": "v2", "ǚ": "v3", "ǜ": "v4", "ü": "v",
}


def _plain(value: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", value.casefold()).split())


def _pinyin(value: str, keep_tones: bool = True) -> str:
    syllables: list[str] = []
    normalized_value = value.casefold().replace("u:", "v")
    for token in re.findall(r"[^\W\d_]+[1-5]?", normalized_value):
        tone, letters = "", ""
        for character in token:
            if character in PINYIN_MARKS:
                replacement = PINYIN_MARKS[character]
                letters += replacement[0]
                tone = replacement[1:] or tone
            elif character.isdigit():
                tone = character
            elif character != ":":
                letters += "v" if character == "ü" else character
        syllables.append(letters + tone if keep_tones else letters)
    return " ".join(syllables)


def _english_answers(value: str) -> list[str]:
    answers = [part.strip() for part in re.split(r"[;/]", value) if part.strip()]
    return answers or [value]


def evaluate(
    answer: str,
    channel: StudyChannel,
    snapshot: dict[str, str],
    accepted_answers: list[str] | None = None,
) -> StudyAttemptResult:
    if channel == "characters":
        expected = [snapshot["simplified"]]
        if snapshot["traditional"] and snapshot["traditional"] not in expected:
            expected.append(snapshot["traditional"])
        normalized = re.sub(r"\s+", "", answer)
        score = max(SequenceMatcher(None, normalized, re.sub(r"\s+", "", item)).ratio() for item in expected)
    elif channel == "pinyin":
        expected = [snapshot["pinyin"]]
        normalized, target = _pinyin(answer), _pinyin(expected[0])
        score = SequenceMatcher(None, normalized, target).ratio()
        if normalized != target and _pinyin(answer, False) == _pinyin(expected[0], False):
            score = max(score, 0.8)
    else:
        expected = _english_answers(snapshot["english"])
        normalized = _plain(answer)
        score = max(SequenceMatcher(None, normalized, _plain(item)).ratio() for item in expected)

    for accepted in accepted_answers or []:
        if accepted not in expected:
            expected.append(accepted)
    if accepted_answers:
        comparisons = [
            SequenceMatcher(
                None,
                normalize_for_storage(answer, channel),
                normalize_for_storage(item, channel),
            ).ratio()
            for item in accepted_answers
        ]
        score = max(score, *comparisons)

    if score >= 0.9:
        verdict, feedback = "correct", "Correct — nicely done."
    elif score >= 0.7:
        verdict, feedback = "mostly_correct", "Close. Compare your answer with the expected form."
    else:
        verdict, feedback = "incorrect", "Not quite. Review the expected answer before continuing."
    return StudyAttemptResult(
        attemptId="",
        score=round(score, 3),
        verdict=verdict,
        finalVerdict=verdict,
        expectedAnswers=expected,
        feedback=feedback,
        evaluatorVersion=EVALUATOR_VERSION,
    )


def normalize_for_storage(answer: str, channel: StudyChannel) -> str:
    if channel == "pinyin":
        return _pinyin(answer)
    if channel == "english":
        return _plain(answer)
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", answer))