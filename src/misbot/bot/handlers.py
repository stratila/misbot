import logging

from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ChatMemberHandler, CommandHandler, ContextTypes, MessageHandler

from misbot.config import get_settings
from misbot.constans import FIRST_MSG_TEXT, GREETING_MSG_TEXT
from misbot.database import exec as db

settings = get_settings()


async def callback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await db.get_user(user_id=update.effective_chat.id)
    if user is None:
        logging.info(
            f"User for {update.effective_chat.id=} not found in the database, creating."
        )

        is_admin = (
            True
            if update.effective_chat.id == settings.channel.admin_user_id
            else False
        )
        await db.create_user(
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


async def callback_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Echo private chat: {update.message.text}",
        )
        return

    if (
        update.channel_post
        and update.channel_post.from_user
        and update.channel_post.from_user.id == settings.channel.admin_user_id
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Echo channel (authorized): {update.channel_post.text}",
        )
        return


async def callback_ack_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.effective_chat.id
    status = update.my_chat_member.new_chat_member.status
    logging.info(f"Handling callback_ack_chat_member function {channel_id=} {status=}")

    channel = await db.get_channel(channel_id)
    if not channel:
        # In case of how ChatMemberHandler filers for `chat_id` work, channel always managed.
        logging.info(f"Channel doesn't exist, creating in the db {channel_id=}")
        await db.create_channel(channel_id=channel_id, is_managed=True)

    match status:
        case ChatMemberStatus.ADMINISTRATOR:
            logging.info(f"Channel exists, updating in the db {channel_id=} {status=}")
            await db.update_channel(
                channel_id=channel_id,
                is_managed=True,
                status=status,
            )
            text = f"Enabled in {update.my_chat_member.chat.title}"
            await context.bot.send_message(
                chat_id=channel_id,
                text=text,
            )
        case ChatMemberStatus.LEFT:
            logging.info(f"Channel exists, updating in the db {channel_id=} {status=}")
            await db.update_channel(
                channel_id=update.effective_chat.id,
                is_managed=True,
                status=status,
            )
        case _:
            return


handler_ack_chat_member = ChatMemberHandler(
    callback=callback_ack_chat_member,
    chat_id=settings.channel.managed_chat_ids,
)
handler_message_echo = MessageHandler(filters=None, callback=callback_echo)
handler_start_echo = CommandHandler("start", callback_start)
