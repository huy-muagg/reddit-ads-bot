import google.generativeai as genai
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, TOOLS_INFO, POST_GENERATION_PROMPT

load_dotenv()

class AIGenerator:
    def __init__(self):
        # (giữ nguyên init)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        else:
            self.model = None

    async def generate_comment(self, tool_id, post_content):
        # (giữ nguyên hàm cmt cũ)
        if not self.model: return "Error: API key missing"
        tool = TOOLS_INFO.get(tool_id)
        prompt = SYSTEM_PROMPT.format(tool_name=tool["name"], post_content=post_content, tool_details=f"URL: {tool['url']}")
        response = self.model.generate_content(prompt)
        return response.text.strip()

    async def generate_post(self, tool_id):
        if not self.model:
            return "Error: GEMINI_API_KEY not found."
        
        tool = TOOLS_INFO.get(tool_id)
        if not tool:
            return "Error: Tool ID not found."

        prompt = POST_GENERATION_PROMPT.format(
            tool_name=tool["name"],
            tool_details=f"Description: {tool['description']}\nUSP: {tool['usp']}\nURL: {tool['url']}"
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating post: {str(e)}"

# Example usage (uncomment to test):
# async def test():
#     gen = AIGenerator()
#     print(await gen.generate_comment("subly", "I need a way to translate my TikTok videos to Spanish."))
