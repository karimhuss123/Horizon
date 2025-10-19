from openai import OpenAI
from fastapi import HTTPException
from dotenv import load_dotenv
import os
load_dotenv()

class OpenAIClient:
    def __init__(self, model=None):
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def chat(self, messages, temperature):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return resp.choices[0].message.to_dict().get("content")