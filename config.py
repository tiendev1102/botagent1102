import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Chua cai dat bien moi truong TELEGRAM_BOT_TOKEN")

if not GEMINI_API_KEY:
    raise ValueError("Chua cai dat bien moi truong GEMINI_API_KEY")
