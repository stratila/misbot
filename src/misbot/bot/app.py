from telegram.ext import Application, ApplicationBuilder

from misbot.config import TELEGRAM_BOT_TOKEN

from misbot.bot.handlers import handler_start_echo, handler_message_echo

_bot_app: Application | None = None


def get_bot_app() -> Application:
    global _bot_app

    if _bot_app is None:
        _bot_app = (
            ApplicationBuilder()
            .token(TELEGRAM_BOT_TOKEN)
            .get_updates_pool_timeout(20)
            .build()
        )

        _bot_app.add_handlers(
            (
                handler_start_echo,
                handler_message_echo,
            ),
        )

    return _bot_app
