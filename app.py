import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
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

# Telegram bot application (global)
bot_app = None


def get_bot_app():
    """Lấy hoặc tạo bot application"""
    global bot_app
    if bot_app is None:
        bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start_command))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        bot_app.add_error_handler(error_handler)

        # Initialize
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_app.initialize())
        loop.close()
    return bot_app


async def start_command(update: Update, context):
    """Xử lý lệnh /start"""
    user = update.effective_user
    welcome_msg = (
        f"Chào anh {user.first_name}! 😊\n\n"
        f"Em là Agent của anh Tiến đây ạ! Em rất vui được gặp anh! 🎉\n\n"
        f"Em có thể giúp anh:\n"
        f"💬 Trò chuyện, tư vấn\n"
        f"📝 Viết lách, soạn văn bản\n"
        f"🌐 Dịch thuật\n"
        f"💡 Giải đáp thắc mắc\n"
        f"📋 Lên kế hoạch\n\n"
        f"Anh cứ nhắn tin cho em bất cứ lúc nào nha! ✨"
    )
    await update.message.reply_text(welcome_msg)


async def handle_message(update: Update, context):
    """Xử lý tin nhắn text"""
    user_message = update.message.text
    chat_id = update.effective_chat.id

    try:
        # Hiển thị "đang gõ..."
        await update.effective_chat.send_action("typing")

        # Lấy phản hồi từ AI
        response = get_ai_response(user_message, chat_id)
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "Dạ, em xin lỗi anh 😅 Em đang gặp trục trặc nhỏ. Anh thử lại sau nha! 🙏"
        )


async def error_handler(update, context):
    """Xử lý lỗi"""
    logger.error(f"Error: {context.error}")


@flask_app.route("/")
def index():
    """Health check endpoint - giữ bot không bị ngủ"""
    return "Agent cua Tien - Bot is running! 🤖", 200


@flask_app.route("/webhook", methods=["POST"])
def webhook():
    """Nhận webhook từ Telegram"""
    try:
        app = get_bot_app()
        data = request.get_json(force=True)
        update = Update.de_json(data, app.bot)

        # Xử lý update bằng asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(app.process_update(update))
        loop.close()

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@flask_app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Endpoint để cài đặt webhook (gọi 1 lần sau khi deploy)"""
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    else:
        webhook_url = f"https://{request.host}/webhook"

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        loop.run_until_complete(bot.set_webhook(url=webhook_url))
        loop.close()
        return f"Webhook set to: {webhook_url}", 200
    except Exception as e:
        return f"Error setting webhook: {e}", 500


# Khởi tạo bot app khi server start
get_bot_app()
logger.info("Bot initialized successfully!")


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=PORT, debug=False)
