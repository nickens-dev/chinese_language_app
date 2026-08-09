from fastapi import APIRouter

from app.api.routes import cards, decks, dictionary, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(decks.router)
api_router.include_router(cards.router)
api_router.include_router(dictionary.router)
