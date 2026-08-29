import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from misbot.bot.app import get_bot_app
from misbot.config import RuntimeEnvironment, get_settings
from misbot.database.db import engine
from misbot.server.routers import ROUTERS

settings = get_settings()


logger = logging.getLogger(__name__)
logger.setLevel(
    level=logging.DEBUG
    if settings.environment == RuntimeEnvironment.DEV
    else logging.INFO
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot_app = get_bot_app()
    yield
    await engine.dispose()


fastapi_app = FastAPI(lifespan=lifespan)


@fastapi_app.get("/")
def status():
    return JSONResponse(
        content={
            "message": "Hello from misbot!",
        },
    )


for router in ROUTERS:
    fastapi_app.include_router(router)
