from misbot.server.routers.players import players_router
from misbot.server.routers.telegram import telegram_router

ROUTERS = (telegram_router, players_router)

__all__ = ["ROUTERS", "players_router", "telegram_router"]
