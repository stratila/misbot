import logging
import asyncio
from misbot.server.app import fastapi_app
from misbot.bot.app import get_bot_app
from misbot.server import initialize_unvicorn_fastapi_server


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def main():
    bot = get_bot_app()
    server = initialize_unvicorn_fastapi_server(fastapi_app)

    async with bot:
        await bot.start()

        async with bot.updater:
            await bot.updater.start_polling()
            await server.serve()
            await bot.updater.stop()

        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
