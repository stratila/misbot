import logging

from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ChatMemberHandler, CommandHandler, ContextTypes, MessageHandler

from misbot.config import ADMIN_USER_ID, MANAGED_CHAT_IDS
from misbot.database import exec as db


async def callback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await db.get_user(user_id=update.effective_chat.id)
    if user is None:
        logging.info(
            f"User for {update.effective_chat.id=} not found in the database, creating."
        )

        is_admin = True if str(update.effective_chat.id) == ADMIN_USER_ID else False
        await db.create_user(
            update.effective_chat.id,
            is_admin=is_admin,
        )

        text = f"Fist time here! Your role is {'admin' if is_admin else 'user'}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return

    logging.info(
        f"User for {update.effective_chat.id=} is present in the database, handling."
    )
    text = f"Weclome to misbot again! Your role is {'admin' if user and user.get('is_admin') else 'user'}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def callback_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Echo private chat: {update.message.text}",
        )
        return

    if update.channel_post:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Echo channel: {update.channel_post.text}",
        )
        return


async def callback_ack_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.effective_chat.id
    status = update.my_chat_member.new_chat_member.status

    channel = await db.get_channel(channel_id)
    if not channel:
        # In case of how ChatMemberHandler filers for `chat_id` work, channel always managed.
        await db.create_channel(channel_id=channel_id, is_managed=True)

    match status:
        case ChatMemberStatus.ADMINISTRATOR:
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
            await db.update_channel(
                channel_id=update.effective_chat.id,
                is_managed=True,
                status=status,
            )
        case _:
            return


handler_ack_chat_member = ChatMemberHandler(
    callback=callback_ack_chat_member,
    chat_id=[int(mid) for mid in MANAGED_CHAT_IDS.split(",")],
)
handler_message_echo = MessageHandler(filters=None, callback=callback_echo)
handler_start_echo = CommandHandler("start", callback_start)
