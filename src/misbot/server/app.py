from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request


from misbot.bot.app import get_bot_app

from misbot.config import ADMIN_USER_ID

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
async def player_join(request: Request):
    await request.app.state.bot_app.bot.send_message(
        chat_id=ADMIN_USER_ID, text="Sending a message from POST /player/join"
    )
    return {"status": "ok"}
