import logging
from datetime import date

from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ChatMemberHandler, CommandHandler, ContextTypes, MessageHandler

from misbot.bot.messages import get_time_stats_msg
from misbot.bot.utils import get_channel_type, month_range, parse_monthly_stat_message
from misbot.config import ManagedChannelType, RuntimeEnvironment, get_settings
from misbot.constants import FIRST_MSG_TEXT, GREETING_MSG_TEXT
from misbot.database.queries import channels, players, users

settings = get_settings()


logger = logging.getLogger(__name__)
logger.setLevel(
    level=logging.DEBUG
    if settings.environment == RuntimeEnvironment.DEV
    else logging.INFO
)


async def send_monthly_stat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    regular_channels = await channels.get_channels(
        is_managed=True,
        status=ChatMemberStatus.ADMINISTRATOR,
        type=ManagedChannelType.REGULAR,
    )

    regular_channels_ids = [channel["id"] for channel in regular_channels]
    if update.effective_chat.id not in regular_channels_ids:
        return

    ym1, ym2 = parse_monthly_stat_message(update.channel_post.text)
    ym_range = list(month_range(ym1, ym2))
    logger.debug(
        f"/monthly-stat {ym_range} for {update.effective_chat.id=} {regular_channels_ids=}"
    )
    for year, month in ym_range:
        stats = await players.get_monthly_player_stat(year, month)
        month_human_readable = date(year, month, 1).strftime("%B")
        if stats:
            messages = get_time_stats_msg(year, month_human_readable, stats)
            for message in messages:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    parse_mode="MarkdownV2",
                )


async def callback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await users.get_user(user_id=update.effective_chat.id)
    if user is None:
        logging.info(
            f"User for {update.effective_chat.id=} not found in the database, creating."
        )

        is_admin = (
            True
            if update.effective_chat.id == settings.channel.admin_user_id
            else False
        )
        await users.create_user(
            update.effective_chat.id,
            is_admin=is_admin,
        )

        text = FIRST_MSG_TEXT.format(role=("admin" if is_admin else "user"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    logging.info(
        f"User for {update.effective_chat.id=} is present in the database, handling."
    )
    text = GREETING_MSG_TEXT.format(
        role=("admin" if user and user.get("is_admin") else "user")
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def callback_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug(
        f"callback_handle_message {update.to_json()} {update.effective_chat.id=} {settings.channel.all_managed_chat_ids=}"
    )
    if update.message:
        logger.debug("Handling !echo - first ret")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Echo private chat: {update.message.text}",
        )
        return

    if (
        update.channel_post
        and update.effective_chat.id in settings.channel.all_managed_chat_ids
    ):
        if (
            "!echo" in update.channel_post.text
            and update.channel_post.from_user
            and update.channel_post.from_user.id == settings.channel.admin_user_id
        ):
            logger.debug(
                f"Handling !echo by {update.channel_post.from_user.id=}, admin {settings.channel.admin_user_id}"
            )
            splitted = update.channel_post.text.split(maxsplit=1)
            text = splitted[1] if len(splitted) > 1 else "echo!"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Echo channel (authorized): {text}",
            )
            return

        if "!monthly-stat" in update.channel_post.text:
            logger.debug("Handling !monthly-stat")
            try:
                await send_monthly_stat_message(update, context)
            except Exception as e:
                logger.error("Error happened while sending monthly stat", exc_info=e)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Error happened while sending monthly stat",
                )
            return


async def callback_ack_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.effective_chat.id
    status = update.my_chat_member.new_chat_member.status
    logging.info(f"Handling callback_ack_chat_member function {channel_id=} {status=}")

    channel = await channels.get_channel(channel_id)
    if not channel:
        # In case of how ChatMemberHandler filers for `chat_id` work, channel always managed.
        logging.info(f"Channel doesn't exist, creating in the db {channel_id=}")
        channel_type = get_channel_type(channel_id=channel_id)
        if channel_type is None:
            raise Exception(
                "App's channel type is not found, double check the configuration"
            )

        await channels.create_channel(
            channel_id=channel_id,
            type=channel_type,
            is_managed=True,
        )

    match status:
        case ChatMemberStatus.ADMINISTRATOR:
            logging.info(f"Channel exists, updating in the db {channel_id=} {status=}")
            await channels.update_channel(
                channel_id=channel_id,
                is_managed=True,
                status=status,
            )
            text = f"Enabled in {update.my_chat_member.chat.title}"
            await context.bot.send_message(
                chat_id=channel_id,
                text=text,
            )
        case _:
            logging.info(f"Channel exists, updating in the db {channel_id=} {status=}")
            await channels.update_channel(
                channel_id=channel_id,
                is_managed=True,
                status=status,
            )


handler_ack_chat_member = ChatMemberHandler(
    callback=callback_ack_chat_member,
    chat_id=settings.channel.all_managed_chat_ids,
)
handler_message_echo = MessageHandler(filters=None, callback=callback_handle_message)
handler_start_echo = CommandHandler("start", callback_start)
