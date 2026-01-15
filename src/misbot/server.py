import os
import logging
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)
from dotenv import load_dotenv

load_dotenv()


ENVIRONMENT = os.environ.get("ENVIRONMENT")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN")
SSL_KEY_FILE_PATH = os.environ.get("SSL_KEY_FILE_PATH")
SSL_CERT_FILE_PATH = os.environ.get("SSL_CERT_FILE_PATH")
URL_PATH = os.environ.get("URL_PATH")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Handling command /start")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    message_handler = MessageHandler(filters=None, callback=echo)
    application.add_handler(start_handler)
    application.add_handler(message_handler)

    if ENVIRONMENT == "prod":
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path=URL_PATH,
            secret_token=WEBHOOK_SECRET_TOKEN,
            key=SSL_KEY_FILE_PATH,
            webhook_url=WEBHOOK_URL,
        )
    else:
        application.run_polling()
