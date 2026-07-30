import logging
import requests
import os
from datetime import datetime, timezone, timedelta
from duckduckgo_search import DDGS
from config import GEMINI_API_KEY, OPENROUTER_API_KEY, TAVILY_API_KEY

logger = logging.getLogger(__name__)

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Múi giờ Việt Nam (GMT+7)
VN_TIMEZONE = timezone(timedelta(hours=7))

# System prompt cơ bản
BASE_SYSTEM_PROMPT = """Bạn là "Agent của Tiến", một trợ lý AI trên Telegram. Hãy tuân thủ các quy tắc sau:
1. Xưng hô: Luôn xưng "em", gọi người dùng là "anh Tiến" hoặc "anh".
2. Phong cách: Cute, thân thiện, nhiệt tình, hỗ trợ tận tình. Dùng emoji phù hợp 😊
3. Ngôn ngữ: Trả lời bằng tiếng Việt là chính. Nếu anh hỏi bằng ngôn ngữ khác thì trả lời bằng ngôn ngữ đó.
4. Vai trò: Em là trợ lý đa năng - giúp công việc, học tập, giải trí, tư vấn, dịch thuật, viết lách, lên kế hoạch.
5. Luôn sẵn sàng và vui vẻ khi được nhờ giúp đỡ.
6. Trả lời ngắn gọn, dễ hiểu, không dài dòng trừ khi được yêu cầu giải thích chi tiết.
7. Khi được hỏi về ngày giờ, sử dụng thông tin thời gian thực được cung cấp bên dưới.
8. Anh Tiến không biết code và không giỏi tiếng Anh, nên giải thích mọi thứ đơn giản, dễ hiểu.
9. Nếu có thông tin tìm kiếm từ web (Search Results), hãy sử dụng chúng để trả lời một cách chính xác và cập nhật nhất.
"""


def get_system_prompt():
    """Tạo system prompt với ngày giờ thực tế (múi giờ Việt Nam)"""
    now = datetime.now(VN_TIMEZONE)
    weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    weekday_name = weekdays[now.weekday()]
    time_info = f"""
THÔNG TIN THỜI GIAN THỰC:
- Ngày hiện tại: {weekday_name}, ngày {now.strftime('%d/%m/%Y')} (dương lịch)
- Giờ hiện tại: {now.strftime('%H:%M')} (giờ Việt Nam, GMT+7)
- Năm: {now.year}
"""
    return BASE_SYSTEM_PROMPT + time_info


# Danh sách model miễn phí trên OpenRouter
FREE_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
]

# Lưu lịch sử hội thoại trong RAM
conversation_history = {}
MAX_HISTORY = 20


def load_history_from_supabase(chat_id):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
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
            rows.reverse()
            return [{"role": row["role"], "content": row["content"]} for row in rows]
        else:
            logger.error(f"Supabase load error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Supabase load error: {e}")
        return None


def save_to_supabase(chat_id, role, content):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    try:
        url = f"{SUPABASE_URL}/rest/v1/chat_history"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        data = {"chat_id": str(chat_id), "role": role, "content": content}
        requests.post(url, headers=headers, json=data, timeout=5)
    except Exception as e:
        logger.error(f"Supabase save error: {e}")


def get_history(chat_id):
    history = load_history_from_supabase(chat_id)
    if history is not None:
        return history
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    return conversation_history[chat_id]


def add_to_history(chat_id, role, content):
    save_to_supabase(chat_id, role, content)
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    conversation_history[chat_id].append({"role": role, "content": content})
    if len(conversation_history[chat_id]) > MAX_HISTORY:
        conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY:]


# --- WEB SEARCH MODULE ---

def should_search(text):
    """Phân loại xem tin nhắn có cần search web không dựa trên keyword"""
    keywords = [
        "thời tiết", "tin tức", "giá", "tỷ giá", "mới nhất", "hôm nay", 
        "bây giờ", "hiện tại", "search", "tìm", "tra cứu", "google",
        "thế nào", "ai là", "ở đâu", "mấy giờ", "kết quả", "trận đấu"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def web_search_ddg(query, max_results=5):
    """Tìm kiếm bằng DuckDuckGo (Miễn phí, không cần API key)"""
    try:
        logger.info(f"Searching DuckDuckGo for: {query}")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return None
            
            formatted_results = []
            for r in results:
                formatted_results.append(f"- {r['title']}: {r['body']} (Nguồn: {r['href']})")
            return "\n".join(formatted_results)
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return None


def web_search_tavily(query):
    """Tìm kiếm bằng Tavily (Dự phòng, cần API key)"""
    if not TAVILY_API_KEY:
        return None
    try:
        logger.info(f"Searching Tavily for: {query}")
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": 5
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if not results:
                return None
            
            formatted_results = []
            for r in results:
                formatted_results.append(f"- {r['title']}: {r['content']} (Nguồn: {r['url']})")
            return "\n".join(formatted_results)
        return None
    except Exception as e:
        logger.error(f"Tavily search error: {e}")
        return None


def perform_search(query):
    """Thực hiện tìm kiếm, thử DDG trước, sau đó là Tavily"""
    # Thử DuckDuckGo
    results = web_search_ddg(query)
    
    # Nếu DDG fail, thử Tavily
    if not results:
        results = web_search_tavily(query)
        
    return results


# --- AI CALLS ---

def call_gemini(user_message, chat_id, search_context=None):
    if not GEMINI_API_KEY:
        return None
    try:
        history = get_history(chat_id)
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        # Nếu có kết quả search, thêm vào tin nhắn cuối của user
        final_message = user_message
        if search_context:
            final_message = f"Dưới đây là kết quả tìm kiếm từ internet cho câu hỏi của anh:\n\n{search_context}\n\nDựa vào thông tin trên, hãy trả lời câu hỏi: {user_message}"
            
        contents.append({"role": "user", "parts": [{"text": final_message}]})
        
        system_prompt = get_system_prompt()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.8}
        }
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"Gemini error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None


def call_openrouter(user_message, chat_id, search_context=None):
    if not OPENROUTER_API_KEY:
        return None
    history = get_history(chat_id)
    system_prompt = get_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Thêm context search
    final_message = user_message
    if search_context:
        final_message = f"Dưới đây là kết quả tìm kiếm từ internet cho câu hỏi của anh:\n\n{search_context}\n\nDựa vào thông tin trên, hãy trả lời câu hỏi: {user_message}"
        
    messages.append({"role": "user", "content": final_message})
    
    for model in FREE_MODELS:
        try:
            logger.info(f"Trying OpenRouter model: {model}")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "messages": messages, "max_tokens": 1000},
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


def get_ai_response(user_message, chat_id):
    # 1. Kiểm tra xem có cần search web không
    search_context = None
    if should_search(user_message):
        search_context = perform_search(user_message)
    
    # 2. Gọi AI (Gemini trước, OpenRouter sau)
    response = call_gemini(user_message, chat_id, search_context)
    if response is None:
        logger.info("Gemini failed, switching to OpenRouter...")
        response = call_openrouter(user_message, chat_id, search_context)
    
    if response is None:
        response = "Dạ, em xin lỗi anh 😅 Hiện tại tất cả nguồn AI đều đang gặp trục trặc. Anh thử lại sau vài phút nha! 🙏"
    
    # 3. Lưu lịch sử (Lưu tin nhắn gốc của user, không lưu context search để tiết kiệm dung lượng)
    add_to_history(chat_id, "user", user_message)
    add_to_history(chat_id, "assistant", response)
    
    return response
