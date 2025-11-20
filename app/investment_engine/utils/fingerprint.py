import hashlib
import json

def compute_basket_fingerprint(basket) -> str:
    # Later: maybe include rationale if there is a use
    payload = {
        "name": basket.name or "",
        "description": basket.description or "",
        "holdings": sorted(
            [
                {
                    "ticker": (h.ticker or "").strip(),
                    "weight_pct": float(h.weight_pct or 0.0),
                }
                for h in basket.holdings
            ],
            key=lambda x: x["ticker"],
        ),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
