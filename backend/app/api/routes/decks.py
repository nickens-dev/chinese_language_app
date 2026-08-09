from fastapi import APIRouter, HTTPException, Response, status

from app.content.repository import (
    DeckNameConflictError,
    DeckNotFoundError,
    archive_deck,
    create_deck,
    get_deck,
    list_decks,
    update_deck,
)
from app.content.schemas import DeckCreate, DeckSummary, DeckUpdate

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=list[DeckSummary])
def get_decks() -> list[DeckSummary]:
    """Return visual-card summaries for every active deck."""
    return list_decks()


@router.post("", response_model=DeckSummary, status_code=status.HTTP_201_CREATED)
def post_deck(values: DeckCreate) -> DeckSummary:
    """Create a learner-owned deck."""
    try:
        return create_deck(values)
    except DeckNameConflictError as error:
        raise HTTPException(status_code=409, detail="An active deck already uses that name.") from error


@router.get("/{deck_id}", response_model=DeckSummary)
def get_deck_by_id(deck_id: str) -> DeckSummary:
    try:
        return get_deck(deck_id)
    except DeckNotFoundError as error:
        raise HTTPException(status_code=404, detail="Deck not found.") from error


@router.patch("/{deck_id}", response_model=DeckSummary)
def patch_deck(deck_id: str, values: DeckUpdate) -> DeckSummary:
    """Update only the supplied editable fields."""
    try:
        return update_deck(deck_id, values)
    except DeckNotFoundError as error:
        raise HTTPException(status_code=404, detail="Deck not found.") from error
    except DeckNameConflictError as error:
        raise HTTPException(status_code=409, detail="An active deck already uses that name.") from error


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(deck_id: str) -> Response:
    """Archive a deck while preserving future item and attempt history."""
    try:
        archive_deck(deck_id)
    except DeckNotFoundError as error:
        raise HTTPException(status_code=404, detail="Deck not found.") from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
