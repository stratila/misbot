from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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
