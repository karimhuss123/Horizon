from clients.openai_client import OpenAIClient
from utils.parsing import ensure_valid_basket_json
from prompts.gen import GENERATE_SYSTEM_PROMPT, GENERATE_SYSTEM_PROMPT_VERSION
from prompts.regen import REGENERATE_SYSTEM_PROMPT, REGENERATE_SYSTEM_PROMPT_VERSION

class AIService:
    def __init__(
		self, 
		client: OpenAIClient,
		generate_prompt: str = GENERATE_SYSTEM_PROMPT,
		generate_prompt_version: str = GENERATE_SYSTEM_PROMPT_VERSION,
		regenerate_prompt: str = REGENERATE_SYSTEM_PROMPT,
		regenerate_prompt_version: str = REGENERATE_SYSTEM_PROMPT_VERSION,
    ):
        self.client = client
        self.generate_prompt = generate_prompt
        self.generate_prompt_version = generate_prompt_version
        self.regenerate_prompt = regenerate_prompt
        self.regenerate_prompt_version = regenerate_prompt_version
    
    def generate_basket_data(self, user_prompt):
        messages = [
            {"role": "system", "content": self.generate_prompt},
            {"role": "user", "content": user_prompt}
        ]
        resp = self.client.chat(messages=messages, temperature=0)
        data = ensure_valid_basket_json(resp)
        data["user_prompt"] = user_prompt
        return data
    
    def regenerate_basket_data(self, data):
        holdings_text = "\n".join(
			f"{h.ticker} — {h.name} — "
			f"Weight: {h.weight_pct:.2f}% — Rationale: {h.rationale}"
			for h in data.holdings
		)
        
        basket_context = (
			f"Existing basket:\n"
			f"Name: {data.name}\n"
			f"Description: {data.description}\n\n"
			f"Holdings:\n{holdings_text}\n\n"
			f"New user instructions:\n{data.user_prompt.strip()}"
		)
        
        messages = [
			{"role": "system", "content": self.regenerate_prompt},
			{"role": "user", "content": basket_context},
		]
        
        resp = self.client.chat(messages=messages, temperature=0)
        basket_data = ensure_valid_basket_json(resp)
        
        return basket_data