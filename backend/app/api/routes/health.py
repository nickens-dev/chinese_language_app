from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    """Report that the local API process is ready."""
    return {"status": "ok"}
