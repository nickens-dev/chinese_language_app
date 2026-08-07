from fastapi import APIRouter

from app.content.repository import list_decks
from app.content.schemas import DeckSummary

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=list[DeckSummary])
def get_decks() -> list[DeckSummary]:
    """Return visual-card summaries for every active deck."""
    return list_decks()
