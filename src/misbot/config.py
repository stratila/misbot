import os

from dotenv import load_dotenv

load_dotenv()


ENVIRONMENT = os.environ.get("ENVIRONMENT")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN")
URL_PATH = os.environ.get("URL_PATH")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")
MANAGED_CHAT_IDS = os.environ.get("MANAGED_CHAT_IDS")
SQLITE_DB_FILENAME = os.environ.get("SQLITE_DB_FILENAME")


def get_sqlite_connection_string():
    return f"sqlite+aiosqlite:///{SQLITE_DB_FILENAME}"
