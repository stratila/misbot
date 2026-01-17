import logging
import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler


async def callback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Handling command /start")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def callback_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Echo {update.effective_chat.id=}")
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
