import json

def ensure_valid_basket_json(s: str):
    data = json.loads(s)
    assert "holdings" in data and isinstance(data["holdings"], list), "missing holdings"
    holdings = data["holdings"]

    weights = [float(h.get("weight_pct", 0) or 0) for h in holdings]
    total = sum(weights)

    if total == 0:
        raise ValueError("weights sum to 0")

    # Normalize to 100
    normalized = [(w / total) * 100 for w in weights]

    # Round to 2 decimals
    rounded = [round(w, 2) for w in normalized]
    diff = round(100 - sum(rounded), 2)

    # Adjust the largest weight (or last) to absorb rounding difference
    if rounded:
        idx = max(range(len(rounded)), key=lambda i: rounded[i])
        rounded[idx] = round(rounded[idx] + diff, 2)

    # Reattach corrected weights
    for i, h in enumerate(holdings):
        h["weight_pct"] = rounded[i]

    # Verify again
    assert round(sum(rounded), 2) == 100.00, f"weights sum {sum(rounded)} != 100"

    return data