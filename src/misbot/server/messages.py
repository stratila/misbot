from datetime import datetime, timedelta

from misbot.constans import JOIN_MSG_TEXT, QUIT_MSG_TEXT, TIMEFORMAT
from misbot.server.utils import escape_md_v2, timedelta_to_hhmmss


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
