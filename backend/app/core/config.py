from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Local defaults; environment overrides will be added when needed."""

    database_path: Path = BACKEND_ROOT / "data" / "chinese_study.db"
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
