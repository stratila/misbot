import asyncio
import logging

from misbot.bot.app import get_bot_app
from misbot.database.db import engine
from misbot.server import init_uvicorn_server
from misbot.server.app import fastapi_app

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def main():
    bot = get_bot_app()
    server = init_uvicorn_server(app=fastapi_app)

    async with bot:
        await bot.start()

        async with bot.updater:
            await bot.updater.start_polling()
            await server.serve()
            await bot.updater.stop()

        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(engine.dispose())
