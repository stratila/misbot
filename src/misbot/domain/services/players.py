import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from telegram import Bot
from telegram.constants import ChatMemberStatus
from telegram.error import TelegramError

from misbot.bot.messages import get_join_msg, get_quit_msg
from misbot.config import ManagedChannelType, get_settings
from misbot.database.queries import channels as db_channels
from misbot.database.queries import players as db_players
from misbot.database.queries import players as players_db
from misbot.database.queries.time_sessions import (
    create_time_session,
    get_time_session,
    update_time_session,
)
from misbot.domain.models import (
    JoinData,
    ProcessedJoin,
    ProcessedQuit,
    QuitData,
    SentMessageStatus,
    SessionStatus,
    TimeSession,
)


async def get_player(player_id: UUID) -> dict:
    return await players_db.get_player(player_id=player_id)


logger = logging.getLogger(__name__)

settings = get_settings()


async def send_join_message_incorrect_order(
    bot: Bot,
    join_data: JoinData,
    session: TimeSession,
    duration: timedelta,
):
    channels = await db_channels.get_channels(
        is_managed=True,
        status=ChatMemberStatus.ADMINISTRATOR,
        type=ManagedChannelType.LOGGER,
    )

    result = []

    # Send two messages
    for channel in channels:
        for msg in [
            get_join_msg(
                player_nickname=join_data.nickname,
                player_message=join_data.message,
                timestamp=session.joined_at,
            ),
            get_quit_msg(
                player_nickname=join_data.nickname,
                timestamp=session.quit_at,
                duration=duration,
            ),
        ]:
            try:
                msg = await bot.send_message(
                    chat_id=channel["id"],
                    text=msg,
                    parse_mode="MarkdownV2",
                )
                result.append(
                    SentMessageStatus(
                        channel_id=channel["id"],
                        success=True,
                        message_id=msg.message_id,
                    )
                )

            except TelegramError as e:
                logger.error(
                    "Error on sending incorrect order join message", exc_info=e
                )
                result.append(
                    SentMessageStatus(
                        channel_id=channel["id"], success=False, error_code=e.message
                    )
                )
            except ValueError as e:
                logger.error(
                    "Error on sending incorrect order join message", exc_info=e
                )
                result.append(
                    SentMessageStatus(
                        channel_id=channel["id"], success=False, error_code=str(e)
                    )
                )

    return result


async def send_join_message(
    bot: Bot,
    join_data: JoinData,
    session: TimeSession,
):
    channels = await db_channels.get_channels(
        is_managed=True,
        status=ChatMemberStatus.ADMINISTRATOR,
        type=ManagedChannelType.LOGGER,
    )

    result = []

    for channel in channels:
        try:
            msg = await bot.send_message(
                chat_id=channel["id"],
                text=get_join_msg(
                    player_nickname=join_data.nickname,
                    player_message=join_data.message,
                    timestamp=session.joined_at,
                ),
                parse_mode="MarkdownV2",
            )
            result.append(
                SentMessageStatus(
                    channel_id=channel["id"],
                    success=True,
                    message_id=msg.message_id,
                )
            )
        except TelegramError as e:
            logger.error("Error on sending join message", exc_info=e)
            result.append(
                SentMessageStatus(
                    channel_id=channel["id"], success=False, error_code=e.message
                )
            )
        except ValueError as e:
            logger.error("Error on sending join message", exc_info=e)
            result.append(
                SentMessageStatus(
                    channel_id=channel["id"], success=False, error_code=str(e)
                )
            )
    return result


