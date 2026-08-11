from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

StudyChannel = Literal["characters", "english", "pinyin"]


class ProgressOverview(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    accuracy_percent: float = Field(alias="accuracyPercent")
    average_score: float = Field(alias="averageScore")
    attempts: int
    unique_cards: int = Field(alias="uniqueCards")
    completed_sessions: int = Field(alias="completedSessions")
    study_days: int = Field(alias="studyDays")
    current_streak: int = Field(alias="currentStreak")
    longest_streak: int = Field(alias="longestStreak")
    average_cards_per_session: float = Field(alias="averageCardsPerSession")
    last_studied_at: datetime | None = Field(alias="lastStudiedAt")


class ProgressTrendPoint(BaseModel):
    date: date
    attempts: int
    accuracy_percent: float = Field(alias="accuracyPercent")


class DirectionProgress(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    prompt_channel: StudyChannel = Field(alias="promptChannel")
    response_channel: StudyChannel = Field(alias="responseChannel")
    attempts: int
    accuracy_percent: float = Field(alias="accuracyPercent")


class CardProgress(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    item_id: str = Field(alias="itemId")
    simplified: str
    pinyin: str
    english: str
    prompt_channel: StudyChannel = Field(alias="promptChannel")
    response_channel: StudyChannel = Field(alias="responseChannel")
    correct: int
    attempts: int
    accuracy_percent: float = Field(alias="accuracyPercent")
    average_score: float = Field(alias="averageScore")
    last_studied_at: datetime = Field(alias="lastStudiedAt")


class RecentSession(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    completed_at: datetime = Field(alias="completedAt")
    deck_names: list[str] = Field(alias="deckNames")
    prompt_channel: StudyChannel = Field(alias="promptChannel")
    response_channel: StudyChannel = Field(alias="responseChannel")
    card_count: int = Field(alias="cardCount")
    accuracy_percent: float = Field(alias="accuracyPercent")
    overridden_count: int = Field(alias="overriddenCount")


class ProgressReport(BaseModel):
    overview: ProgressOverview
    trend: list[ProgressTrendPoint]
    directions: list[DirectionProgress]
    cards: list[CardProgress]
    recent_sessions: list[RecentSession] = Field(alias="recentSessions")