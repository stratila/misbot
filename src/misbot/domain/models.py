from datetime import datetime, timezone
from typing import Optional
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


class Player(BaseModel):
    id: UUID
    nickname: Optional[str]
