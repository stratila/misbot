from datetime import datetime, timedelta

from misbot.bot.utils import escape_md_v2, timedelta_to_hhmmss
from misbot.constants import (
    JOIN_MSG_TEXT,
    QUIT_MSG_TEXT,
    TIME_STATS_MSG_TEXT,
    TIMEFORMAT,
)
from misbot.domain.models import PlayerPlayTime


def get_join_msg(
    player_nickname: str,
    player_message: str | None,
    timestamp: datetime,
) -> str:
    timezone_name = timestamp.tzname() if timestamp.tzinfo else "UTC"
    return JOIN_MSG_TEXT.format(
        action="join",
        player_nickname=escape_md_v2(player_nickname),
        timezone=escape_md_v2(f"({timezone_name})"),
        time=escape_md_v2(timestamp.strftime(TIMEFORMAT)),
        message=escape_md_v2(player_message or ""),
    )


def get_quit_msg(
    player_nickname: str,
    timestamp: datetime,
    duration: timedelta,
) -> str:
    timezone_name = timestamp.tzname() if timestamp.tzinfo else "UTC"
    formatted_spent_time = timedelta_to_hhmmss(duration)
    return QUIT_MSG_TEXT.format(
        action="quit",
        player_nickname=escape_md_v2(player_nickname),
        timezone=escape_md_v2(f"({timezone_name})"),
        time=escape_md_v2(timestamp.strftime(TIMEFORMAT)),
        spent_time=escape_md_v2(formatted_spent_time),
    )


def get_time_stats_msg(year: str, month: str, data: list[PlayerPlayTime]) -> str:
    players = []

    for item in data:
        nickname = escape_md_v2(item.name)

        duration = f"{item.days} days {item.hours} hours {item.minutes} minutes {item.seconds} seconds"

        players.append(f"• *{nickname}*: {escape_md_v2(duration)}")

    return TIME_STATS_MSG_TEXT.format(
        year=year,
        month=month,
        players="\n".join(players),
    )
