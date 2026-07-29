import logging
import requests as http_requests
from flask import Flask, request, jsonify
from config import TELEGRAM_BOT_TOKEN, RENDER_EXTERNAL_URL, PORT
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
        http_requests.post(url, json=payload, timeout=10)
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


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT, debug=False)
