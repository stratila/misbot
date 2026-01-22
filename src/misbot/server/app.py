import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from misbot.bot.app import get_bot_app
from misbot.database import exec as db
from misbot.server.schemas import PlayerJoinPostRequestBody

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot_app = get_bot_app()
    yield


fastapi_app = FastAPI(lifespan=lifespan)


@fastapi_app.get("/")
def tatus():
    return {"status": "ok"}


@fastapi_app.post("/player/join")
async def player_join(
    player_join: PlayerJoinPostRequestBody,
    request: Request,
):
    # TODO: Track time player is joining the server.

    # Construct bot message
    text = (
        f"The player {player_join.player.name} has join the server! "
        f"Their hello message on joining - {player_join.meta.join_message}"
    )

    channels = await db.get_channels(is_managed=True, status="administrator")
    for channel in channels:
        channel_id = channel["id"]
        await request.app.state.bot_app.bot.send_message(
            chat_id=channel_id,
            text=text,
        )
    return {"status": "ok"}
