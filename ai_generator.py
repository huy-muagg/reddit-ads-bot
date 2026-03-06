from google import genai
import os
import asyncio
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, TOOLS_INFO, POST_GENERATION_PROMPT, TRANSLATION_PROMPT, SUMMARY_PROMPT

load_dotenv()

class AIGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_id = "gemini-2.5-flash"
        else:
            self.client = None

    async def generate_comment(self, tool_id, post_content, top_comments="None"):
        if not self.client: return "Error: API key missing"
        tool = TOOLS_INFO.get(tool_id)
        prompt = SYSTEM_PROMPT.format(
            tool_name=tool["name"], 
            post_content=post_content, 
            top_comments=top_comments,
            tool_details=f"URL: {tool['url']}\nDescription: {tool['description']}\nUSP: {tool['usp']}"
        )
        try:
            response = await asyncio.to_thread(self.client.models.generate_content, model=self.model_id, contents=prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    async def generate_summary(self, title, content):
        if not self.client: return "Error: API key missing"
        prompt = SUMMARY_PROMPT.format(title=title, content=content)
        try:
            response = await asyncio.to_thread(self.client.models.generate_content, model=self.model_id, contents=prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error summarizing: {str(e)}"

    async def chat_with_ai(self, user_text):
        """Tính năng chat tự do với AI."""
        if not self.client: return "Error: API key missing"
        try:
            # Sử dụng persona là một trợ lý thông minh hỗ trợ marketing và kiến thức tổng quát
            system_instruction = "Bạn là một trợ lý AI thông minh, hỗ trợ Huy trong việc marketing trên Reddit và trả lời mọi câu hỏi kiến thức khác một cách chuyên nghiệp, súc tích bằng Tiếng Việt."
            response = await asyncio.to_thread(
                self.client.models.generate_content, 
                model=self.model_id, 
                contents=f"{system_instruction}\n\nNgười dùng hỏi: {user_text}"
            )
            return response.text.strip()
        except Exception as e:
            return f"Error in AI chat: {str(e)}"

    async def generate_post(self, tool_id):
        if not self.client: return "Error: GEMINI_API_KEY not found."
        tool = TOOLS_INFO.get(tool_id)
        if not tool: return "Error: Tool ID not found."
        prompt = POST_GENERATION_PROMPT.format(
            tool_name=tool["name"],
            tool_details=f"Description: {tool['description']}\nUSP: {tool['usp']}\nURL: {tool['url']}",
            url=tool['url']
        )
        try:
            response = await asyncio.to_thread(self.client.models.generate_content, model=self.model_id, contents=prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating post: {str(e)}"

    async def translate_text(self, text):
        if not self.client: return "Error: API key missing"
        prompt = TRANSLATION_PROMPT.format(text=text)
        try:
            response = await asyncio.to_thread(self.client.models.generate_content, model=self.model_id, contents=prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error translating: {str(e)}"
