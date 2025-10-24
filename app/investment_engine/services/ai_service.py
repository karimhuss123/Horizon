from clients.openai_client import OpenAIClient
from investment_engine.prompts.system.intent_enrichment import INTENT_ENRICHMENT_PROMPT
from investment_engine.prompts.system.intent_regeneration import INTENT_REGENERATION_PROMPT
from investment_engine.prompts.system.rationale import RATIONALE_SYSTEM_PROMPT
from investment_engine.prompts.user.rationale import RATIONALE_USER_PROMPT
from core.config import settings
import json

class AIService:
    def __init__(
		self, 
		client: OpenAIClient,
		intent_enrichment_prompt: str = INTENT_ENRICHMENT_PROMPT,
        intent_regeneration_prompt: str = INTENT_REGENERATION_PROMPT,
        rationale_system_prompt: str = RATIONALE_SYSTEM_PROMPT,
        rationale_user_prompt: str = RATIONALE_USER_PROMPT
    ):
        self.client = client
        self.intent_enrichment_prompt = intent_enrichment_prompt
        self.intent_regeneration_prompt = intent_regeneration_prompt
        self.rationale_system_prompt = rationale_system_prompt
        self.rationale_user_prompt = rationale_user_prompt
    
    def generate_intent_query(self, user_prompt):
        messages = [
            {"role": "system", "content": self.intent_enrichment_prompt},
            {"role": "user", "content": user_prompt}
        ]
        resp = self.client.chat(messages=messages, temperature=settings.TEMPERATURES["intent"], as_json=True)
        data = json.loads(resp)
        data["user_prompt"] = user_prompt
        return data
    
    def regenerate_intent_query(self, regen_data):
        holdings_text = "\n".join(
			f"{h.ticker} — "
			f"Weight: {h.weight_pct:.2f}% — Rationale: {h.rationale}"
			for h in regen_data.holdings
		)
        basket_context = (
			f"Existing basket:\n"
			f"Name: {regen_data.name}\n"
			f"Description: {regen_data.description}\n\n"
			f"Holdings:\n{holdings_text}\n\n"
			f"New user instructions:\n{regen_data.user_prompt.strip()}"
		)
        messages = [
            {"role": "system", "content": self.intent_regeneration_prompt},
            {"role": "user", "content": basket_context}
        ]
        resp = self.client.chat(messages=messages, temperature=settings.TEMPERATURES["regeneration"], as_json=True)
        data = json.loads(resp)
        data["user_prompt"] = regen_data.user_prompt
        return data
    
    def generate_holding_rationales(self, criteria, holdings):
        holdings_text = "\n".join(
            f"Ticker: {h["ticker"]}\n"
            f"Name: {h["name"]}\n"
            f"Description: {h["description"]}\n"
            f"Industry: {h["industry"]}\n"
            f"Market Cap: {h["market_cap_usd"]}\n"
            f"Weight: {h["weight_pct"]:.2f}%\n"
            for h in holdings
		)
        prompt = self.rationale_user_prompt.format(
            basket_name=criteria["name"],
            theme_summary=criteria["theme_summary"],
            keywords=criteria["keywords"],
            holdings_text=holdings_text
        )
        messages = [
            {"role": "system", "content": self.rationale_system_prompt},
            {"role": "user", "content": prompt}
        ]
        resp = self.client.chat(messages=messages, temperature=settings.TEMPERATURES["rationale"], as_json=True)
        data = json.loads(resp)
        if isinstance(data, dict):
            for h in holdings:
                h["rationale"] = data.get(h["ticker"], "")
        return holdings
