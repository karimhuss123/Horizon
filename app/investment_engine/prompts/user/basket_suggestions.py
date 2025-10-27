BASKET_SUGGESTIONS_USER_PROMPT = """
You are given the current basket and optional constraints. Produce up to {max_suggestions} high-quality, evidence-backed suggestions.

## Basket (current state)
Name: {basket_name}
Description: {basket_description}

### Holdings
{holdings_text}

## Decision guidance
- **Add** when a relevant, well-supported name is missing and improves thematic or risk balance.
- **Remove** when a holding is off-theme, redundant, or misaligned with constraints/risk.
- **Update** when keeping the holding makes sense but a change is warranted (e.g., reduce concentration, rebalance after material business changes). Specify the nature of the change inside the rationale text (e.g., “reduce weight to ~5% to limit concentration risk”).

## Output
Return ONLY valid JSON with a single top-level key **"data"**, whose value is a list of suggestion objects.

The JSON must have this exact structure:

{{
  "data": [
    {{
      "ticker": "<ticker of security>",
      "name": "<company/security name>",
      "rationale": "<concise factual reason for the suggestion; no meta phrases like 'aligns with the theme'>",
      "action": "Add" | "Remove" | "Update",
      "source_url": "<credible URL backing the rationale>"
    }},
    ...
  ]
}}

- Do not include any text, commentary, or explanation outside this JSON object.
- If no strong suggestions exist, return: {{"data": []}}
"""
