from uuid import UUID

from pydantic import BaseModel


class Player(BaseModel):
    name: str
    uuid: UUID


class Meta(BaseModel):
    message: str


class PlayerPostRequestBody(BaseModel):
    player: Player
    meta: Meta
