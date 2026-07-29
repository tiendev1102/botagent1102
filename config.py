import os

# Telegram Bot Token (bắt buộc)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Google Gemini API Key (nguồn AI chính)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# OpenRouter API Key (nguồn AI dự phòng - miễn phí)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Render URL (tự động có khi deploy trên Render)
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

# Port cho web server
PORT = int(os.environ.get("PORT", 10000))

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Chua cai dat TELEGRAM_BOT_TOKEN")

if not GEMINI_API_KEY and not OPENROUTER_API_KEY:
    raise ValueError("Can it nhat 1 trong 2: GEMINI_API_KEY hoac OPENROUTER_API_KEY")
