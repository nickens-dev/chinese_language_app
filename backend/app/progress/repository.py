from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from itertools import pairwise
from typing import Any

from app.persistence.database import connect
from app.progress.schemas import (
    CardProgress,
    DirectionProgress,
    ProgressOverview,
    ProgressReport,
    ProgressTrendPoint,
    RecentSession,
)


def _percent(correct: int, attempts: int) -> float:
    return round(correct / attempts * 100, 1) if attempts else 0


def _streaks(days: set[date]) -> tuple[int, int]:
    if not days:
        return 0, 0
    ordered = sorted(days)
    longest = run = 1
    for previous, current in pairwise(ordered):
        run = run + 1 if current - previous == timedelta(days=1) else 1
        longest = max(longest, run)
    latest = ordered[-1]
    if datetime.now(UTC).date() - latest > timedelta(days=1):
        return 0, longest
    current_streak = 1
    for index in range(len(ordered) - 1, 0, -1):
        if ordered[index] - ordered[index - 1] != timedelta(days=1):
            break
        current_streak += 1
    return current_streak, longest


def get_progress(
    days: int = 30,
    deck_id: str | None = None,
    prompt_channel: str | None = None,
    response_channel: str | None = None,
    timezone_offset: int = 0,
) -> ProgressReport:
    conditions: list[str] = []
    parameters: list[Any] = []
    if days:
        conditions.append("attempts.created_at >= ?")
        parameters.append((datetime.now(UTC) - timedelta(days=days)).isoformat())
    if deck_id:
        conditions.append(
            """EXISTS (SELECT 1 FROM study_session_decks AS selected_decks
            WHERE selected_decks.session_id = sessions.id
                AND selected_decks.deck_id = ?)"""
        )
        parameters.append(deck_id)
    if prompt_channel:
        conditions.append("sessions.prompt_channel = ?")
        parameters.append(prompt_channel)
    if response_channel:
        conditions.append("sessions.response_channel = ?")
        parameters.append(response_channel)
    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    with connect() as connection:
        rows = connection.execute(
            f"""SELECT attempts.id AS attempt_id, attempts.score,
            attempts.final_verdict, attempts.overridden_at,
            attempts.created_at AS attempt_created_at,
            prompts.item_id, prompts.simplified, prompts.pinyin, prompts.english,
            sessions.id AS session_id, sessions.status,
            sessions.prompt_channel, sessions.response_channel,
            sessions.completed_at
            FROM study_attempts AS attempts
            JOIN study_prompts AS prompts ON prompts.id = attempts.prompt_id
            JOIN study_sessions AS sessions ON sessions.id = prompts.session_id
            {where} ORDER BY attempts.created_at""",
            parameters,
        ).fetchall()

        attempts = len(rows)
        correct = sum(row["final_verdict"] == "correct" for row in rows)
        completed_ids = {
            row["session_id"] for row in rows if row["status"] == "completed"
        }
        study_dates = {
            (datetime.fromisoformat(row["attempt_created_at"]) - timedelta(minutes=timezone_offset)).date() for row in rows
        }
        current_streak, longest_streak = _streaks(study_dates)
        overview = ProgressOverview(
            accuracyPercent=_percent(correct, attempts),
            averageScore=round(sum(row["score"] for row in rows) / attempts * 100, 1)
            if attempts
            else 0,
            attempts=attempts,
            uniqueCards=len({row["item_id"] for row in rows}),
            completedSessions=len(completed_ids),
            studyDays=len(study_dates),
            currentStreak=current_streak,
            longestStreak=longest_streak,
            averageCardsPerSession=round(
                sum(row["status"] == "completed" for row in rows) / len(completed_ids), 1
            )
            if completed_ids
            else 0,
            lastStudiedAt=rows[-1]["attempt_created_at"] if rows else None,
        )

        trend_groups: dict[date, list[Any]] = defaultdict(list)
        direction_groups: dict[tuple[str, str], list[Any]] = defaultdict(list)
        card_groups: dict[tuple[str, str, str], list[Any]] = defaultdict(list)
        session_groups: dict[str, list[Any]] = defaultdict(list)
        for row in rows:
            trend_groups[(datetime.fromisoformat(row["attempt_created_at"]) - timedelta(minutes=timezone_offset)).date()].append(row)
            direction_groups[(row["prompt_channel"], row["response_channel"])].append(row)
            card_groups[(row["item_id"], row["prompt_channel"], row["response_channel"])].append(row)
            if row["status"] == "completed":
                session_groups[row["session_id"]].append(row)

        trend = [
            ProgressTrendPoint(
                date=day,
                attempts=len(group),
                accuracyPercent=_percent(
                    sum(row["final_verdict"] == "correct" for row in group), len(group)
                ),
            )
            for day, group in sorted(trend_groups.items())
        ]
        directions = [
            DirectionProgress(
                promptChannel=channels[0], responseChannel=channels[1],
                attempts=len(group),
                accuracyPercent=_percent(
                    sum(row["final_verdict"] == "correct" for row in group), len(group)
                ),
            )
            for channels, group in sorted(direction_groups.items())
        ]
        cards = []
        for (item_id, prompt, response), group in card_groups.items():
            latest = group[-1]
            cards.append(
                CardProgress(
                    itemId=item_id, simplified=latest["simplified"],
                    pinyin=latest["pinyin"], english=latest["english"],
                    promptChannel=prompt, responseChannel=response,
                    correct=sum(row["final_verdict"] == "correct" for row in group),
                    attempts=len(group),
                    accuracyPercent=_percent(
                        sum(row["final_verdict"] == "correct" for row in group), len(group)
                    ),
                    averageScore=round(
                        sum(row["score"] for row in group) / len(group) * 100, 1
                    ),
                    lastStudiedAt=latest["attempt_created_at"],
                )
            )
        cards.sort(key=lambda card: (card.accuracy_percent, -card.attempts, card.simplified))

        recent_sessions = []
        for session_id, group in sorted(
            session_groups.items(), key=lambda item: item[1][0]["completed_at"], reverse=True
        )[:10]:
            first = group[0]
            deck_names = [
                row[0]
                for row in connection.execute(
                    """SELECT decks.name FROM study_session_decks
                    JOIN decks ON decks.id = study_session_decks.deck_id
                    WHERE study_session_decks.session_id = ? ORDER BY decks.name""",
                    (session_id,),
                )
            ]
            recent_sessions.append(
                RecentSession(
                    id=session_id, completedAt=first["completed_at"],
                    deckNames=deck_names, promptChannel=first["prompt_channel"],
                    responseChannel=first["response_channel"], cardCount=len(group),
                    accuracyPercent=_percent(
                        sum(row["final_verdict"] == "correct" for row in group), len(group)
                    ),
                    overriddenCount=sum(row["overridden_at"] is not None for row in group),
                )
            )
    return ProgressReport(
        overview=overview, trend=trend, directions=directions,
        cards=cards, recentSessions=recent_sessions,
    )