import logging
from datetime import date, datetime

from sqlalchemy import Integer, bindparam, case, cast, func, insert, select, update
from sqlalchemy.dialects import sqlite

from misbot.config import RuntimeEnvironment, get_settings
from misbot.database.db import engine
from misbot.database.models import players, time_sessions
from misbot.domain.models import PlayerPlayTime, UpdatePlayerModel
from misbot.server.utils import chunked

settings = get_settings()

logger = logging.getLogger(__name__)
logger.setLevel(
    level=logging.DEBUG
    if settings.environment == RuntimeEnvironment.DEV
    else logging.INFO
)


# 24 hours in seconds
_24H = 86400


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


async def get_monthly_player_stat(year: int, month: int) -> list[PlayerPlayTime]:
    try:
        date(year, month, 1)
        year = str(year)
        month = str(month) if month > 10 else "0" + str(month)
    except ValueError:
        raise ValueError("Invalid year/month: {e}")

    anchor = (
        select(
            time_sessions.c.session_id.label("session_id"),
            time_sessions.c.player_id.label("player_id"),
            time_sessions.c.joined_at.label("start_date"),
            time_sessions.c.quit_at.label("end_date"),
            func.datetime(time_sessions.c.joined_at, "start of day").label(
                "delta_date"
            ),
            case(
                (
                    func.date(time_sessions.c.joined_at)
                    == func.date(time_sessions.c.quit_at),
                    func.round(
                        (
                            func.julianday(time_sessions.c.quit_at)
                            - func.julianday(time_sessions.c.joined_at)
                        )
                        * _24H,
                        0,
                    ),
                ),
                (
                    func.date(time_sessions.c.joined_at, "+1 day")
                    <= func.date(time_sessions.c.quit_at),
                    func.round(
                        (
                            func.julianday(
                                func.datetime(
                                    time_sessions.c.joined_at, "+1 day", "start of day"
                                )
                            )
                            - func.julianday(time_sessions.c.joined_at)
                        )
                        * _24H,
                        0,
                    ),
                ),
            ).label("duration"),
        )
        .where(time_sessions.c.joined_at.isnot(None))
        .where(time_sessions.c.quit_at.isnot(None))
        .cte(name="dates", recursive=True)
    )

    # self-reference of the anchor to be used in the recursive part
    d = anchor.alias()

    recursive = select(
        d.c.session_id,
        d.c.player_id,
        d.c.start_date,
        d.c.end_date,
        func.datetime(d.c.delta_date, "+1 day").label("delta_date"),
        case(
            (
                func.date(d.c.delta_date, "+1 day") < func.date(d.c.end_date),
                func.round(
                    (
                        func.julianday(
                            func.datetime(d.c.delta_date, "+1 day", "start of day")
                        )
                        - func.julianday(func.datetime(d.c.delta_date, "start of day"))
                    )
                    * _24H,
                    0,
                ),
            ),
            (
                func.date(d.c.delta_date, "+1 day") == func.date(d.c.end_date),
                func.round(
                    (
                        func.julianday(d.c.end_date)
                        - func.julianday(
                            func.datetime(d.c.delta_date, "+1 day", "start of day")
                        )
                    )
                    * _24H,
                    0,
                ),
            ),
        ).label("duration"),
    ).where(func.date(d.c.delta_date, "+1 day") < d.c.end_date)

    dates_cte = anchor.union_all(recursive)

    total_duration = func.sum(dates_cte.c.duration).label("total_duration")

    main_qry = (
        select(
            func.coalesce(
                players.c.nickname,
                dates_cte.c.player_id,
            ).label("name"),
            cast(total_duration / _24H, Integer).label("days"),
            cast((total_duration % _24H) / 3600, Integer).label("hours"),
            cast((total_duration % 3600) / 60, Integer).label("minutes"),
            cast(total_duration % 60, Integer).label("seconds"),
        )
        .join_from(
            dates_cte,
            players,
            dates_cte.c.player_id == players.c.id,
        )
        .where(func.strftime("%Y-%m", dates_cte.c.start_date) == f"{year}-{month}")
        .group_by(dates_cte.c.player_id, players.c.nickname)
        .order_by(total_duration.desc())
    )

    if settings.environment == RuntimeEnvironment.DEV:
        logger.debug(
            main_qry.compile(
                dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True}
            ).__str__()
        )

    monthly_play_time = []
    async with engine.begin() as conn:
        result = await conn.execute(main_qry)
        for row in result.fetchall():
            monthly_play_time.append(PlayerPlayTime(**row._mapping))

    return monthly_play_time
