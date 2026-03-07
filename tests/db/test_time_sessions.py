import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from misbot.database.queries.time_sessions import create_time_session
from misbot.domain.models import TimeSession


def _make_session(**kwargs) -> TimeSession:
    defaults = {
        "session_id": uuid.uuid4(),
        "player_id": uuid.uuid4(),
        "joined_at": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "quit_at": None,
    }
    defaults.update(kwargs)
    return TimeSession(**defaults)


@pytest.mark.asyncio
async def test_create_time_session_duplicate_returns_existing():
    """create_time_session should return the existing record on duplicate session_id."""
    session_id = uuid.uuid4()
    player_id = uuid.uuid4()
    joined_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    original = _make_session(session_id=session_id, player_id=player_id, joined_at=joined_at)
    existing_row = original  # what the DB would return

    mock_conn = AsyncMock()
    mock_conn.execute.side_effect = [
        IntegrityError("UNIQUE constraint failed: time_sessions.session_id", None, Exception("UNIQUE constraint failed")),
        AsyncMock(fetchone=lambda: type("Row", (), {"_mapping": original.model_dump()})()),
    ]

    with patch("misbot.database.queries.time_sessions.engine") as mock_engine:
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await create_time_session(original)

    assert result.session_id == session_id
    assert result.player_id == player_id
    assert mock_conn.execute.call_count == 2


@pytest.mark.asyncio
async def test_create_time_session_non_unique_integrity_error_propagates():
    """Non-UNIQUE IntegrityErrors (e.g. FK violations) should propagate."""
    original = _make_session()

    mock_conn = AsyncMock()
    mock_conn.execute.side_effect = IntegrityError(
        "FOREIGN KEY constraint failed", None, Exception("FOREIGN KEY constraint failed")
    )

    with patch("misbot.database.queries.time_sessions.engine") as mock_engine:
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(IntegrityError):
            await create_time_session(original)


@pytest.mark.asyncio
async def test_create_time_session_new_record():
    """create_time_session should return the input session when insert succeeds."""
    original = _make_session()

    mock_conn = AsyncMock()
    mock_conn.execute.return_value = AsyncMock()

    with patch("misbot.database.queries.time_sessions.engine") as mock_engine:
        mock_engine.begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.begin.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await create_time_session(original)

    assert result == original
    assert mock_conn.execute.call_count == 1
