import logging
from telegram import Update
from telegram.ext import ContextTypes
from gemini_service import get_gemini_response

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the command /start is issued."""
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
        f"Anh cứ nhắn tin cho em bất cứ lúc nào nha! Em luôn sẵn sàng hỗ trợ anh! ✨"
    )
    await update.message.reply_text(welcome_msg)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages using Gemini API."""
    user_message = update.message.text
    chat_id = update.effective_chat.id

    # Lấy lịch sử hội thoại từ context.user_data
    if 'history' not in context.user_data:
        context.user_data['history'] = []

    history = context.user_data['history']

    try:
        # Hiển thị "đang gõ..." trong khi chờ phản hồi
        await update.effective_chat.send_action("typing")

        gemini_response = await get_gemini_response(user_message, chat_id, history)
        await update.message.reply_text(gemini_response)

    except Exception as e:
        logger.error(f"Error getting Gemini response: {e}")
        await update.message.reply_text(
            "Dạ, em xin lỗi anh 😅 Hiện tại em đang gặp trục trặc nhỏ. "
            "Anh thử nhắn lại sau vài giây nha! 🙏"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the user."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "Dạ, em xin lỗi anh 😅 Có lỗi xảy ra rồi ạ. Anh thử lại sau nha! 🙏"
            )
    except Exception as e:
        logger.error(f"Error sending error message to user: {e}")
