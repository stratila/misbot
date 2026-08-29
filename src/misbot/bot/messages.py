from datetime import datetime, timedelta

from misbot.bot.utils import escape_md_v2, timedelta_to_hhmmss
from misbot.constants import (
    JOIN_MSG_TEXT,
    QUIT_MSG_TEXT,
    TIME_STATS_MSG_TEXT,
    TIMEFORMAT,
)
from misbot.domain.models import PlayerPlayTime
from telegram.constants import MessageLimit


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


def get_time_stats_msg(year: str, month: str, data: list[PlayerPlayTime]) -> list[str]:
    """
    Generate time statistics messages, splitting into multiple messages if needed.
    Returns a list of message strings, each ≤ 4096 characters.
    """
    messages = []
    current_players = []
    current_length = 0

    # Calculate header length once
    header = TIME_STATS_MSG_TEXT.format(year=year, month=month)
    header_length = len(header)

    for item in data:
        nickname = escape_md_v2(item.name)
        duration = f"{item.days} days {item.hours} hours {item.minutes} minutes {item.seconds} seconds"
        player_line = f"• *{nickname}*: {escape_md_v2(duration)}\n"
        player_length = len(player_line)

        # Check if adding this player would exceed limit
        # Account for header + current content + new player + newline between players
        needed_length = header_length + current_length + player_length

        if current_players and needed_length > MessageLimit.MAX_TEXT_LENGTH:
            # Save current message and start a new one
            message_content = "\n".join(current_players)
            messages.append(header + message_content)
            current_players = []
            current_length = 0

        current_players.append(player_line.rstrip("\n"))
        current_length += player_length

    # Add the last message
    if current_players:
        message_content = "\n".join(current_players)
        messages.append(header + message_content)

    return messages
