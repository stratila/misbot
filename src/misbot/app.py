import asyncio
import contextlib
import logging

from telegram import Update
from telegram.ext import Application
from uvicorn import Server

from misbot.bot.app import get_bot_app
from misbot.config import ENVIRONMENT, WEBHOOK_SECRET_TOKEN, WEBHOOK_URL
from misbot.database.db import engine
from misbot.server import init_uvicorn_server
from misbot.server.app import fastapi_app

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def run_polling(bot_app: Application, server: Server):
    async with bot_app.updater:
        await bot_app.updater.start_polling()
        await server.serve()
        await bot_app.updater.stop()


async def setup_webhook(bot_app: Application):
    bot_app.updater = None
    await bot_app.bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
        secret_token=WEBHOOK_SECRET_TOKEN,
    )


async def main():
    bot_app = get_bot_app()
    server = init_uvicorn_server(app=fastapi_app)

    async with bot_app:
        await bot_app.start()

        if ENVIRONMENT == "prod":
            await setup_webhook(bot_app)
            await server.serve()
        else:
            await run_polling(bot_app, server)

        with contextlib.suppress(asyncio.CancelledError):
            await bot_app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(engine.dispose())
