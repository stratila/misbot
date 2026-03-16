from telegram.ext import Application, ApplicationBuilder

from misbot.bot_helper.handlers import (
    handler_start,
    handler_create,
    handler_callback,
    handler_info,
    handler_creation_text
)
from misbot.config import TELEGRAM_BOT_TOKEN_HELPER


_bot_app_helper: Application | None = None


def get_bot_app_helper() -> Application:
    global _bot_app_helper

    if _bot_app_helper is None:
        _bot_app_helper = (
            ApplicationBuilder()
            .token(TELEGRAM_BOT_TOKEN_HELPER)
            .get_updates_pool_timeout(20)
            .build()
        )

        _bot_app_helper.add_handlers(
            (
                handler_start,
                handler_create,
                handler_callback,
                handler_info,
                handler_creation_text,
            ),
        )

    return _bot_app_helper
