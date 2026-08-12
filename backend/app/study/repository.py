from datetime import UTC, datetime
from sqlite3 import Connection
from uuid import uuid4

from app.persistence.database import connect
from app.study.evaluator import evaluate, normalize_for_storage
from app.study.scheduler import record_review, sync_deck_schedule_counts, weak_reason
from app.study.schemas import (
    StudyAttemptResult,
    StudyAttemptReview,
    StudyCardResult,
    StudySession,
    StudySessionCreate,
    StudySessionSummary,
)


class StudyNotFoundError(LookupError):
    pass


class StudyStateError(ValueError):
    pass


def _summary(connection: Connection, session_id: str) -> StudySessionSummary:
    rows = connection.execute(
        """SELECT prompts.id AS prompt_id, prompts.item_id, prompts.simplified,
        prompts.pinyin, prompts.english, attempts.raw_answer, attempts.score,
        attempts.verdict, attempts.final_verdict, attempts.overridden_at,
        prompts.selection_reason, prompts.prompt_channel, prompts.response_channel
        FROM study_prompts AS prompts
        JOIN study_attempts AS attempts ON attempts.prompt_id = prompts.id
        WHERE prompts.session_id = ? ORDER BY prompts.position""",
        (session_id,),
    ).fetchall()
    results: list[StudyCardResult] = []
    for row in rows:
        history = connection.execute(
            """SELECT COUNT(*) AS attempts,
            SUM(CASE WHEN attempts.final_verdict = 'correct' THEN 1 ELSE 0 END)
                AS correct
            FROM study_attempts AS attempts
            JOIN study_prompts AS prompts ON prompts.id = attempts.prompt_id
            WHERE prompts.item_id = ? AND prompts.prompt_channel = ?
                AND prompts.response_channel = ?""",
            (row["item_id"], row["prompt_channel"], row["response_channel"]),
        ).fetchone()
        historical_attempts = history["attempts"]
        historical_correct = history["correct"] or 0
        results.append(
            StudyCardResult(
                promptId=row["prompt_id"], simplified=row["simplified"],
                pinyin=row["pinyin"], english=row["english"],
                answer=row["raw_answer"], score=row["score"],
                evaluatorVerdict=row["verdict"], finalVerdict=row["final_verdict"],
                overridden=row["overridden_at"] is not None,
                selectionReason=row["selection_reason"],
                historicalCorrect=historical_correct,
                historicalAttempts=historical_attempts,
                historicalPercent=round(historical_correct / historical_attempts * 100, 1),
            )
        )
    total = len(results)
    counts = {
        verdict: sum(result.final_verdict == verdict for result in results)
        for verdict in ("correct", "mostly_correct", "incorrect")
    }
    return StudySessionSummary(
        correctCount=counts["correct"], mostlyCorrectCount=counts["mostly_correct"],
        incorrectCount=counts["incorrect"],
        overriddenCount=sum(result.overridden for result in results),
        correctPercent=round(counts["correct"] / total * 100, 1) if total else 0,
        averageScore=round(sum(result.score for result in results) / total * 100, 1) if total else 0,
        results=results,
    )

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
        text = prompt[prompt["prompt_channel"] if prompt["prompt_channel"] != "characters" else "simplified"]
        current = {
            "id": prompt["id"], "position": prompt["position"], "total": count,
            "promptText": text, "promptChannel": prompt["prompt_channel"],
            "responseChannel": prompt["response_channel"], "answered": prompt["attempt_id"] is not None,
            "selectionReason": prompt["selection_reason"], "selectionBucket": prompt["selection_bucket"],
        }
    return StudySession(
        id=row["id"], status=row["status"], requestedCount=row["requested_count"], actualCount=count,
        currentIndex=row["current_index"], promptChannel=row["prompt_channel"], responseChannel=row["response_channel"],
        createdAt=row["created_at"], completedAt=row["completed_at"], currentPrompt=current,
        summary=_summary(connection, session_id)
        if row["status"] == "completed" else None,
    )


