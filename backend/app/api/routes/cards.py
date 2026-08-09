from fastapi import APIRouter, HTTPException, Response, status

from app.content.card_repository import (
    CardMembershipNotFoundError,
    CardNotFoundError,
    create_card,
    list_cards,
    remove_card_from_deck,
    update_card,
)
from app.content.schemas import Card, CardCreate, CardUpdate

router = APIRouter(tags=["cards"])


@router.get("/decks/{deck_id}/cards", response_model=list[Card])
def get_deck_cards(deck_id: str) -> list[Card]:
    """Return active cards in their deck order."""
    try:
        return list_cards(deck_id)
    except CardMembershipNotFoundError as error:
        raise HTTPException(status_code=404, detail="Deck not found.") from error


@router.post(
    "/decks/{deck_id}/cards", response_model=Card, status_code=status.HTTP_201_CREATED
)
def post_deck_card(deck_id: str, values: CardCreate) -> Card:
    """Create a language item and add it to the requested deck."""
    try:
        return create_card(deck_id, values)
    except CardMembershipNotFoundError as error:
        raise HTTPException(status_code=404, detail="Deck not found.") from error


@router.patch("/cards/{card_id}", response_model=Card)
def patch_card(card_id: str, values: CardUpdate) -> Card:
    """Update only the supplied language-item fields."""
    try:
        return update_card(card_id, values)
    except CardNotFoundError as error:
        raise HTTPException(status_code=404, detail="Card not found.") from error


@router.delete("/decks/{deck_id}/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck_card(deck_id: str, card_id: str) -> Response:
    """Remove a membership and archive the card when it becomes orphaned."""
    try:
        remove_card_from_deck(deck_id, card_id)
    except (CardNotFoundError, CardMembershipNotFoundError) as error:
        raise HTTPException(status_code=404, detail="Card not found in this deck.") from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)