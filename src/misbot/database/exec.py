from datetime import date, datetime
from typing import Any

from sqlalchemy import insert, select, update

from misbot.database.db import engine
from misbot.database.models import channels, players, time_spent, users


async def get_user(user_id: int) -> dict[Any, Any] | None:
    async with engine.connect() as conn:
        result = await conn.execute(
            select(users).where(
                users.c.id == user_id,
            ),
        )
        user = result.fetchone()
        return dict(user._mapping) if user else None


async def create_user(user_id: int, is_admin: bool = False):
    async with engine.begin() as conn:
        values = {
            "id": user_id,
            "is_admin": is_admin,
        }
        await conn.execute(
            insert(users).values(**values),
        )
        await conn.commit()


async def update_user(user_id: int, is_admin: bool):
    async with engine.begin() as conn:
        values = {
            "is_admin": is_admin,
        }
        await conn.execute(
            update(users).where(users.c.id == user_id).values(**values),
        )
        await conn.commit()


async def get_channel(channel_id: int) -> dict[Any, Any] | None:
    async with engine.connect() as conn:
        result = await conn.execute(
            select(channels).where(
                channels.c.id == channel_id,
            ),
        )
        channel = result.fetchone()
        return dict(channel._mapping) if channel else None


async def get_channels(is_managed: bool, status: str | None = None) -> list[dict]:
    async with engine.connect() as conn:
        result = await conn.execute(
            select(channels).where(
                channels.c.is_managed == is_managed,
                channels.c.status == status,
            ),
        )
        result = result.fetchall()
        return [channel._mapping for channel in result]


async def create_channel(channel_id: int, is_managed: bool, status: str | None = None):
    async with engine.begin() as conn:
        values = {
            "id": channel_id,
            "is_managed": is_managed,
            "status": status,
        }
        await conn.execute(
            insert(channels).values(**values),
        )
        await conn.commit()


async def update_channel(channel_id: int, is_managed: bool, status: str | None = None):
    async with engine.begin() as conn:
        values = {
            "is_managed": is_managed,
            "status": status,
        }
        await conn.execute(
            update(channels).where(channels.c.id == channel_id).values(values),
        )
        await conn.commit()


async def get_player(player_id: str):
    async with engine.begin() as conn:
        result = await conn.execute(select(players).where(players.c.id == player_id))
        player = result.fetchone()
        return dict(player._mapping) if player else None


async def upsert_player(player_id: str, seen: datetime):
    async with engine.begin() as conn:
        result = await conn.execute(
            update(players)
            .where(players.c.id == player_id)
            .values(seen=seen)
            .returning(players.c.id)
        )
        updated = result.fetchone()

        if not updated:
            await conn.execute(insert(players).values(id=player_id, seen=seen))
        await conn.commit()


async def create_time_spent(player_id: str, target_date: date, duration: int):
    async with engine.begin() as conn:
        await conn.execute(
            insert(time_spent).values(
                player_id=player_id, date=target_date, duration=duration
            )
        )
        await conn.commit()
