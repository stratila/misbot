from telegram.ext import Application, ApplicationBuilder

from misbot.bot.handlers import (
    handler_ack_chat_member,
    handler_message_echo,
    handler_start_echo,
)
from misbot.config import get_settings

settings = get_settings()

_bot_app: Application | None = None


def get_bot_app() -> Application:
    global _bot_app

    if _bot_app is None:
        _bot_app = (
            ApplicationBuilder()
            .token(settings.telegram_bot.token.get_secret_value())
            .get_updates_pool_timeout(20)
            .build()
        )

        _bot_app.add_handlers(
            (
                handler_ack_chat_member,
                handler_start_echo,
                handler_message_echo,
            ),
        )

    return _bot_app
