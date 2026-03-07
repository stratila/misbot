import logging

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from misbot.database.db import engine
from misbot.database.models import time_sessions
from misbot.domain.models import TimeSession

logging.getLogger(__name__)


async def get_time_session(session_id: str) -> TimeSession | None:
    """Get a time session by session_id."""
    async with engine.connect() as conn:
        result = await conn.execute(
            select(time_sessions).where(
                time_sessions.c.session_id == session_id,
            ),
        )
        session = result.fetchone()
        return TimeSession(**session._mapping) if session else None


async def create_time_session(time_session: TimeSession) -> TimeSession:
    """Create a new time session idempotently, returns full record.

    If a session with the same session_id already exists (e.g. due to a retry
    or concurrent request), the existing record is returned unchanged.
    """
    async with engine.begin() as conn:
        values = {
            "session_id": time_session.session_id,
            "player_id": time_session.player_id,
            "joined_at": time_session.joined_at,
            "quit_at": time_session.quit_at,
        }
        try:
            await conn.execute(
                insert(time_sessions).values(**values),
            )
        except IntegrityError as exc:
            if "UNIQUE" not in str(exc.orig).upper():
                raise
            logging.info(
                f"Time session with session_id {time_session.session_id} already exists, returning existing record.",
            )
            result = await conn.execute(
                select(time_sessions).where(
                    time_sessions.c.session_id == time_session.session_id,
                ),
            )
            existing = result.fetchone()
            return TimeSession(**existing._mapping)
        return time_session


async def update_time_session(time_session: TimeSession) -> TimeSession | None:
    """Update an existing time session, returns full record."""
    async with engine.begin() as conn:
        result = await conn.execute(
            update(time_sessions)
            .where(time_sessions.c.session_id == time_session.session_id)
            .values(
                player_id=time_session.player_id,
                joined_at=time_session.joined_at,
                quit_at=time_session.quit_at,
            )
            .returning(
                time_sessions.c.session_id,
                time_sessions.c.player_id,
                time_sessions.c.joined_at,
                time_sessions.c.quit_at,
            )
        )
        updated = result.fetchone()
        if not updated:
            logging.info(
                f"Time session with session_id {time_session.session_id} not found, ignoring update.",
            )
            return None
        return TimeSession(**updated._mapping)
