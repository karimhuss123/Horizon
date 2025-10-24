RATIONALE_USER_PROMPT_VERSION = "rationale.user.v1.0"

RATIONALE_USER_PROMPT = """
You are an investment assistant. Write concise, professional rationales for why each holding belongs in the basket, grounded ONLY in the context provided. Do not add facts not given in the holding profiles.

## Basket Theme
Name: {basket_name}
Theme summary: {theme_summary}
Keywords (optional): {keywords}

## Holdings
You are given a list of holdings. Each item includes:
- Ticker
- Name
- Description (1–2 sentence company profile from our database)
- Industry
- Market Cap (USD)
- Weight Percentage

Holdings:
{holdings_text}

## Task
For EACH holding, produce a short rationale (1–2 sentences, 20–40 words) that:
- Explicitly connects the company’s business, products, or services to the overall investment idea (e.g., relevant industries, technologies, or markets).
- Uses ONLY the information provided in the holding (name, industry, description, etc.).
- Avoids speculative claims, price targets, or performance predictions.
- If information is sparse, keep the rationale general but still relevant (e.g., reference the company’s sector or market focus).
- Keep tone factual, precise, and investor-oriented.
- **Do NOT mention the “basket,” “theme,” or the idea of alignment or fit.** Write each rationale as an independent, factual statement about the company itself.
- Tickers in the output **must be exactly the same** as the tickers in the provided list of holdings

## Output
Return ONLY valid JSON as a single object.

Each key must be the holding’s ticker symbol, and each value must be a concise, factual rationale (1–2 sentences) describing the company’s core business, strengths, or relevance based on the provided information.

Example:
{{
  "AAPL": "Apple designs and sells consumer electronics, software, and services, generating consistent revenue from its ecosystem of devices and digital platforms.",
  "ADBE": "Adobe develops creative and digital experience software that enables content creation, marketing, and document management for individuals and enterprises.",
  "CRM": "Salesforce provides cloud-based customer relationship management software supporting business sales, service, and marketing operations globally."
}}


Do not include any other fields or commentary.
"""
