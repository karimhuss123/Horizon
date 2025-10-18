import json
from typing import Any, Dict

def ensure_valid_basket_json(str):
    data = json.loads(str)
    assert "holdings" in data and isinstance(data["holdings"], list), "missing holdings"
    weights = [h.get("weight_pct", 0) for h in data["holdings"]]
    total = sum(weights)
    if total != 1:
        if total == 0:
            raise ValueError("weights sum to 0")
        data["holdings"] = [
            {**h, "weight_pct": (h.get("weight_pct", 0) / total)}
            for h in data["holdings"]
        ]
    return data
