from fastapi import APIRouter, HTTPException, status

from app.study.repository import (
    StudyNotFoundError,
    StudyStateError,
    advance_session,
    create_session,
    get_session,
    submit_attempt,
)
from app.study.schemas import (
    StudyAttemptCreate,
    StudyAttemptResult,
    StudySession,
    StudySessionCreate,
)

router = APIRouter(prefix="/study/sessions", tags=["study"])


def _not_found(error: StudyNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(error))


def _conflict(error: StudyStateError) -> HTTPException:
    return HTTPException(status_code=409, detail=str(error))


@router.post("", response_model=StudySession, status_code=status.HTTP_201_CREATED)
def post_session(values: StudySessionCreate) -> StudySession:
    try:
        return create_session(values)
    except StudyNotFoundError as error:
        raise _not_found(error) from error
    except StudyStateError as error:
        raise _conflict(error) from error


@router.get("/{session_id}", response_model=StudySession)
def get_study_session(session_id: str) -> StudySession:
    try:
        return get_session(session_id)
    except StudyNotFoundError as error:
        raise _not_found(error) from error


@router.post("/{session_id}/attempts", response_model=StudyAttemptResult, status_code=status.HTTP_201_CREATED)
def post_attempt(session_id: str, values: StudyAttemptCreate) -> StudyAttemptResult:
    try:
        return submit_attempt(session_id, values.answer)
    except StudyNotFoundError as error:
        raise _not_found(error) from error
    except StudyStateError as error:
        raise _conflict(error) from error


@router.post("/{session_id}/advance", response_model=StudySession)
def post_advance(session_id: str) -> StudySession:
    try:
        return advance_session(session_id)
    except StudyNotFoundError as error:
        raise _not_found(error) from error
    except StudyStateError as error:
        raise _conflict(error) from error