from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DeckAccent = Literal[
    "jade", "coral", "gold", "ink", "sky",
    "plum", "rose", "tangerine", "moss", "slate",
]


class DeckFields(BaseModel):
    """Editable deck fields shared by API inputs and outputs."""

    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=500)
    accent: DeckAccent = "jade"

    @model_validator(mode="after")
    def normalize_text(self) -> "DeckFields":
        self.name = self.name.strip()
        self.description = self.description.strip()
        if not self.name:
            raise ValueError("Deck name cannot be blank.")
        return self


class DeckCreate(DeckFields):
    """Fields accepted when a learner creates a deck."""


class DeckUpdate(BaseModel):
    """Editable fields; omitted values remain unchanged."""

    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    accent: DeckAccent | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "DeckUpdate":
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValueError("Deck name cannot be blank.")
        if self.description is not None:
            self.description = self.description.strip()
        if not self.model_fields_set:
            raise ValueError("At least one deck field is required.")
        return self


class DeckSummary(DeckFields):
    """The deck projection used by library and detail screens."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    item_count: int = Field(serialization_alias="itemCount")
    due_count: int = Field(serialization_alias="dueCount")
    weak_count: int = Field(serialization_alias="weakCount")
    last_studied_at: datetime | None = Field(serialization_alias="lastStudiedAt")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


CardType = Literal["word", "phrase", "sentence"]


class CardFields(BaseModel):
    """Editable language content shared by card inputs and outputs."""

    model_config = ConfigDict(populate_by_name=True)

    item_type: CardType = Field(alias="itemType")
    simplified: str = Field(min_length=1, max_length=120)
    traditional: str = Field(default="", max_length=120)
    pinyin: str = Field(default="", max_length=240)
    english: str = Field(min_length=1, max_length=300)
    notes: str = Field(default="", max_length=1000)
    source_name: str = Field(default="user", alias="sourceName", max_length=80)
    source_entry_id: str | None = Field(default=None, alias="sourceEntryId", max_length=120)

    @model_validator(mode="after")
    def normalize_card_text(self) -> "CardFields":
        self.simplified = self.simplified.strip()
        self.traditional = self.traditional.strip()
        self.pinyin = self.pinyin.strip()
        self.english = self.english.strip()
        self.notes = self.notes.strip()
        self.source_name = self.source_name.strip() or "user"
        if not self.simplified:
            raise ValueError("Simplified Chinese cannot be blank.")
        if not self.english:
            raise ValueError("English meaning cannot be blank.")
        return self


class CardCreate(CardFields):
    """Fields accepted when a learner creates a card in a deck."""


class CardUpdate(BaseModel):
    """Editable card fields; omitted values remain unchanged."""

    model_config = ConfigDict(populate_by_name=True)

    item_type: CardType | None = Field(default=None, alias="itemType")
    simplified: str | None = Field(default=None, min_length=1, max_length=120)
    traditional: str | None = Field(default=None, max_length=120)
    pinyin: str | None = Field(default=None, max_length=240)
    english: str | None = Field(default=None, min_length=1, max_length=300)
    notes: str | None = Field(default=None, max_length=1000)
    source_name: str | None = Field(default=None, alias="sourceName", max_length=80)
    source_entry_id: str | None = Field(default=None, alias="sourceEntryId", max_length=120)

    @model_validator(mode="after")
    def validate_update(self) -> "CardUpdate":
        for field in ("simplified", "traditional", "pinyin", "english", "notes", "source_name"):
            value = getattr(self, field)
            if value is not None:
                setattr(self, field, value.strip())
        if self.simplified is not None and not self.simplified:
            raise ValueError("Simplified Chinese cannot be blank.")
        if self.english is not None and not self.english:
            raise ValueError("English meaning cannot be blank.")
        if not self.model_fields_set:
            raise ValueError("At least one card field is required.")
        return self


class Card(CardFields):
    """A language item projected in deck order."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

class DictionaryCandidateResponse(BaseModel):
    """A sourced card candidate that still requires learner review."""

    model_config = ConfigDict(populate_by_name=True)

    simplified: str
    traditional: str
    pinyin: str
    definitions: tuple[str, ...]
    source_name: str = Field(alias="sourceName")
    source_entry_id: str | None = Field(alias="sourceEntryId")