def _select_cards(
    connection: Connection,
    values: StudySessionCreate,
    prompt_channel: str,
    response_channel: str,
) -> list[dict[str, object]]:
    placeholders = ",".join("?" for _ in values.deck_ids)
    item_filter = ""
    extra_items = values.item_ids or []
    if extra_items:
        item_filter = " AND items.id IN (" + ",".join("?" for _ in extra_items) + ")"
    rows = connection.execute(
        f"""SELECT items.id, items.simplified, items.traditional, items.pinyin,
        items.english, MIN(memberships.position) AS first_position,
        MIN(memberships.added_at) AS first_added, states.due_at
        FROM deck_memberships AS memberships
        JOIN language_items AS items ON items.id = memberships.item_id
        LEFT JOIN card_skill_states AS states ON states.item_id = items.id
            AND states.prompt_channel = ? AND states.response_channel = ?
        WHERE memberships.deck_id IN ({placeholders})
            AND items.archived_at IS NULL {item_filter}
        GROUP BY items.id ORDER BY first_position, first_added, items.id""",
        [prompt_channel, response_channel, *values.deck_ids, *extra_items],
    ).fetchall()
    now = datetime.now(UTC)
    selected: list[dict[str, object]] = []
    for row in rows:
        weak = weak_reason(connection, row["id"], prompt_channel, response_channel)
        due_at = datetime.fromisoformat(row["due_at"]) if row["due_at"] else None
        is_due = due_at is not None and due_at <= now
        if values.selection_policy == "weak" and weak is None:
            continue
        if values.selection_policy == "due" and not is_due:
            continue
        if values.selection_policy == "new" and due_at is not None:
            continue
        if is_due and weak:
            bucket, rank = "overdue_weak", 0
        elif is_due:
            bucket, rank = "due", 1
        elif weak:
            bucket, rank = "weak", 2
        elif due_at is None:
            bucket, rank = "new", 3
        else:
            bucket, rank = "early_fill", 4
        reasons: list[str] = []
        if is_due and due_at:
            overdue_days = max(0, (now - due_at).days)
            reasons.append(f"Overdue by {overdue_days} day{'s' if overdue_days != 1 else ''}" if overdue_days else "Due now")
        elif due_at is None:
            reasons.append("New in this study direction")
        elif bucket == "early_fill":
            reasons.append("Selected to fill your requested session size")
        if weak:
            reasons.append(weak.capitalize())
        selected.append({**dict(row), "prompt_channel": prompt_channel,
                         "response_channel": response_channel,
                         "selection_reason": "; ".join(reasons),
                         "selection_bucket": bucket, "rank": rank,
                         "due_sort": row["due_at"] or ""})
    selected.sort(key=lambda item: (item["rank"], item["due_sort"], item["first_position"], item["id"]))
    return selected[: values.requested_count]

