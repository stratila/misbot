import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

ENVIRONMENT = os.environ.get("ENVIRONMENT")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN")
SSL_KEY_FILE_PATH = os.environ.get("SSL_KEY_FILE")
SSL_CERT_FILE_PATH = os.environ.get("SSL_CERT_FILE_PATH")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    if ENVIRONMENT == "prod":
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            secret_token=WEBHOOK_SECRET_TOKEN,
            key=SSL_KEY_FILE_PATH,
            cert=SSL_CERT_FILE_PATH,
            webhook_url=WEBHOOK_URL,
        )
    else:
        application.run_polling()
