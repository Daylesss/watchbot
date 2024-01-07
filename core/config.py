from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
SECRET = os.environ.get("SECRET")
BOT_TOKEN= os.environ.get("BOT_TOKEN")
ADMIN = os.environ.get("ADMIN")
CHANNEL = os.environ.get("CHANNEL")
BOT_LINK = os.environ.get("BOT_LINK")
WEBHOOK = os.environ.get("WEBHOOK")
