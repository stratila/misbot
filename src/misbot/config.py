import os
from dotenv import load_dotenv


load_dotenv()


ENVIRONMENT = os.environ.get("ENVIRONMENT")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN")
SSL_KEY_FILE_PATH = os.environ.get("SSL_KEY_FILE_PATH")
SSL_CERT_FILE_PATH = os.environ.get("SSL_CERT_FILE_PATH")
URL_PATH = os.environ.get("URL_PATH")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")
