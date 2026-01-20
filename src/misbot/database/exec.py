from typing import Any

from sqlalchemy import insert, select, update

from misbot.database.db import engine
from misbot.database.models import channels, users


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
            select(users).where(
                channels.c.id == channel_id,
            ),
        )
        user = result.fetchone()
        return dict(user._mapping) if user else None


async def create_channel(channel_id, is_managed):
    async with engine.begin() as conn:
        values = {
            "id": channel_id,
            "is_managed": is_managed,
        }
        await conn.execute(
            insert(channels).values(**values),
        )
        await conn.commit()


async def update_channel(user_id: int, is_managed: bool):
    async with engine.begin() as conn:
        values = {
            "is_managed": is_managed,
        }
        await conn.execute(
            update(users).where(channels.c.id == user_id).values(**values),
        )
        await conn.commit()
