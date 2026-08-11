from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.progress.repository import get_progress
from app.progress.schemas import ProgressReport, StudyChannel

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=ProgressReport)
def read_progress(
    days: Annotated[int, Query(ge=0, le=90)] = 30,
    deck_id: Annotated[str | None, Query(alias="deckId")] = None,
    prompt_channel: Annotated[
        StudyChannel | None, Query(alias="promptChannel")
    ] = None,
    response_channel: Annotated[
        StudyChannel | None, Query(alias="responseChannel")
    ] = None,
    timezone_offset: Annotated[
        int, Query(alias="timezoneOffset", ge=-840, le=840)
    ] = 0,
) -> ProgressReport:
    """Return read-only progress aggregates for the selected history slice."""
    if days not in {0, 7, 30, 90}:
        raise HTTPException(status_code=422, detail="Days must be 0, 7, 30, or 90.")
    return get_progress(
        days, deck_id, prompt_channel, response_channel, timezone_offset
    )