from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Player(BaseModel):
    name: str
    uuid: UUID


class Meta(BaseModel):
    message: Optional[str]


class PlayerPostRequestBody(BaseModel):
    player: Player
    meta: Meta
