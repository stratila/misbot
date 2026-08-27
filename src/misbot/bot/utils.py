import logging
from datetime import date

from misbot.config import ManagedChannelType, RuntimeEnvironment, get_settings

settings = get_settings()



logger = logging.getLogger(__name__)
logger.setLevel(
    level=logging.DEBUG
    if settings.environment == RuntimeEnvironment.DEV
    else logging.INFO
)


def get_channel_type(channel_id: int) -> ManagedChannelType | None:
    """This is an app's internal type"""
    for mcid in settings.channel.managed_chat_ids:
        chat_id, chat_type = mcid.rsplit("-", maxsplit=1)
        if channel_id == int(chat_id):
            return ManagedChannelType(chat_type)


def get_year_month_from_text(date_part: str) -> tuple[int, int]:
    year, month = date_part.split("-", 1)
    year, month = int(year), int(month)
    date(year, month, 1)
    return year, month


def get_year_month_rage_from_text(
    date_part_1: str, date_part_2: str
) -> tuple[tuple[int, int], tuple[int, int]]:
    year1, month1 = date_part_1.split("-", 1)
    year2, month2 = date_part_2.split("-", 1)
    year1, month1 = int(year1), int(month1)
    year2, month2 = int(year2), int(month2)
    date(year1, month1, 1)
    date(year2, month2, 1)
    if month1 > month2 or year1 > year2:
        raise ValueError("Invalid month or year range")
    return (year1, month1), (year2, month2)


def parse_monthly_stat_message(
    text: str,
) -> tuple[tuple[int, int], tuple[int, int] | None]:
    parts = text.split(maxsplit=2)
    if len(parts) == 2:
        return get_year_month_from_text(parts[1]), None
    if len(parts) == 3:
        return get_year_month_rage_from_text(parts[1], parts[2])
    raise ValueError("Invalid format")


def month_range(start, end):
    sy, sm = start

    if end is None:
        yield start
        return

    ey, em = end

    start_i = sy * 12 + (sm - 1)
    end_i = ey * 12 + (em - 1)

    for i in range(start_i, end_i + 1):
        yield i // 12, i % 12 + 1


