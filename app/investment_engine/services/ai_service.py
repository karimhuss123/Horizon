import json
from app.clients.openai_client import OpenAIClient
from app.investment_engine.prompts.system.intent_enrichment import INTENT_ENRICHMENT_PROMPT
from app.investment_engine.prompts.system.intent_regeneration import INTENT_REGENERATION_PROMPT
from app.investment_engine.prompts.system.gen_rationale import GEN_RATIONALE_SYSTEM_PROMPT
from app.investment_engine.prompts.user.gen_rationale import GEN_RATIONALE_USER_PROMPT
from app.investment_engine.prompts.system.suggestion_rationale import SUG_RATIONALE_SYSTEM_PROMPT
from app.investment_engine.prompts.user.suggestion_rationale import SUG_RATIONALE_USER_PROMPT
from app.investment_engine.prompts.system.basket_metadata_generate import BASKET_METADATA_SYSTEM_PROMPT
from app.core.config import settings

class AIService:
    def __init__(
		self, 
		client: OpenAIClient,
		intent_enrichment_prompt: str = INTENT_ENRICHMENT_PROMPT,
        intent_regeneration_prompt: str = INTENT_REGENERATION_PROMPT,
        gen_rationale_system_prompt: str = GEN_RATIONALE_SYSTEM_PROMPT,
        gen_rationale_user_prompt: str = GEN_RATIONALE_USER_PROMPT,
        sug_rationale_system_prompt: str = SUG_RATIONALE_SYSTEM_PROMPT,
        sug_rationale_user_prompt: str = SUG_RATIONALE_USER_PROMPT,
        basket_metadata_generate_prompt: str = BASKET_METADATA_SYSTEM_PROMPT
    ):
        self.client = client
        self.intent_enrichment_prompt = intent_enrichment_prompt
        self.intent_regeneration_prompt = intent_regeneration_prompt
        self.gen_rationale_system_prompt = gen_rationale_system_prompt
        self.gen_rationale_user_prompt = gen_rationale_user_prompt
        self.sug_rationale_system_prompt = sug_rationale_system_prompt
        self.sug_rationale_user_prompt = sug_rationale_user_prompt
        self.basket_metadata_generate_prompt = basket_metadata_generate_prompt
    
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
			f"{h["ticker"]} — "
			f"Weight: {h["weight_pct"]:.2f}% — Rationale: {h["rationale"]}"
			for h in regen_data["holdings"]
		)
        basket_context = (
			f"Existing basket:\n"
			f"Name: {regen_data["name"]}\n"
			f"Description: {regen_data["description"]}\n\n"
			f"Holdings:\n{holdings_text}\n\n"
			f"New user instructions:\n{regen_data["user_prompt"].strip()}"
		)
        messages = [
            {"role": "system", "content": self.intent_regeneration_prompt},
            {"role": "user", "content": basket_context}
        ]
        resp = self.client.chat(messages=messages, temperature=settings.TEMPERATURES["regeneration"], as_json=True)
        data = json.loads(resp)
        data["user_prompt"] = regen_data["user_prompt"]
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
        user_prompt = self.gen_rationale_user_prompt.format(
            basket_name=criteria["name"],
            theme_summary=criteria["theme_summary"],
            keywords=criteria["keywords"],
            sectors=criteria["sectors"],
            holdings_text=holdings_text
        )
        messages = [
            {"role": "system", "content": self.gen_rationale_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        resp = self.client.chat(messages=messages, temperature=settings.TEMPERATURES["rationale"], as_json=True)
        data = json.loads(resp)
        if isinstance(data, dict):
            for h in holdings:
                h["rationale"] = data.get(h["ticker"], "")
        return holdings
    
    def generate_suggestion_rationales(self, basket, securities):
        securities_text = "\n".join(
            f"Ticker: {s["ticker"]}\n"
            f"Name: {s["name"]}\n"
            f"Description: {s["company_description"]}\n"
            f"Industry: {s["industry"]}\n"
            f"Market Cap (USD): {s["market_cap_usd"]}\n"
            f"Relevant news: {s["news_summary"]}\n"
            for s in securities
        )
        user_prompt = self.sug_rationale_user_prompt.format(
            basket_name=basket.name,
            theme_summary=basket.description,
            keywords=basket.keywords,
            sectors=basket.sectors,
            securities_text=securities_text
        )
        messages = [
            {"role": "system", "content": self.sug_rationale_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        resp = self.client.chat(messages=messages, temperature=settings.TEMPERATURES["rationale"], as_json=True)
        data = json.loads(resp)
        if isinstance(data, dict):
            for s in securities:
                s["rationale"] = data.get(s["ticker"], "")
        return securities
    
    def generate_basket_metadata(self, basket):
        holdings_text = "\n".join(
            f"Ticker: {h.ticker}\n"
            f"Weight: {h.weight_pct:.2f}%\n"
            f"Rationale: {h.rationale}\n"
            for h in basket.holdings
		)
        basket_context = (
			f"Existing basket:\n"
			f"Name: {basket.name}\n"
			f"Description: {basket.description}\n\n"
			f"Holdings:\n{holdings_text}\n\n"
		)
        messages = [
            {"role": "system", "content": self.basket_metadata_generate_prompt},
            {"role": "user", "content": basket_context}
        ]
        resp = self.client.chat(messages=messages, temperature=settings.TEMPERATURES["regeneration"], as_json=True)
        data = json.loads(resp)
        return data