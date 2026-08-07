# Getting Started

## Prerequisites

Install these tools before running the application:

- Git;
- Node.js 22 or newer, including npm;
- Python 3.12 or newer, including `pip` and the `py` launcher.

The project has been validated with Node.js 24.18.1, npm 11.16.0, Python 3.14.6, and SQLite 3.50.4. The supported minimums remain Node.js 22 and Python 3.12.

On Windows systems where PowerShell script execution is restricted, use `npm.cmd` rather than `npm`. This invokes npm's standard Windows command shim without changing the machine's execution policy.

## Start the backend

Open PowerShell in the repository root:

```powershell
Set-Location backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, and its interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Start the frontend

Open a second PowerShell window in the repository root:

```powershell
Set-Location frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173`. Vite forwards requests beginning with `/api` to the backend.

## What happens on first launch

FastAPI creates `backend/data/chinese_study.db`. If the database contains no decks, it inserts three demonstration deck summaries so the first screen has realistic content. The database is local and ignored by Git.

## Validate the project

Backend:

```powershell
Set-Location backend
ruff check .
pytest
```

Frontend:

```powershell
Set-Location frontend
npm.cmd run lint
npm.cmd run build
npm.cmd run test
```
