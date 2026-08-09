from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

StudyChannel = Literal["characters", "english", "pinyin"]
StudyVerdict = Literal["correct", "mostly_correct", "incorrect"]


class StudySessionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    deck_ids: list[str] = Field(alias="deckIds", min_length=1)
    requested_count: int = Field(alias="requestedCount", gt=0, le=500)
    prompt_channel: StudyChannel = Field(alias="promptChannel")
    response_channel: StudyChannel = Field(alias="responseChannel")

    @model_validator(mode="after")
    def validate_mode(self) -> "StudySessionCreate":
        supported = {
            ("characters", "english"), ("english", "characters"),
            ("characters", "pinyin"), ("pinyin", "english"),
        }
        if (self.prompt_channel, self.response_channel) not in supported:
            raise ValueError("That prompt and response combination is not supported yet.")
        self.deck_ids = list(dict.fromkeys(self.deck_ids))
        return self


class StudyPrompt(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    position: int
    total: int
    prompt_text: str = Field(alias="promptText")
    prompt_channel: StudyChannel = Field(alias="promptChannel")
    response_channel: StudyChannel = Field(alias="responseChannel")
    answered: bool


class StudySession(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    status: Literal["active", "completed"]
    requested_count: int = Field(alias="requestedCount")
    actual_count: int = Field(alias="actualCount")
    current_index: int = Field(alias="currentIndex")
    prompt_channel: StudyChannel = Field(alias="promptChannel")
    response_channel: StudyChannel = Field(alias="responseChannel")
    created_at: datetime = Field(alias="createdAt")
    completed_at: datetime | None = Field(alias="completedAt")
    current_prompt: StudyPrompt | None = Field(alias="currentPrompt")


class StudyAttemptCreate(BaseModel):
    answer: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def normalize_answer(self) -> "StudyAttemptCreate":
        self.answer = self.answer.strip()
        if not self.answer:
            raise ValueError("An answer is required.")
        return self


class StudyAttemptResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    score: float
    verdict: StudyVerdict
    expected_answers: list[str] = Field(alias="expectedAnswers")
    feedback: str
    evaluator_version: str = Field(alias="evaluatorVersion")