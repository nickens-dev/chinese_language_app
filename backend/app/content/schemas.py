from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DeckAccent = Literal["jade", "coral", "gold", "ink"]


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
