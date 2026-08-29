import json
import logging
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.responses import JSONResponse

from misbot.config import RuntimeEnvironment, get_settings
from misbot.database.queries import players as db_players
from misbot.domain.models import (
    JoinData,
    ListUpdatePlayerModel,
    ProcessedJoin,
    QuitData,
)
from misbot.domain.services import players as players_svc
from misbot.domain.services.players import (
    handle_player_join,
    handle_player_quit,
    handle_player_stat_from_json,
)
from misbot.server.auth import require_scope
from misbot.server.schemas import (
    GetPlayerResponse,
    PlayerPlayTimeResponse,
    PlayerPostRequestBody,
)

# Tag
TAG = "players"

# Endpoints
PLAYERS = "/players"
PLAYERS_PLAYERS_ID = "/{player_id}"
JOIN = "/join"
QUIT = "/quit"
UPDATE_FROM_JSON = "/update-from-json"
MONTHLY_STAT = "/monthly-stat"
SEND_STAT_FROM_JSON = "/send-stat-from-json"


# Players scopes
PLAYERS_WRITE = "players:write"
PLAYERS_READ = "players:read"

# Regexes.

Q_DATE_FMT = r"^\d{4}-(0[1-9]|1[0-2])$"

settings = get_settings()


logger = logging.getLogger(__name__)
logger.setLevel(
    level=logging.DEBUG
    if settings.environment == RuntimeEnvironment.DEV
    else logging.INFO
)


players_router = APIRouter(prefix=PLAYERS, tags=[TAG])


@players_router.get(
    MONTHLY_STAT,
    dependencies=[Depends(require_scope(PLAYERS_READ))],
    response_model=list[PlayerPlayTimeResponse],
)
async def get_monthly_stat(year: int, month: int):
    try:
        # Calls the db without a service layer.
        return await db_players.get_monthly_player_stat(year, month)
    except ValueError as e:
        logger.error("Error happened while getting player monthly stat", exc_info=e)
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error {PLAYERS + MONTHLY_STAT}", exc_info=e)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@players_router.get(
    PLAYERS_PLAYERS_ID,
    dependencies=[Depends(require_scope(PLAYERS_READ))],
    response_model=GetPlayerResponse,
    response_model_by_alias=True,
)
async def get_player(player_id: UUID):
    return await players_svc.get_player(
        player_id=player_id,
    )


@players_router.post(
    JOIN,
    dependencies=[Depends(require_scope(PLAYERS_WRITE))],
    response_model=ProcessedJoin,
)
async def post_player_join(
    player_request_body: PlayerPostRequestBody,
    request: Request,
):
    try:
        return await handle_player_join(
            bot=request.app.state.bot_app.bot,
            join_data=JoinData(
                player_id=player_request_body.player.uuid,
                session_id=player_request_body.meta.session_id,
                nickname=player_request_body.player.name,
                message=player_request_body.meta.message,
            ),
        )
    except Exception as exc:
        logger.error(f"Unexpected error in {PLAYERS + JOIN}", exc_info=exc)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@players_router.post(
    QUIT,
    dependencies=[Depends(require_scope(PLAYERS_WRITE))],
    response_model=ProcessedJoin,
)
async def post_player_quit(
    player_request_body: PlayerPostRequestBody,
    request: Request,
):
    try:
        return await handle_player_quit(
            bot=request.app.state.bot_app.bot,
            quit_data=QuitData(
                player_id=player_request_body.player.uuid,
                session_id=player_request_body.meta.session_id,
                nickname=player_request_body.player.name,
            ),
        )
    except Exception as exc:
        logger.error(f"Unexpected error in {PLAYERS + QUIT}", exc_info=exc)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@players_router.put(
    UPDATE_FROM_JSON,
    dependencies=[Depends(require_scope(PLAYERS_WRITE))],
)
async def update_players_from_json(file: UploadFile = File(...)):
    """Internal route to update the table with new columns"""
    contents = await file.read()
    try:
        decoded_contents = {"players": json.loads(contents)}
        parsed_contents = ListUpdatePlayerModel.model_validate(decoded_contents)
        # Calls the db without a service layer.
        await db_players.update_players(parsed_contents.players)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
    except Exception as e:
        logger.error(f"Unexpected error in {PLAYERS + UPDATE_FROM_JSON}", exc_info=e)
        return {"error": "Error while handling JSON"}
    return JSONResponse(content={"status": "ok"})


@players_router.post(
    SEND_STAT_FROM_JSON,
    dependencies=[Depends(require_scope(PLAYERS_WRITE))],
)
async def send_stat_from_json(
    request: Request,
    date1: Annotated[str, Query(pattern=Q_DATE_FMT)],
    date2: Annotated[str | None, Query(pattern=Q_DATE_FMT)] = None,
    file: UploadFile = File(...),
):
    """Send stored chat statistics that are missing from the database.

    Args:
        date1: Start date of the range to process, in YYYY-MM format.
        date2: Optional end date of the range to process, in YYYY-MM format.
            If omitted, only ``date1`` is processed.
        file: Upload file containing the statistics payload to send.
    """
    try:
        await handle_player_stat_from_json(
            request.app.state.bot_app.bot, file.file, date1, date2
        )
        return JSONResponse({"status": "ok"})

    except Exception as e:
        logger.error(f"Unexpected error in {PLAYERS + SEND_STAT_FROM_JSON}", exc_info=e)
        return {"error": "Error while handling JSON"}
