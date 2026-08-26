from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel


class TimeSession(BaseModel):
    session_id: UUID
    player_id: UUID
    joined_at: datetime | None = None
    quit_at: datetime | None = None

    def __init__(self, **data):
        for field in ("joined_at", "quit_at"):
            dt = data.get(field)
            if dt is not None and dt.tzinfo is None:
                data[field] = dt.replace(tzinfo=timezone.utc)
        super().__init__(**data)


class UpdatePlayerModel(BaseModel):
    player_id: UUID
    nickname: str


class ListUpdatePlayerModel(BaseModel):
    players: list[UpdatePlayerModel]


class PlayerPlayTime(BaseModel):
    name: str
    days: int
    hours: int
    minutes: int
    seconds: int
