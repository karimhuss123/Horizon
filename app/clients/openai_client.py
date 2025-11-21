from openai import OpenAI
from app.core.config import settings

class OpenAIClient:
    def __init__(self, model=None, embeddings_model=None):
        self.client = OpenAI(api_key=settings.OPENAI_KEY)
        self.model = model or settings.OPENAI_CHAT_MODEL
        self.embeddings_model = embeddings_model or settings.OPENAI_EMBEDDINGS_MODEL
    
    def chat(self, messages, temperature, as_json=False):
        kwargs = dict(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        if as_json:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.to_dict().get("content")
    
    def get_embeddings(self, string):
        resp = self.client.embeddings.create(model=self.embeddings_model, input=string)
        return resp.data[0].embedding

    def get_embeddings_batch(self, list):
        resp = self.client.embeddings.create(model=self.embeddings_model, input=list)
        embeddings_list = [item.embedding for item in resp.data]
        return embeddings_list, len(embeddings_list)