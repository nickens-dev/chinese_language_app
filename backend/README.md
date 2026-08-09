# Backend

The backend is a Python and FastAPI application. It owns learning rules, persistence, evaluation, and integrations so future desktop and mobile clients behave consistently.

## Source map

```text
app/
  api/          HTTP routes and request/response boundary
  content/      Language items, deck projections, and dictionary entry
  study/        Future sessions, selection, attempts, and mastery
  evaluation/   Future character, pinyin, meaning, and speech evaluation
  intelligence/ Future retrieval and ML provider adapters
  persistence/  SQLite connections, schema, repositories, and migrations
  core/         Configuration and shared infrastructure
tests/          Unit, integration, contract, and simulation tests
data/           Ignored local SQLite database files
```

The current vertical slice exposes health, persistent deck CRUD, and card-management endpoints. Startup creates the SQLite schema when needed and preserves the learner's existing decks; it does not insert sample content.

## Commands

After installing Python 3.12 or newer:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

FastAPI runs at `http://127.0.0.1:8000`. Its interactive API documentation is at `http://127.0.0.1:8000/docs`.

Validation commands:

```powershell
ruff check .
pytest
```

## Boundaries

- Routes translate HTTP data and delegate; they do not contain learning rules.
- API schemas are not database models.
- Repositories isolate SQLite queries from application behavior.
- Attempts will be append-only, while mastery remains derived and rebuildable.
- Dictionary and ML providers will sit behind interfaces and must preserve provenance.
