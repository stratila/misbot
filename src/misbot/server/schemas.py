from uuid import UUID

from pydantic import BaseModel


class Player(BaseModel):
    name: str
    uuid: UUID


class Meta(BaseModel):
    join_message: str


class PlayerJoinPostRequestBody(BaseModel):
    player: Player
    meta: Meta
