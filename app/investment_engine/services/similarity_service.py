from sqlalchemy.orm import Session
from investment_engine.utils.similarity_backend import np_cosine_similarity_batch
from market_data.repositories.security_repo import SecurityRepo
from db.utils.time import current_datetime_et
from datetime import timezone
import math
from core.config import settings

class SimilarityService:
    def __init__(self, db: Session):
        self.db = db
        self.securities = SecurityRepo(db)
    
    def get_top_k_suggestions(self, theme_embedding, securities, k=settings.AI_SUGGESTIONS_COUNT):
        blocks, meta = self._collect_news_blocks(securities)
        if not blocks:
            return []
        sims_all = np_cosine_similarity_batch(blocks, theme_embedding)
        suggestions = []
        for (si, s, e, news_list) in meta:
            sec = securities[si]
            sec_sim = sec["similarity"]
            sims_slice = sims_all[s:e]
            pairs_sorted = self._get_sorted_news_sim_pairs(news_list, s, e, sims_slice)

            top_news = pairs_sorted[:3]
            agg_news_score = self._compute_news_agg_score(top_news)
            final_score = self._compute_suggestion_final_score(sec_sim, agg_news_score)

            top1 = top_news[0]["news"] if top_news else None
            suggestions.append(self._build_suggestion(sec, final_score, top1))

        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:k]
    
    def _collect_news_blocks(self, securities):
        blocks = []
        meta = []
        start = 0
        for si, sec in enumerate(securities):
            news = self.securities.get_security(sec["id"]).news
            news_embeddings = [n.text_embedding for n in news]
            blocks.extend(news_embeddings)
            end = start + len(news_embeddings)
            meta.append((si, start, end, news))
            start = end
        return blocks, meta
    
    def _get_sorted_news_sim_pairs(self, news_list, start, end, sims_slice):
        pairs = []
        for i in range(end - start):
            n = news_list[i]
            sim = float(sims_slice[i])
            recency_score = self._recency_score(n.published_at)
            pairs.append({
                "news": n,
                "sim_theme_news": sim,
                "recency_score": recency_score,
                "weighted_news_score": sim * recency_score
            })
        return sorted(pairs, key=lambda x: x["weighted_news_score"], reverse=True)
    
    def _build_suggestion(self, sec, score, news=None):
        return {
            "security_id": sec["id"],
            "ticker": sec["ticker"],
            "name": sec["name"],
            "company_description": sec["description"],
            "industry": sec["industry"],
            "market_cap_usd": sec["market_cap_usd"],
            "action": "Add",
            "source_url": news.url if news else "",
            "news_summary": news.summary if news else "",
            "news_id": news.id if news else None,
            "score": score
        }
    
    def _compute_news_agg_score(self, news, decaying_factor=0.5):
        return sum(x["weighted_news_score"] * (decaying_factor ** i) for i, x in enumerate(news))

    def _compute_suggestion_final_score(self, sec_sim, agg_news_score, theme_wgt=0.5, news_wgt=0.5):
        return theme_wgt * sec_sim + news_wgt * agg_news_score

    def _recency_score(self, published_at, half_life_days: float = 5.0) -> float:
        if not published_at:
            return 0.0
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        now = current_datetime_et()
        delta_days = max((now - published_at).total_seconds() / 86400.0, 0.0)
        tau = half_life_days / math.log(2)  # score halves every half_life_days
        return math.exp(-delta_days / tau)
