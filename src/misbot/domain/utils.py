import logging
import re
from collections import defaultdict
from datetime import UTC, datetime

import ijson

logger = logging.getLogger(__name__)


def time_to_seconds(time_string):
    """Convert '00 h. 13 m. 31 s.' to total seconds."""
    match = re.search(r"(\d+)\s*h\.\s*(\d+)\s*m\.\s*(\d+)\s*s\.", time_string)

    if not match:
        raise ValueError(f"Invalid time format: {time_string}")

    hours, minutes, seconds = map(int, match.groups())
    return hours * 3600 + minutes * 60 + seconds


def seconds_to_time(total_seconds):
    """Convert total seconds to 'Xd Yh Zm Ws'."""
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, hours, minutes, seconds


def parse_chat_history_file(file):
    final_stat = defaultdict(lambda: defaultdict(int))

    for record in ijson.items(file, "messages.item"):
        try:
            if (
                isinstance(record.get("text"), list)
                and len(record["text"]) > 0
                and isinstance(record["text"][0], dict)
                and record["text"][0]["text"] == "Player quit!"
            ):
                nickname = record["text"][2]["text"]
                timestamp = datetime.strptime(
                    record["text"][4]["text"], "%d/%m/%Y %H:%M:%S"
                ).astimezone(UTC)
                total_seconds = time_to_seconds(record["text"][6]["text"])

                final_stat[f"{timestamp.year}-{timestamp.month}"][nickname] += (
                    total_seconds
                )
        except TypeError as exc:
            logger.error("Error on handling record", exc_info=exc)

    return final_stat


def get_human_readable_result_for_a_month(
    result_set: defaultdict, year: int, month: int
):
    playtime: defaultdict = result_set.get(f"{year}-{month}")
    if not playtime:
        return

    playtime = sorted(playtime.items(), key=lambda item: item[1], reverse=True)
    playtime = [(key, seconds_to_time(value)) for key, value in playtime]

    return playtime
