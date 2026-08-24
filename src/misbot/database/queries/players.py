from datetime import datetime

from sqlalchemy import bindparam, insert, select, update

from misbot.database.db import engine
from misbot.database.models import players
from misbot.domain.models import UpdatePlayerModel
from misbot.server.utils import chunked


async def get_player(player_id: str):
    async with engine.begin() as conn:
        result = await conn.execute(select(players).where(players.c.id == player_id))
        player = result.fetchone()
        return dict(player._mapping) if player else None


async def upsert_player(player_id: str, nickname: str, seen: datetime):
    async with engine.begin() as conn:
        result = await conn.execute(
            update(players)
            .where(players.c.id == player_id)
            .values(seen=seen)
            .returning(players.c.id)
        )
        updated = result.fetchone()

        if not updated:
            await conn.execute(
                insert(players).values(
                    id=player_id,
                    seen=seen,
                    nickname=nickname,
                )
            )
        await conn.commit()


async def update_players(records: list[UpdatePlayerModel]):
    async with engine.begin() as conn:
        for batch in chunked(records, 100):
            await conn.execute(
                update(players).where(players.c.id == bindparam("_id")),
                [{"_id": r.player_id, "nickname": r.nickname} for r in batch],
            )
        await conn.commit()
