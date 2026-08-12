from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from sqlite3 import Connection

from app.persistence.database import connect

SCHEDULER_VERSION = "transparent-v1"


@dataclass
class SkillState:
    learning_state: str = "learning"
    due_at: datetime | None = None
    last_reviewed_at: datetime | None = None
    interval_days: float = 0
    stability: float = 0.5
    difficulty: float = 5
    review_count: int = 0
    lapse_count: int = 0


def verdict_rating(verdict: str) -> str:
    return {"incorrect": "again", "mostly_correct": "hard", "correct": "good"}[verdict]


def _apply(state: SkillState, rating: str, reviewed_at: datetime) -> SkillState:
    previous_reviews = state.review_count
    state.review_count += 1
    state.last_reviewed_at = reviewed_at
    if rating == "again":
        state.learning_state = "relearning" if previous_reviews else "learning"
        state.interval_days = 10 / 1440
        state.stability = max(0.25, state.stability * 0.5)
        state.difficulty = min(10, state.difficulty + 0.8)
        state.lapse_count += int(previous_reviews > 0)
    elif rating == "hard":
        state.learning_state = "learning" if previous_reviews < 2 else "review"
        state.interval_days = max(1, state.interval_days * 1.2)
        state.stability = max(1, state.stability * 1.2)
        state.difficulty = min(10, state.difficulty + 0.25)
    elif rating == "easy":
        state.learning_state = "review"
        state.interval_days = 4 if previous_reviews == 0 else max(4, state.interval_days * 3.2)
        state.stability = state.interval_days
        state.difficulty = max(1, state.difficulty - 0.35)
    else:
        state.learning_state = "learning" if previous_reviews == 0 else "review"
        state.interval_days = 1 if previous_reviews == 0 else max(3, state.interval_days * 2.5)
        state.stability = state.interval_days
        state.difficulty = max(1, state.difficulty - 0.1)
    state.due_at = reviewed_at + timedelta(days=state.interval_days)
    return state


def rebuild_skill(connection: Connection, item_id: str, prompt: str, response: str) -> None:
    state = SkillState()
    events = connection.execute(
        """SELECT rating, reviewed_at FROM review_events
        WHERE item_id = ? AND prompt_channel = ? AND response_channel = ?
        ORDER BY reviewed_at, attempt_id""",
        (item_id, prompt, response),
    ).fetchall()
    if not events:
        connection.execute(
            "DELETE FROM card_skill_states WHERE item_id = ? AND prompt_channel = ? AND response_channel = ?",
            (item_id, prompt, response),
        )
        return
    for event in events:
        _apply(state, event["rating"], datetime.fromisoformat(event["reviewed_at"]))
    connection.execute(
        """INSERT INTO card_skill_states (
            item_id, prompt_channel, response_channel, learning_state, due_at,
            last_reviewed_at, interval_days, stability, difficulty, review_count,
            lapse_count, scheduler_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(item_id, prompt_channel, response_channel) DO UPDATE SET
            learning_state=excluded.learning_state, due_at=excluded.due_at,
            last_reviewed_at=excluded.last_reviewed_at, interval_days=excluded.interval_days,
            stability=excluded.stability, difficulty=excluded.difficulty,
            review_count=excluded.review_count, lapse_count=excluded.lapse_count,
            scheduler_version=excluded.scheduler_version""",
        (item_id, prompt, response, state.learning_state, state.due_at.isoformat(),
         state.last_reviewed_at.isoformat(), state.interval_days, state.stability,
         state.difficulty, state.review_count, state.lapse_count, SCHEDULER_VERSION),
    )


def record_review(connection: Connection, attempt_id: str) -> None:
    row = connection.execute(
        """SELECT COALESCE(attempts.final_verdict, attempts.verdict) AS final_verdict,
        attempts.created_at, prompts.item_id,
        prompts.prompt_channel, prompts.response_channel
        FROM study_attempts AS attempts
        JOIN study_prompts AS prompts ON prompts.id = attempts.prompt_id
        WHERE attempts.id = ?""",
        (attempt_id,),
    ).fetchone()
    connection.execute(
        """INSERT INTO review_events (
            attempt_id, item_id, prompt_channel, response_channel, rating,
            reviewed_at, scheduler_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(attempt_id) DO UPDATE SET rating=excluded.rating,
            scheduler_version=excluded.scheduler_version""",
        (attempt_id, row["item_id"], row["prompt_channel"], row["response_channel"],
         verdict_rating(row["final_verdict"]), row["created_at"], SCHEDULER_VERSION),
    )
    rebuild_skill(connection, row["item_id"], row["prompt_channel"], row["response_channel"])


def weak_reason(connection: Connection, item_id: str, prompt: str, response: str) -> str | None:
    events = connection.execute(
        """SELECT rating FROM review_events WHERE item_id = ? AND prompt_channel = ?
        AND response_channel = ? ORDER BY reviewed_at DESC""",
        (item_id, prompt, response),
    ).fetchall()
    if len(events) < 2:
        return None
    ratings = [row["rating"] for row in events]
    accuracy = sum(rating in {"good", "easy"} for rating in ratings) / len(ratings)
    recent = ratings[:3]
    state = connection.execute(
        """SELECT lapse_count, difficulty FROM card_skill_states
        WHERE item_id = ? AND prompt_channel = ? AND response_channel = ?""",
        (item_id, prompt, response),
    ).fetchone()
    reasons = []
    if accuracy < 0.7:
        reasons.append(f"{round(accuracy * 100)}% reviewed accuracy")
    if recent and recent[0] == "again":
        reasons.append("incorrect last time")
    if state and state["lapse_count"] >= 2:
        reasons.append(f"{state['lapse_count']} lapses")
    if state and state["difficulty"] >= 6.5:
        reasons.append("high scheduler difficulty")
    return "; ".join(reasons) or None


def sync_deck_schedule_counts(connection: Connection) -> None:
    now = datetime.now(UTC).isoformat()
    decks = connection.execute("SELECT id FROM decks WHERE archived_at IS NULL").fetchall()
    for deck in decks:
        items = connection.execute(
            """SELECT DISTINCT memberships.item_id FROM deck_memberships AS memberships
            JOIN language_items AS items ON items.id = memberships.item_id
            WHERE memberships.deck_id = ? AND items.archived_at IS NULL""",
            (deck["id"],),
        ).fetchall()
        due_items: set[str] = set()
        weak_items: set[str] = set()
        for item in items:
            states = connection.execute(
                "SELECT * FROM card_skill_states WHERE item_id = ?", (item["item_id"],)
            ).fetchall()
            for state in states:
                if state["due_at"] <= now:
                    due_items.add(item["item_id"])
                if weak_reason(connection, item["item_id"], state["prompt_channel"], state["response_channel"]):
                    weak_items.add(item["item_id"])
        connection.execute(
            "UPDATE decks SET due_count = ?, weak_count = ? WHERE id = ?",
            (len(due_items), len(weak_items), deck["id"]),
        )


def backfill_schedule() -> None:
    with connect() as connection:
        attempts = connection.execute(
            """SELECT attempts.id FROM study_attempts AS attempts
            LEFT JOIN review_events ON review_events.attempt_id = attempts.id
            WHERE review_events.attempt_id IS NULL ORDER BY attempts.created_at"""
        ).fetchall()
        for attempt in attempts:
            record_review(connection, attempt["id"])
        sync_deck_schedule_counts(connection)
        connection.commit()
