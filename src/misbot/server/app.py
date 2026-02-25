import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Request
from telegram import Bot, Update
from telegram.ext import Application

from misbot.bot.app import get_bot_app
from misbot.config import WEBHOOK_SECRET_TOKEN
from misbot.constans import JOIN_MSG_TEXT, QUIT_MSG_TEXT
from misbot.database import exec as db
from misbot.server.schemas import PlayerPostRequestBody
from misbot.server.utils import escape_md_v2, timedelta_to_hhmmss


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot_app = get_bot_app()
    yield


fastapi_app = FastAPI(lifespan=lifespan)


@fastapi_app.get("/")
def tatus():
    return {"status": "ok"}


@fastapi_app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
):
    if not x_telegram_bot_api_secret_token:
        return HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET_TOKEN:
        logger.info(
            "X-Telegram-Bot-Api-Secret-Token header's value is wrong or missing."
        )
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    bot_app: Application = request.app.state.bot_app
    await bot_app.update_queue.put(
        Update.de_json(data=await request.json(), bot=bot_app.bot)
    )
    return {"status": "ok"}


@fastapi_app.post("/player/join")
async def player_join(
    player_request_body: PlayerPostRequestBody,
    request: Request,
):
    bot: Bot = request.app.state.bot_app.bot
    player_nickname = player_request_body.player.name
    player_uuid = str(player_request_body.player.uuid)
    player_message = player_request_body.meta.message
    now = datetime.now(tz=timezone.utc)

    await db.upsert_player(player_id=player_uuid, seen=now)

    text = JOIN_MSG_TEXT.format(
        action="join",
        player_nickname=escape_md_v2(player_nickname),
        timezone=escape_md_v2('(UTC)'),
        time=escape_md_v2(now.strftime('%d/%m/%Y %H:%M:%S')),
        message=escape_md_v2(player_message),
    )

    channels = await db.get_channels(is_managed=True, status="administrator")

    for channel in channels:
        channel_id = channel["id"]

        await bot.send_message(chat_id=channel_id, text=text, parse_mode="MarkdownV2")
    return {"status": "ok"}


@fastapi_app.post("/player/quit")
async def player_quit(
    player_request_body: PlayerPostRequestBody,
    request: Request,
):
    bot: Bot = request.app.state.bot_app.bot
    player_nickname = player_request_body.player.name
    player_uuid = str(player_request_body.player.uuid)
    now = datetime.now(tz=timezone.utc)

    palyer = await db.get_player(player_id=player_uuid)
    await db.upsert_player(player_id=player_uuid, seen=now)

    last_seen: datetime = palyer.get("seen")
    last_seen = last_seen.replace(tzinfo=timezone.utc)

    duration: timedelta = now - last_seen

    await db.create_time_spent(player_uuid, now.date(), duration.seconds)

    formatted_spent_time = timedelta_to_hhmmss(duration)

    text = QUIT_MSG_TEXT.format(
        action="quit",
        player_nickname=escape_md_v2(player_nickname),
        timezone=escape_md_v2('(UTC)'),
        time=escape_md_v2(now.strftime('%d/%m/%Y %H:%M:%S')),
        spent_time=escape_md_v2(formatted_spent_time),
        )

    print(text)

    channels = await db.get_channels(is_managed=True, status="administrator")

    for channel in channels:
        channel_id = channel["id"]
        await bot.send_message(chat_id=channel_id, text=text, parse_mode="MarkdownV2")

    return {"status": "ok"}
