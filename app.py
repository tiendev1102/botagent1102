import logging
import requests as http_requests
from flask import Flask, request, jsonify
from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, OPENROUTER_API_KEY, RENDER_EXTERNAL_URL, PORT
from ai_service import get_ai_response

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app
flask_app = Flask(__name__)

# Telegram API base URL
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(chat_id, text):
    """Gửi tin nhắn qua Telegram API"""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        resp = http_requests.post(url, json=payload, timeout=10)
        logger.info(f"send_message status: {resp.status_code}")
    except Exception as e:
        logger.error(f"Send message error: {e}")


def send_chat_action(chat_id, action="typing"):
    """Gửi trạng thái 'đang gõ...'"""
    url = f"{TELEGRAM_API}/sendChatAction"
    payload = {"chat_id": chat_id, "action": action}
    try:
        http_requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Chat action error: {e}")


def handle_start(chat_id, first_name):
    """Xử lý lệnh /start"""
    welcome_msg = (
        f"Chào anh {first_name}! 😊\n\n"
        f"Em là Agent của anh Tiến đây ạ! Em rất vui được gặp anh! 🎉\n\n"
        f"Em có thể giúp anh:\n"
        f"💬 Trò chuyện, tư vấn\n"
        f"📝 Viết lách, soạn văn bản\n"
        f"🌐 Dịch thuật\n"
        f"💡 Giải đáp thắc mắc\n"
        f"📋 Lên kế hoạch\n\n"
        f"Anh cứ nhắn tin cho em bất cứ lúc nào nha! ✨"
    )
    send_message(chat_id, welcome_msg)


def handle_text_message(chat_id, text):
    """Xử lý tin nhắn text"""
    try:
        # Hiển thị "đang gõ..."
        send_chat_action(chat_id)

        # Lấy phản hồi từ AI
        response = get_ai_response(text, chat_id)
        send_message(chat_id, response)

    except Exception as e:
        logger.error(f"Handle message error: {e}")
        send_message(chat_id, "Dạ, em xin lỗi anh 😅 Em đang gặp trục trặc nhỏ. Anh thử lại sau nha! 🙏")


@flask_app.route("/")
def index():
    """Health check endpoint"""
    return "Agent cua Tien - Bot is running! 🤖", 200


@flask_app.route("/webhook", methods=["POST"])
def webhook():
    """Nhận webhook từ Telegram"""
    try:
        data = request.get_json(force=True)
        logger.info(f"Received update: {data.get('update_id', 'unknown')}")

        # Lấy message
        message = data.get("message")
        if not message:
            return jsonify({"status": "ok"}), 200

        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        first_name = message.get("from", {}).get("first_name", "bạn")

        # Xử lý lệnh /start
        if text.startswith("/start"):
            handle_start(chat_id, first_name)
        elif text.startswith("/"):
            send_message(chat_id, "Em chưa hiểu lệnh này anh ơi 😅 Anh cứ nhắn tin bình thường cho em nha!")
        elif text:
            handle_text_message(chat_id, text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error"}), 500


@flask_app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Endpoint để cài đặt webhook (gọi 1 lần sau khi deploy)"""
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    else:
        webhook_url = f"https://{request.host}/webhook"

    try:
        url = f"{TELEGRAM_API}/setWebhook"
        response = http_requests.post(url, json={"url": webhook_url}, timeout=10)
        result = response.json()

        if result.get("ok"):
            return f"✅ Webhook set successfully to: {webhook_url}", 200
        else:
            return f"❌ Error: {result.get('description', 'Unknown error')}", 500
    except Exception as e:
        return f"❌ Error setting webhook: {e}", 500


@flask_app.route("/debug", methods=["GET"])
def debug():
    """Debug endpoint - kiểm tra trạng thái các API keys"""
    results = []

    # Check env vars
    results.append(f"TELEGRAM_BOT_TOKEN: {'SET (' + TELEGRAM_BOT_TOKEN[:10] + '...)' if TELEGRAM_BOT_TOKEN else 'NOT SET'}")
    results.append(f"GEMINI_API_KEY: {'SET (' + GEMINI_API_KEY[:8] + '...)' if GEMINI_API_KEY else 'NOT SET'}")
    results.append(f"OPENROUTER_API_KEY: {'SET (' + OPENROUTER_API_KEY[:10] + '...)' if OPENROUTER_API_KEY else 'NOT SET'}")
    results.append(f"RENDER_EXTERNAL_URL: {RENDER_EXTERNAL_URL or 'NOT SET'}")
    results.append("")

    # Test Gemini
    results.append("--- Testing Gemini API ---")
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": "Say hi"}]}]}
            resp = http_requests.post(url, json=payload, timeout=15)
            results.append(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                results.append(f"Response: {text[:100]}")
            else:
                results.append(f"Error: {resp.text[:300]}")
        except Exception as e:
            results.append(f"Exception: {e}")
    else:
        results.append("SKIPPED - no key")

    results.append("")

    # Test OpenRouter
    results.append("--- Testing OpenRouter API ---")
    if OPENROUTER_API_KEY:
        try:
            resp = http_requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemma-4-31b-it:free",
                    "messages": [{"role": "user", "content": "Say hi"}],
                    "max_tokens": 50,
                },
                timeout=30
            )
            results.append(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                results.append(f"Response: {text[:100]}")
            else:
                results.append(f"Error: {resp.text[:300]}")
        except Exception as e:
            results.append(f"Exception: {e}")
    else:
        results.append("SKIPPED - no key")

    return "<pre>" + "\n".join(results) + "</pre>", 200


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT, debug=False)
