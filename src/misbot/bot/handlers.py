import logging
import random

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler

from misbot.config import ADMIN_USER_ID
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
    print(update)

    if update.message:
        logging.info(f"Handling a message {update.message}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Echoing {update.message.text}"
        )

    if update.channel_post:
        logging.info(f"Handling a channel_post {update.channel_post}")
        phrases = [
            "What kind of nonsense are you sending to machines",
            "Stop this right now",
            "My bytes got mixed up with bits",
        ]
        message = f"{random.choice(phrases)}. What is this {update.channel_post.text}?"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


handler_message_echo = MessageHandler(filters=None, callback=callback_echo)
handler_start_echo = CommandHandler("start", callback_start)
