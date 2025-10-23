from openai import OpenAI
from fastapi import HTTPException
from dotenv import load_dotenv
import os
load_dotenv()

class OpenAIClient:
    def __init__(self, model=None, embeddings_model=None):
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.embeddings_model = embeddings_model or os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    
    def chat(self, messages, temperature):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return resp.choices[0].message.to_dict().get("content")
    
    def get_embeddings(self, string):
        resp = self.client.embeddings.create(model=self.embeddings_model, input=string)
        return resp.data[0].embedding