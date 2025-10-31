from sqlalchemy.orm import Session
from db.models import Security
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

class SelectorService:
    def __init__(self, db: Session):
        self.db = db
    
    def screen(self, criteria):
        q = self.db.query(Security)
        if criteria.get("min_market_cap_usd"):
            q = q.filter(Security.market_cap_usd >= criteria["min_market_cap_usd"])
        if criteria.get("max_market_cap_usd"):
            q = q.filter(Security.market_cap_usd <= criteria["max_market_cap_usd"])
        if criteria.get("sectors"):
            q = q.filter(Security.gics_sector.in_(criteria["sectors"]))
        if criteria.get("regions"):
            q = q.filter(Security.region.in_(criteria["regions"]))
        # More filters can be added...
        
        return [s.id for s in q.all()]
    
    def assign_hybrid_weights(self, securities, alpha=1.0, beta=0.7, min_cap=1e6):
        """
        securities: list of dicts with keys ['similarity', 'market_cap']
        alpha: importance of similarity
        beta: importance of market cap
        """
        sims = np.array([max(s["similarity"], 0) for s in securities])
        caps = np.array([max(s.get("market_cap", 0), min_cap) for s in securities])

        caps_norm = caps / caps.max()
        scores = (sims ** alpha) * (caps_norm ** beta)
        weights = scores / scores.sum() * 100
        
        normalized = self._normalize_weights_to_100(weights)

        for s, w in zip(securities, normalized):
            s["weight_pct"] = w

        return securities
    
    def _normalize_weights_to_100(self, weights):
        if len(list(weights)) == 0:
            return []
        weights = [Decimal(str(w)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for w in weights]
        diff = Decimal('100.00') - sum(weights)
        if diff != 0:
            i = max(range(len(weights)), key=lambda i: weights[i])
            weights[i] = (weights[i] + diff).quantize(Decimal('0.01'))
        return [float(w) for w in weights]
