from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Player(BaseModel):
    name: str
    uuid: UUID


class Meta(BaseModel):
    message: Optional[str]
    session_id: UUID


class PlayerPostRequestBody(BaseModel):
    player: Player
    meta: Meta


class PlayerPlayTimeResponse(BaseModel):
    name: str
    days: int
    hours: int
    minutes: int
    seconds: int


class GetPlayerResponse(BaseModel):
    player_id: UUID = Field(alias="id")
    nickname: str | None = None
    last_seen: datetime = Field(alias="seen")