def create_session(values: StudySessionCreate) -> StudySession:
    now, session_id = datetime.now(UTC).isoformat(), str(uuid4())
    placeholders = ",".join("?" for _ in values.deck_ids)
    with connect() as connection:
        deck_count = connection.execute(
            f"SELECT COUNT(*) FROM decks WHERE id IN ({placeholders}) AND archived_at IS NULL", values.deck_ids
        ).fetchone()[0]
        if deck_count != len(values.deck_ids):
            raise StudyNotFoundError("One or more decks were not found.")
        modes = [
            ("characters", "english"), ("english", "characters"),
            ("characters", "pinyin"), ("pinyin", "english"),
        ] if values.mixed_mode else [(values.prompt_channel, values.response_channel)]
        mode_cards = [_select_cards(connection, values, *mode) for mode in modes]
        cards = []
        for index in range(max((len(candidates) for candidates in mode_cards), default=0)):
            for candidates in mode_cards:
                if index < len(candidates):
                    cards.append(candidates[index])
                    if len(cards) == values.requested_count:
                        break
            if len(cards) == values.requested_count:
                break
        if not cards:
            descriptions = {"weak": "weak", "due": "due", "new": "new"}
            focus = descriptions.get(values.selection_policy)
            message = (f"No {focus} cards match the selected decks and study mode."
                       if focus else "The selected decks do not contain any cards.")
            raise StudyStateError(message)
        if any(card["prompt_channel"] == "pinyin" and not card["pinyin"] for card in cards):
            raise StudyStateError("Every selected card needs pinyin for this study mode.")
        if any(card["response_channel"] == "pinyin" and not card["pinyin"] for card in cards):
            raise StudyStateError("Every selected card needs pinyin for this study mode.")
        connection.execute(
            "INSERT INTO study_sessions (id, requested_count, prompt_channel, response_channel, selection_policy, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, values.requested_count, values.prompt_channel, values.response_channel, values.selection_policy, now),
        )
        connection.executemany("INSERT INTO study_session_decks (session_id, deck_id) VALUES (?, ?)", [(session_id, deck_id) for deck_id in values.deck_ids])
        connection.executemany(
            """INSERT INTO study_prompts (id, session_id, item_id, position,
            simplified, traditional, pinyin, english, prompt_channel,
            response_channel, selection_reason, selection_bucket)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [(str(uuid4()), session_id, card["id"], position, card["simplified"],
              card["traditional"], card["pinyin"], card["english"],
              card["prompt_channel"], card["response_channel"],
              card["selection_reason"], card["selection_bucket"])
             for position, card in enumerate(cards)],
        )
        connection.commit()
        return _session(connection, session_id)


def get_session(session_id: str) -> StudySession:
    with connect() as connection:
        return _session(connection, session_id)


def _accepted_answers(
    connection: Connection, item_id: str, channel: str
) -> list[str]:
    return [
        row["answer"]
        for row in connection.execute(
            """SELECT answer FROM accepted_answers
            WHERE item_id = ? AND channel = ? ORDER BY created_at""",
            (item_id, channel),
        )
    ]


def submit_attempt(session_id: str, answer: str) -> StudyAttemptResult:
    now, attempt_id = datetime.now(UTC).isoformat(), str(uuid4())
    with connect() as connection:
        session = _session(connection, session_id)
        if session.status != "active" or session.current_prompt is None:
            raise StudyStateError("This session is already complete.")
        prompt = connection.execute(
            "SELECT * FROM study_prompts WHERE id = ?", (session.current_prompt.id,)
        ).fetchone()
        if connection.execute(
            "SELECT 1 FROM study_attempts WHERE prompt_id = ?", (prompt["id"],)
        ).fetchone():
            raise StudyStateError("This prompt has already been answered.")
        snapshot = {
            key: prompt[key]
            for key in ("simplified", "traditional", "pinyin", "english")
        }
        accepted = _accepted_answers(
            connection, prompt["item_id"], prompt["response_channel"]
        )
        result = evaluate(answer, prompt["response_channel"], snapshot, accepted)
        connection.execute(
            """INSERT INTO study_attempts (
                id, prompt_id, raw_answer, normalized_answer, score, verdict,
                final_verdict, feedback, evaluator_version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                attempt_id,
                prompt["id"],
                answer,
                normalize_for_storage(answer, prompt["response_channel"]),
                result.score,
                result.verdict,
                result.verdict,
                result.feedback,
                result.evaluator_version,
                now,
            ),
        )
        record_review(connection, attempt_id)
        sync_deck_schedule_counts(connection)
        connection.commit()
        return result.model_copy(update={"attempt_id": attempt_id})


def review_attempt(attempt_id: str, values: StudyAttemptReview) -> StudyAttemptResult:
    now = datetime.now(UTC).isoformat()
    with connect() as connection:
        row = connection.execute(
            """SELECT attempts.*, prompts.item_id, prompts.simplified,
            prompts.traditional, prompts.pinyin, prompts.english,
            prompts.response_channel
            FROM study_attempts AS attempts
            JOIN study_prompts AS prompts ON prompts.id = attempts.prompt_id
            WHERE attempts.id = ?""",
            (attempt_id,),
        ).fetchone()
        if row is None:
            raise StudyNotFoundError(attempt_id)
        if row["overridden_at"] is not None:
            raise StudyStateError("This attempt has already been reviewed.")
        connection.execute(
            """UPDATE study_attempts
            SET final_verdict = 'correct', override_reason = ?, overridden_at = ?
            WHERE id = ?""",
            (values.reason.strip(), now, attempt_id),
        )
        answer_added = False
        if values.add_to_card:
            normalized = normalize_for_storage(
                row["raw_answer"], row["response_channel"]
            )
            result = connection.execute(
                """INSERT OR IGNORE INTO accepted_answers (
                    id, item_id, channel, answer, normalized_answer,
                    source_attempt_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid4()),
                    row["item_id"],
                    row["response_channel"],
                    row["raw_answer"],
                    normalized,
                    attempt_id,
                    now,
                ),
            )
            answer_added = result.rowcount > 0
        record_review(connection, attempt_id)
        sync_deck_schedule_counts(connection)
        snapshot = {
            key: row[key]
            for key in ("simplified", "traditional", "pinyin", "english")
        }
        expected = evaluate(
            row["raw_answer"],
            row["response_channel"],
            snapshot,
            _accepted_answers(connection, row["item_id"], row["response_channel"]),
        ).expected_answers
        connection.commit()
        return StudyAttemptResult(
            attemptId=attempt_id,
            score=row["score"],
            verdict=row["verdict"],
            finalVerdict="correct",
            overridden=True,
            acceptedAnswerAdded=answer_added,
            expectedAnswers=expected,
            feedback="Marked correct by you.",
            evaluatorVersion=row["evaluator_version"],
        )

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
