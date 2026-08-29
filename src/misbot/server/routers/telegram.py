import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Request,
)
from fastapi.responses import JSONResponse
from telegram import Update
from telegram.ext import Application

from misbot.config import RuntimeEnvironment, get_settings

# Tag
TAG = "telegram"

# Endpoints
WEBHOOK = "/webhook"

settings = get_settings()


logger = logging.getLogger(__name__)
logger.setLevel(
    level=logging.DEBUG
    if settings.environment == RuntimeEnvironment.DEV
    else logging.INFO
)


telegram_router = APIRouter(tags=[TAG])


@telegram_router.post(WEBHOOK)
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
        logger.error(
            "X-Telegram-Bot-Api-Secret-Token header's value is wrong or missing."
        )
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    bot_app: Application = request.app.state.bot_app
    try:
        await bot_app.update_queue.put(
            Update.de_json(data=await request.json(), bot=bot_app.bot)
        )
    except Exception as exc:
        logger.error(f"Unexpected error happened on POST {WEBHOOK}", exc_info=exc)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
        )
    return JSONResponse(
        content={"status": "ok"},
        status_code=HTTPStatus.OK,
    )
