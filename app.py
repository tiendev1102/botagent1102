import os
import logging
import requests
from flask import Flask, request

# Config
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
flask_app = Flask(__name__)

# Import AI service
from ai_service import get_ai_response


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            # Fallback if Markdown fails
            payload.pop("parse_mode", None)
            requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Send message error: {e}")


@flask_app.route("/")
def home():
    return "Agent cua Tien - Bot is running with Web Search! 🤖🌐"


@flask_app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if not data:
            return "OK", 200
        message = data.get("message", {})
        if not message:
            return "OK", 200
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        if not chat_id or not text:
            return "OK", 200
            
        if text == "/start":
            welcome = """Chào anh Tiến! 😊\n\nEm là Agent của anh Tiến đây ạ! Em đã được nâng cấp thêm tính năng **Tìm kiếm Web Real-time** rồi nhé! 🎉\n\nEm có thể giúp anh:\n🔍 Tìm kiếm tin tức, thời tiết, tỷ giá mới nhất\n💬 Trò chuyện, tư vấn\n📝 Viết lách, soạn văn bản\n🌐 Dịch thuật\n💡 Giải đáp thắc mắc\n📋 Lên kế hoạch\n\nAnh cứ nhắn tin cho em bất cứ lúc nào nha! ✨"""
            send_telegram_message(chat_id, welcome)
            return "OK", 200
            
        # Gọi AI service (đã bao gồm logic search)
        response = get_ai_response(text, chat_id)
        send_telegram_message(chat_id, response)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return "OK", 200


@flask_app.route("/set_webhook")
def set_webhook():
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"✅ Webhook set successfully to: {webhook_url}"
        else:
            return f"❌ Error: {response.text}", 500
    except Exception as e:
        return f"❌ Error: {e}", 500


@flask_app.route("/debug")
def debug():
    results = []
    results.append(f"TELEGRAM_BOT_TOKEN: {'SET (' + TELEGRAM_BOT_TOKEN[:10] + '...)' if TELEGRAM_BOT_TOKEN else 'NOT SET'}")
    results.append(f"GEMINI_API_KEY: {'SET (' + GEMINI_API_KEY[:7] + '...)' if GEMINI_API_KEY else 'NOT SET'}")
    results.append(f"OPENROUTER_API_KEY: {'SET (' + OPENROUTER_API_KEY[:10] + '...)' if OPENROUTER_API_KEY else 'NOT SET'}")
    results.append(f"TAVILY_API_KEY: {'SET' if os.environ.get('TAVILY_API_KEY') else 'NOT SET'}")
    results.append(f"RENDER_EXTERNAL_URL: {RENDER_EXTERNAL_URL}")
    return "\n".join(results), 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
