import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy import event, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from misbot.database.models import Base, players, time_sessions
from misbot.database.queries.time_sessions import create_time_session
from misbot.domain.models import TimeSession


def _make_time_session(player_id: uuid.UUID, **kwargs) -> TimeSession:
    defaults = {
        "session_id": uuid.uuid4(),
        "player_id": player_id,
        "joined_at": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "quit_at": None,
    }
    defaults.update(kwargs)
    return TimeSession(**defaults)


@pytest_asyncio.fixture(scope="module")
async def db_engine_with_fk():
    """In-memory engine with SQLite foreign key enforcement enabled."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def enable_fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_test_data(db_engine):
    """Clean up time_sessions and players tables after each test."""
    yield
    async with db_engine.begin() as conn:
        await conn.execute(time_sessions.delete())
        await conn.execute(players.delete())


@pytest_asyncio.fixture
async def player_id(db_engine) -> uuid.UUID:
    """Insert a player row and return its UUID."""
    pid = uuid.uuid4()
    async with db_engine.begin() as conn:
        await conn.execute(
            insert(players).values(id=pid, seen=datetime(2024, 1, 1, tzinfo=timezone.utc)),
        )
    return pid


@pytest.mark.asyncio
async def test_create_time_session_new_record(db_engine, player_id):
    """create_time_session should persist and return the new session."""
    ts = _make_time_session(player_id)
    with patch("misbot.database.queries.time_sessions.engine", db_engine):
        result = await create_time_session(ts)
    assert result.session_id == ts.session_id
    assert result.player_id == player_id
    assert result.joined_at == ts.joined_at
    assert result.quit_at is None


@pytest.mark.asyncio
async def test_create_time_session_duplicate_returns_existing(db_engine, player_id):
    """create_time_session should return the original record on duplicate session_id."""
    ts = _make_time_session(player_id)
    duplicate = _make_time_session(
        player_id,
        session_id=ts.session_id,
        quit_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    with patch("misbot.database.queries.time_sessions.engine", db_engine):
        first = await create_time_session(ts)
        second = await create_time_session(duplicate)
    assert second.session_id == ts.session_id
    # original quit_at is preserved, not the duplicate's value
    assert second.quit_at == ts.quit_at


@pytest.mark.asyncio
async def test_create_time_session_non_unique_integrity_error_propagates(db_engine_with_fk):
    """FK violations (non-UNIQUE IntegrityErrors) should propagate unhandled."""
    ts = _make_time_session(uuid.uuid4())  # player_id does not exist in DB
    with patch("misbot.database.queries.time_sessions.engine", db_engine_with_fk):
        with pytest.raises(IntegrityError) as exc_info:
            await create_time_session(ts)
    assert "FOREIGN KEY" in str(exc_info.value.orig).upper()