async def send_quit_message(
    bot: Bot,
    quit_data: QuitData,
    session: TimeSession,
):
    channels = await db_channels.get_channels(
        is_managed=True,
        status=ChatMemberStatus.ADMINISTRATOR,
        type=ManagedChannelType.LOGGER,
    )

    result = []

    for channel in channels:
        try:
            msg = await bot.send_message(
                chat_id=channel["id"],
                text=get_quit_msg(
                    player_nickname=quit_data.nickname,
                    timestamp=session.quit_at,
                    duration=session.quit_at - session.joined_at,
                ),
                parse_mode="MarkdownV2",
            )
            result.append(
                SentMessageStatus(
                    channel_id=channel["id"],
                    success=True,
                    message_id=msg.message_id,
                )
            )
        except TelegramError as e:
            logger.error("Error on sending quit message", exc_info=e)
            result.append(
                SentMessageStatus(
                    channel_id=channel["id"], success=False, error_code=e.message
                )
            )
        except ValueError as e:
            logger.error("Error on sending quit message", exc_info=e)
            result.append(
                SentMessageStatus(
                    channel_id=channel["id"], success=False, error_code=str(e)
                )
            )
    return result


async def handle_player_join(bot: Bot, join_data: JoinData) -> ProcessedJoin:
    now = datetime.now(tz=timezone.utc)

    # Update player's last seen time or create a new player if it doesn't exist.
    await db_players.upsert_player(
        player_id=join_data.player_id,
        nickname=join_data.nickname,
        seen=now,
    )

    session: TimeSession | None = await get_time_session(join_data.session_id)

    # Handle already exists
    if session and session.joined_at is not None:
        return ProcessedJoin(
            session_id=session.session_id,
            status=SessionStatus.ALREADY_EXISTS,
            sent_messages_status=[],
        )

    # Handle incorrect order.
    if session and session.quit_at is not None:
        joined_at = now
        duration = joined_at - session.quit_at
        if duration.total_seconds() > 0:
            logger.info(
                f"Session has quit_at but {joined_at=} is after {session.quit_at=}. This is an incorrect order."
                "Setting duration to 0.",
            )
            joined_at = session.quit_at
            duration = timedelta()

        session: TimeSession | None = await update_time_session(
            session.model_copy(update={"joined_at": joined_at})
        )

        messages_status = await send_join_message_incorrect_order(
            bot, join_data, session, duration
        )
        return ProcessedJoin(
            session_id=session.session_id,
            status=SessionStatus.INCORRECT_ORDER,
            sent_messages_status=messages_status,
        )

    # Handle normal case
    session = await create_time_session(
        TimeSession(
            session_id=join_data.session_id,
            player_id=join_data.player_id,
            joined_at=now,
        )
    )
    messages_status = await send_join_message(bot, join_data, session)

    return ProcessedJoin(
        session_id=session.session_id,
        status=SessionStatus.OK,
        sent_messages_status=messages_status,
    )


async def handle_player_quit(bot: Bot, quit_data: QuitData) -> ProcessedJoin:
    now = datetime.now(tz=timezone.utc)

    session: TimeSession | None = await get_time_session(quit_data.session_id)

    # Handle already exists
    if session and session.quit_at is not None:
        logger.info(
            "Session already exists and has quit_at. No need to update the session."
        )
        return ProcessedQuit(
            session_id=session.session_id,
            status=SessionStatus.ALREADY_EXISTS,
            sent_messages_status=[],
        )

    # Handle incorrect order.
    if not session:
        session = await create_time_session(
            TimeSession(
                session_id=quit_data.session_id,
                player_id=quit_data.player_id,
                joined_at=None,
                quit_at=now,
            )
        )
        logger.info(
            "Session doesn't exist but quit_at is provided. Created a new session with quit_at and without joined_at."
        )
        return ProcessedQuit(
            session_id=session.session_id,
            status=SessionStatus.INCORRECT_ORDER,
            sent_messages_status=[],
        )

    session: TimeSession | None = await update_time_session(
        session.model_copy(update={"quit_at": now})
    )

    messages_status = await send_quit_message(bot, quit_data, session)

    return ProcessedQuit(
        session_id=session.session_id,
        status=SessionStatus.OK,
        sent_messages_status=messages_status,
    )
