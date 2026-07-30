import logging
import requests
import os
from config import GEMINI_API_KEY, OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# System prompt cho bot
SYSTEM_PROMPT = """Bạn là "Agent của Tiến", một trợ lý AI trên Telegram. Hãy tuân thủ các quy tắc sau:
1. Xưng hô: Luôn xưng "em", gọi người dùng là "anh".
2. Phong cách: Cute, thân thiện, nhiệt tình, hỗ trợ tận tình. Dùng emoji phù hợp 😊
3. Ngôn ngữ: Trả lời bằng tiếng Việt là chính. Nếu anh hỏi bằng ngôn ngữ khác thì trả lời bằng ngôn ngữ đó.
4. Vai trò: Em là trợ lý đa năng - giúp công việc, học tập, giải trí, tư vấn, dịch thuật, viết lách, lên kế hoạch.
5. Luôn sẵn sàng và vui vẻ khi được nhờ giúp đỡ.
6. Trả lời ngắn gọn, dễ hiểu, không dài dòng trừ khi được yêu cầu giải thích chi tiết.
"""

# Danh sách model miễn phí trên OpenRouter (thử lần lượt nếu model trước bị rate-limit)
FREE_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
]

# Lưu lịch sử hội thoại trong RAM (backup khi không có Supabase)
conversation_history = {}
MAX_HISTORY = 20


# ==================== LỊCH SỬ HỘI THOẠI ====================

def load_history_from_supabase(chat_id):
    """Tải lịch sử hội thoại từ Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None  # Không có Supabase, dùng RAM

    try:
        url = f"{SUPABASE_URL}/rest/v1/chat_history"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        params = {
            "chat_id": f"eq.{chat_id}",
            "order": "created_at.desc",
            "limit": str(MAX_HISTORY)
        }
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            rows = response.json()
            rows.reverse()  # Đảo ngược: cũ -> mới
            return [{"role": row["role"], "content": row["content"]} for row in rows]
        else:
            logger.error(f"Supabase load error: {response.status_code} - {response.text[:100]}")
            return None
    except Exception as e:
        logger.error(f"Supabase load error: {e}")
        return None


def save_to_supabase(chat_id, role, content):
    """Lưu tin nhắn vào Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return  # Không có Supabase, bỏ qua

    try:
        url = f"{SUPABASE_URL}/rest/v1/chat_history"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        data = {
            "chat_id": str(chat_id),
            "role": role,
            "content": content
        }
        requests.post(url, headers=headers, json=data, timeout=5)
    except Exception as e:
        logger.error(f"Supabase save error: {e}")


def get_history(chat_id):
    """Lấy lịch sử hội thoại - ưu tiên Supabase, fallback RAM"""
    # Thử lấy từ Supabase trước
    history = load_history_from_supabase(chat_id)
    if history is not None:
        return history

    # Fallback: dùng RAM
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    return conversation_history[chat_id]


def add_to_history(chat_id, role, content):
    """Lưu tin nhắn vào lịch sử (cả Supabase và RAM)"""
    # Lưu vào Supabase
    save_to_supabase(chat_id, role, content)

    # Lưu vào RAM (backup)
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    conversation_history[chat_id].append({"role": role, "content": content})
    if len(conversation_history[chat_id]) > MAX_HISTORY:
        conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY:]


# ==================== GỌI AI API ====================

def call_gemini(user_message, chat_id):
    """Gọi Google Gemini API"""
    if not GEMINI_API_KEY:
        return None

    try:
        history = get_history(chat_id)
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.8}
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"Gemini error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None


def call_openrouter(user_message, chat_id):
    """Gọi OpenRouter API - thử nhiều model miễn phí"""
    if not OPENROUTER_API_KEY:
        return None

    history = get_history(chat_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    for model in FREE_MODELS:
        try:
            logger.info(f"Trying OpenRouter model: {model}")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 1000,
                },
                timeout=25
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if content:
                    logger.info(f"OpenRouter success: {model}")
                    return content
            else:
                logger.warning(f"OpenRouter {model} failed: {response.status_code}")
                continue
        except Exception as e:
            logger.error(f"OpenRouter {model} error: {e}")
            continue

    return None


# ==================== HÀM CHÍNH ====================

def get_ai_response(user_message, chat_id):
    """Lấy phản hồi AI - thử Gemini trước, nếu lỗi thì dùng OpenRouter với nhiều model"""
    # Thử Gemini trước
    response = call_gemini(user_message, chat_id)

    # Nếu Gemini lỗi, dùng OpenRouter (thử nhiều model)
    if response is None:
        logger.info("Gemini failed, switching to OpenRouter...")
        response = call_openrouter(user_message, chat_id)

    # Nếu tất cả đều lỗi
    if response is None:
        response = "Dạ, em xin lỗi anh 😅 Hiện tại tất cả nguồn AI đều đang gặp trục trặc. Anh thử lại sau vài phút nha! 🙏"

    # Lưu vào lịch sử (cả Supabase và RAM)
    add_to_history(chat_id, "user", user_message)
    add_to_history(chat_id, "assistant", response)

    return response

