import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from telegram import Bot, Update
from telegram.ext import Application

from misbot.bot.app import get_bot_app
from misbot.config import get_settings, ManagedChannelType
from misbot.database.queries import channels as db_channels
from misbot.database.queries import players as db_players
from misbot.database.queries.time_sessions import (
    create_time_session,
    get_time_session,
    update_time_session,
)
from misbot.domain.models import ListUpdatePlayerModel, TimeSession
from misbot.server.auth import require_scope
from misbot.bot.messages import get_join_msg, get_quit_msg
from misbot.server.schemas import PlayerPlayTimeResponse, PlayerPostRequestBody

from telegram.constants import ChatMemberStatus

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot_app = get_bot_app()
    yield


fastapi_app = FastAPI(lifespan=lifespan)


@fastapi_app.get("/")
def status():
    return {"status": "ok"}


@fastapi_app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
):
    if not x_telegram_bot_api_secret_token:
        return HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    if (
        x_telegram_bot_api_secret_token
        != settings.telegram_bot.webhook_secret_token.get_secret_value()
    ):
        logger.info(
            "X-Telegram-Bot-Api-Secret-Token header's value is wrong or missing."
        )
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    bot_app: Application = request.app.state.bot_app
    await bot_app.update_queue.put(
        Update.de_json(data=await request.json(), bot=bot_app.bot)
    )
    return {"status": "ok"}


@fastapi_app.post(
    "/player/join",
    dependencies=[Depends(require_scope("player:write"))],
)
async def player_join(
    player_request_body: PlayerPostRequestBody,
    request: Request,
):
    bot: Bot = request.app.state.bot_app.bot
    now = datetime.now(tz=timezone.utc)
    channels = await db_channels.get_channels(
        is_managed=True,
        status=ChatMemberStatus.ADMINISTRATOR,
        type=ManagedChannelType.LOGGER,
    )

    # Update player's last seen time or create a new player if it doesn't exist.
    await db_players.upsert_player(
        player_id=player_request_body.player.uuid,
        nickname=player_request_body.player.name,
        seen=now,
    )

    session: TimeSession | None = await get_time_session(
        player_request_body.meta.session_id
    )

    # Handle already exists
    if session and session.joined_at is not None:
        logger.info(
            "Session already exists and has joined_at. No need to create a new session."
        )
        return {"status": "ok"}

    # Handle incorrect order.
    if session and session.quit_at is not None:
        joined_at = now
        duration = joined_at - session.quit_at
        if duration.total_seconds() > 0:
            logger.info(
                f"Session has quit_at but {joined_at=} is after {session.quit_at=}. This is an incorrect order."
                "Setting duration to 0.",
            )
            joined_at = session.quit_at
            duration = timedelta()

        session: TimeSession | None = await update_time_session(
            session.model_copy(update={"joined_at": joined_at})
        )
        if session is None:
            logger.error("update_time_session returned None after join update.")
            return {"status": "ok"}

        for channel in channels:
            await bot.send_message(
                chat_id=channel["id"],
                text=get_join_msg(
                    player_nickname=player_request_body.player.name,
                    player_message=player_request_body.meta.message,
                    timestamp=session.joined_at,
                ),
                parse_mode="MarkdownV2",
            )

            await bot.send_message(
                chat_id=channel["id"],
                text=get_quit_msg(
                    player_nickname=player_request_body.player.name,
                    timestamp=session.quit_at,
                    duration=duration,
                ),
                parse_mode="MarkdownV2",
            )
        return {"status": "ok"}

    # Handle normal case.
    if not session:
        session = await create_time_session(
            TimeSession(
                session_id=player_request_body.meta.session_id,
                player_id=player_request_body.player.uuid,
                joined_at=now,
            )
        )
        if session is None:
            logger.error("create_time_session returned None after join.")
            return {"status": "ok"}
        for channel in channels:
            await bot.send_message(
                chat_id=channel["id"],
                text=get_join_msg(
                    player_nickname=player_request_body.player.name,
                    player_message=player_request_body.meta.message,
                    timestamp=session.joined_at,
                ),
                parse_mode="MarkdownV2",
            )

    return {"status": "ok"}


@fastapi_app.post(
    "/player/quit",
    dependencies=[Depends(require_scope("player:write"))],
)
async def player_quit(
    player_request_body: PlayerPostRequestBody,
    request: Request,
):
    bot: Bot = request.app.state.bot_app.bot
    now = datetime.now(tz=timezone.utc)
    channels = await db_channels.get_channels(
        is_managed=True,
        status=ChatMemberStatus.ADMINISTRATOR,
        type=ManagedChannelType.LOGGER,
    )

    session: TimeSession | None = await get_time_session(
        player_request_body.meta.session_id
    )

    # Handle already exists
    if session and session.quit_at is not None:
        logger.info(
            "Session already exists and has quit_at. No need to update the session."
        )
        return {"status": "ok"}

    # Handle incorrect order.
    if not session:
        session = await create_time_session(
            TimeSession(
                session_id=player_request_body.meta.session_id,
                player_id=player_request_body.player.uuid,
                joined_at=None,
                quit_at=now,
            )
        )
        if session is None:
            logger.error("create_time_session returned None after quit.")
            return {"status": "ok"}
        logger.info(
            "Session doesn't exist but quit_at is provided. Created a new session with quit_at and without joined_at."
        )
        return {"status": "ok"}

    # Handle normal case.
    if session.joined_at is not None:
        session: TimeSession | None = await update_time_session(
            session.model_copy(update={"quit_at": now})
        )
        if session is None:
            logger.error("update_time_session returned None after quit update.")
            return {"status": "ok"}
        for channel in channels:
            await bot.send_message(
                chat_id=channel["id"],
                text=get_quit_msg(
                    player_nickname=player_request_body.player.name,
                    timestamp=session.quit_at,
                    duration=session.quit_at - session.joined_at,
                ),
                parse_mode="MarkdownV2",
            )

    return {"status": "ok"}


@fastapi_app.put(
    "/players/update-from-json",
    dependencies=[Depends(require_scope("player:write"))],
)
async def update_players(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        decoded_contents = {"players": json.loads(contents)}
        parsed_contents = ListUpdatePlayerModel.model_validate(decoded_contents)
        await db_players.update_players(parsed_contents.players)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
    except Exception as e:
        logger.error("Handling JSON error", exc_info=e)
        return {"error": "Error while handling JSON"}
    return {"status": "ok"}


@fastapi_app.get(
    "/player/monthly-stat",
    dependencies=[Depends(require_scope("player:read"))],
    response_model=list[PlayerPlayTimeResponse],
)
async def get_monthly_stat(year: int, month: int):
    try:
        return await db_players.get_monthly_player_stat(year, month)
    except ValueError as e:
        logger.error("Error happened while getting player monthly stat", exc_info=e)
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.error("Unexpected error", exc_info=e)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
