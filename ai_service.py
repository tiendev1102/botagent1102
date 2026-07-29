import logging
import requests
from config import GEMINI_API_KEY, OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

# System prompt cho bot
SYSTEM_PROMPT = """Bạn là "Agent của Tiến", một trợ lý AI trên Telegram. Hãy tuân thủ các quy tắc sau:

1. Xưng hô: Luôn xưng "em", gọi người dùng là "anh".
2. Phong cách: Cute, thân thiện, nhiệt tình, hỗ trợ tận tình. Dùng emoji phù hợp 😊
3. Ngôn ngữ: Trả lời bằng tiếng Việt là chính. Nếu anh hỏi bằng ngôn ngữ khác thì trả lời bằng ngôn ngữ đó.
4. Vai trò: Em là trợ lý đa năng - giúp công việc, học tập, giải trí, tư vấn, dịch thuật, viết lách, lên kế hoạch.
5. Luôn sẵn sàng và vui vẻ khi được nhờ giúp đỡ.
6. Trả lời ngắn gọn, dễ hiểu, không dài dòng trừ khi được yêu cầu giải thích chi tiết.
"""

# Lưu lịch sử hội thoại (trong RAM)
conversation_history = {}
MAX_HISTORY = 20


def get_history(chat_id):
    """Lấy lịch sử hội thoại của một chat"""
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    return conversation_history[chat_id]


def add_to_history(chat_id, role, content):
    """Thêm tin nhắn vào lịch sử"""
    history = get_history(chat_id)
    history.append({"role": role, "content": content})
    # Giới hạn lịch sử
    if len(history) > MAX_HISTORY:
        conversation_history[chat_id] = history[-MAX_HISTORY:]


def call_gemini(user_message, chat_id):
    """Gọi Google Gemini API bằng REST API trực tiếp"""
    if not GEMINI_API_KEY:
        return None

    try:
        history = get_history(chat_id)

        # Tạo contents cho Gemini API
        contents = []

        # Thêm lịch sử hội thoại
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        # Thêm tin nhắn hiện tại
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        # Gọi Gemini API trực tiếp qua REST
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "maxOutputTokens": 1000,
                "temperature": 0.8
            }
        }

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None


def call_openrouter(user_message, chat_id):
    """Gọi OpenRouter API (miễn phí, dự phòng)"""
    if not OPENROUTER_API_KEY:
        return None

    try:
        history = get_history(chat_id)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "google/gemma-4-31b-it:free",
                "messages": messages,
                "max_tokens": 1000,
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenRouter error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        return None


def get_ai_response(user_message, chat_id):
    """Lấy phản hồi AI - thử Gemini trước, nếu lỗi thì dùng OpenRouter"""

    # Thử Gemini trước (nguồn chính)
    response = call_gemini(user_message, chat_id)

    # Nếu Gemini lỗi, dùng OpenRouter (dự phòng)
    if response is None:
        logger.info("Gemini failed, switching to OpenRouter...")
        response = call_openrouter(user_message, chat_id)

    # Nếu cả 2 đều lỗi
    if response is None:
        response = "Dạ, em xin lỗi anh 😅 Hiện tại cả 2 nguồn AI đều đang gặp trục trặc. Anh thử lại sau vài phút nha! 🙏"

    # Lưu vào lịch sử
    add_to_history(chat_id, "user", user_message)
    add_to_history(chat_id, "assistant", response)

    return response
