import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

ENVIRONMENT = os.environ.get("ENVIRONMENT")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    if ENVIRONMENT == "prod":
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            secret_token="ASecretTokenIHaveChangedByNow",
            key="private.key",
            cert="cert.pem",
            webhook_url="https://example.com:8443",
        )
    else:
        application.run_polling()
