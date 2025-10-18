from clients.openai_client import OpenAIClient
from utils.parsing import ensure_valid_basket_json

SYSTEM_PROMPT = """
You are an AI portfolio builder. Return STRICT JSON with:
{
  "basket_name": string,
  "thesis": string,
  "holdings": [
    {"ticker": string, "name": string, "weight_pct": number, "rationale": string}
  ]
}
Rules:
- Max 10 holdings
- Weights must sum to 100
- Only include tickers that exist and match the user's constraints
- No prose outside JSON
"""

class AIService:
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    def generate_basket_data(self, user_prompt):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        resp = self.client.chat(messages=messages, temperature=0)
        data = ensure_valid_basket_json(resp)
        data["user_prompt"] = user_prompt
        return data