from fastapi import APIRouter, Query

from app.content.dictionary_provider import get_dictionary_provider
from app.content.schemas import DictionaryCandidateResponse

router = APIRouter(prefix="/dictionary", tags=["dictionary"])


@router.get("/search", response_model=list[DictionaryCandidateResponse])
def search_dictionary(
    query: str = Query(alias="q", min_length=1, max_length=120),
    limit: int = Query(default=10, ge=1, le=20),
) -> list[DictionaryCandidateResponse]:
    """Search CC-CEDICT by characters, pinyin, or English and return reviewed candidates."""
    return [
        DictionaryCandidateResponse.model_validate(candidate, from_attributes=True)
        for candidate in get_dictionary_provider().search(query, limit)
    ]