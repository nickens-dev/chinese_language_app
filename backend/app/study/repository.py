from datetime import UTC, datetime
from sqlite3 import Connection
from uuid import uuid4

from app.persistence.database import connect
from app.study.evaluator import evaluate, normalize_for_storage
from app.study.schemas import StudyAttemptResult, StudySession, StudySessionCreate


class StudyNotFoundError(LookupError):
    pass


class StudyStateError(ValueError):
    pass


def _session(connection: Connection, session_id: str) -> StudySession:
    row = connection.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise StudyNotFoundError(session_id)
    count = connection.execute("SELECT COUNT(*) FROM study_prompts WHERE session_id = ?", (session_id,)).fetchone()[0]
    prompt = connection.execute(
        """SELECT prompts.*, attempts.id AS attempt_id FROM study_prompts AS prompts
        LEFT JOIN study_attempts AS attempts ON attempts.prompt_id = prompts.id
        WHERE prompts.session_id = ? AND prompts.position = ?""",
        (session_id, row["current_index"]),
    ).fetchone()
    current = None
    if prompt is not None and row["status"] == "active":
        text = prompt[row["prompt_channel"] if row["prompt_channel"] != "characters" else "simplified"]
        current = {
            "id": prompt["id"], "position": prompt["position"], "total": count,
            "promptText": text, "promptChannel": row["prompt_channel"],
            "responseChannel": row["response_channel"], "answered": prompt["attempt_id"] is not None,
        }
    return StudySession(
        id=row["id"], status=row["status"], requestedCount=row["requested_count"], actualCount=count,
        currentIndex=row["current_index"], promptChannel=row["prompt_channel"], responseChannel=row["response_channel"],
        createdAt=row["created_at"], completedAt=row["completed_at"], currentPrompt=current,
    )


def create_session(values: StudySessionCreate) -> StudySession:
    now, session_id = datetime.now(UTC).isoformat(), str(uuid4())
    placeholders = ",".join("?" for _ in values.deck_ids)
    with connect() as connection:
        deck_count = connection.execute(
            f"SELECT COUNT(*) FROM decks WHERE id IN ({placeholders}) AND archived_at IS NULL", values.deck_ids
        ).fetchone()[0]
        if deck_count != len(values.deck_ids):
            raise StudyNotFoundError("One or more decks were not found.")
        cards = connection.execute(
            f"""SELECT items.id, items.simplified, items.traditional, items.pinyin, items.english,
            MIN(memberships.position) AS first_position, MIN(memberships.added_at) AS first_added
            FROM deck_memberships AS memberships JOIN language_items AS items ON items.id = memberships.item_id
            WHERE memberships.deck_id IN ({placeholders}) AND items.archived_at IS NULL
            GROUP BY items.id ORDER BY first_position, first_added, items.id LIMIT ?""",
            [*values.deck_ids, values.requested_count],
        ).fetchall()
        if not cards:
            raise StudyStateError("The selected decks do not contain any cards.")
        if values.prompt_channel == "pinyin" and any(not card["pinyin"] for card in cards):
            raise StudyStateError("Every selected card needs pinyin for this study mode.")
        if values.response_channel == "pinyin" and any(not card["pinyin"] for card in cards):
            raise StudyStateError("Every selected card needs pinyin for this study mode.")
        connection.execute(
            "INSERT INTO study_sessions (id, requested_count, prompt_channel, response_channel, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, values.requested_count, values.prompt_channel, values.response_channel, now),
        )
        connection.executemany("INSERT INTO study_session_decks (session_id, deck_id) VALUES (?, ?)", [(session_id, deck_id) for deck_id in values.deck_ids])
        connection.executemany(
            """INSERT INTO study_prompts (id, session_id, item_id, position, simplified, traditional, pinyin, english)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [(str(uuid4()), session_id, card["id"], position, card["simplified"], card["traditional"], card["pinyin"], card["english"]) for position, card in enumerate(cards)],
        )
        connection.commit()
        return _session(connection, session_id)


def get_session(session_id: str) -> StudySession:
    with connect() as connection:
        return _session(connection, session_id)


def submit_attempt(session_id: str, answer: str) -> StudyAttemptResult:
    now = datetime.now(UTC).isoformat()
    with connect() as connection:
        session = _session(connection, session_id)
        if session.status != "active" or session.current_prompt is None:
            raise StudyStateError("This session is already complete.")
        prompt = connection.execute("SELECT * FROM study_prompts WHERE id = ?", (session.current_prompt.id,)).fetchone()
        if connection.execute("SELECT 1 FROM study_attempts WHERE prompt_id = ?", (prompt["id"],)).fetchone():
            raise StudyStateError("This prompt has already been answered.")
        snapshot = {key: prompt[key] for key in ("simplified", "traditional", "pinyin", "english")}
        result = evaluate(answer, session.response_channel, snapshot)
        connection.execute(
            """INSERT INTO study_attempts (id, prompt_id, raw_answer, normalized_answer, score, verdict, feedback, evaluator_version, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(uuid4()), prompt["id"], answer, normalize_for_storage(answer, session.response_channel), result.score, result.verdict, result.feedback, result.evaluator_version, now),
        )
        connection.commit()
        return result


def advance_session(session_id: str) -> StudySession:
    now = datetime.now(UTC).isoformat()
    with connect() as connection:
        session = _session(connection, session_id)
        if session.status != "active" or session.current_prompt is None:
            raise StudyStateError("This session is already complete.")
        if not session.current_prompt.answered:
            raise StudyStateError("Answer the current prompt before continuing.")
        next_index = session.current_index + 1
        if next_index >= session.actual_count:
            connection.execute("UPDATE study_sessions SET current_index = ?, status = 'completed', completed_at = ? WHERE id = ?", (next_index, now, session_id))
            deck_ids = [row[0] for row in connection.execute("SELECT deck_id FROM study_session_decks WHERE session_id = ?", (session_id,))]
            connection.executemany("UPDATE decks SET last_studied_at = ?, updated_at = ? WHERE id = ?", [(now, now, deck_id) for deck_id in deck_ids])
        else:
            connection.execute("UPDATE study_sessions SET current_index = ? WHERE id = ?", (next_index, session_id))
        connection.commit()
        return _session(connection, session_id)