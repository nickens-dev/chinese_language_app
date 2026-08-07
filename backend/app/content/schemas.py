from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DeckSummary(BaseModel):
    """The small deck projection required by the library screen."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    item_count: int = Field(serialization_alias="itemCount")
    due_count: int = Field(serialization_alias="dueCount")
    weak_count: int = Field(serialization_alias="weakCount")
    last_studied_at: datetime | None = Field(serialization_alias="lastStudiedAt")
    accent: Literal["jade", "coral", "gold", "ink"]
