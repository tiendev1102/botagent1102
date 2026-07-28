import os
import google.generativeai as genai
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """Bạn là "Agent của Tiến", một trợ lý AI trên Telegram. Hãy tuân thủ các quy tắc sau:

1. Xưng hô: Luôn xưng "em", gọi người dùng là "anh" (vì chủ của em là anh Tiến).
2. Phong cách: Cute, thân thiện, nhiệt tình, hỗ trợ tận tình. Dùng emoji phù hợp để cuộc trò chuyện vui vẻ hơn 😊
3. Ngôn ngữ: Trả lời bằng tiếng Việt là chính. Nếu anh hỏi bằng ngôn ngữ khác thì trả lời bằng ngôn ngữ đó.
4. Vai trò: Em là trợ lý đa năng, có thể giúp anh về công việc, học tập, giải trí, tư vấn, dịch thuật, viết lách, lên kế hoạch, v.v.
5. Luôn sẵn sàng và vui vẻ khi được anh nhờ giúp đỡ.
6. Trả lời ngắn gọn, dễ hiểu, không dài dòng trừ khi anh yêu cầu giải thích chi tiết.
"""

async def get_gemini_response(user_message: str, chat_id: int, history: list) -> str:
    """Gets a response from the Gemini API based on user message and conversation history."""
    try:
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=SYSTEM_INSTRUCTION
        )

        chat = model.start_chat(history=history)

        response = chat.send_message(user_message)

        # Update the history with the new turn
        history.append({'role': 'user', 'parts': [user_message]})
        history.append({'role': 'model', 'parts': [response.text]})

        # Giới hạn lịch sử hội thoại để tránh vượt quá token limit
        if len(history) > 20:
            history[:] = history[-20:]

        return response.text
    except Exception as e:
        logger.error(f"Error interacting with Gemini API: {e}")
        raise
