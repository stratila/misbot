from datetime import datetime, timezone
from enum import StrEnum
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
    player_id: UUID
    nickname: str | None
    seen: str


class QuitData(BaseModel):
    player_id: UUID
    session_id: UUID
    nickname: str | None


class JoinData(QuitData):
    message: str


class SessionStatus(StrEnum):
    OK = "ok"
    ALREADY_EXISTS = "already_exists"
    INCORRECT_ORDER = "incorrect_order"


class SentMessageStatus(BaseModel):
    channel_id: int
    success: bool
    message_id: int | None = None
    error_code: str | None = None


class ProcessedJoin(BaseModel):
    session_id: UUID
    status: SessionStatus
    sent_messages_status: list[SentMessageStatus]


class ProcessedQuit(ProcessedJoin):
    pass


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
