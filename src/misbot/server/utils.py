import re
from datetime import timedelta


def escape_md_v2(text: str) -> str:
    # Escape all Telegram MarkdownV2 special characters
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", text)


def timedelta_to_hhmmss(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02} h. {minutes:02} m. {seconds:02} s."

