from datetime import datetime, timedelta

from misbot.constans import (
    JOIN_MSG_TEXT,
    PLAYERS_ONLINE_TEXT,
    QUIT_MSG_TEXT,
    TIMEFORMAT,
)
from misbot.domain.models import Player
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


def get_players_online_msg(players: list[Player], server_address: str):
    server_address = escape_md_v2(server_address)
    players_count = len(players)
    formatted_players_list = "\n".join(
        [f"_{escape_md_v2(player.nickname or player.id)}_" for player in players]
    )
    return PLAYERS_ONLINE_TEXT.format(
        server_address=server_address,
        players_count=players_count,
        players_list=formatted_players_list,
    )
