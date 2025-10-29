from sqlalchemy.orm import Session
from clients.openai_client import OpenAIClient
from db.models import Security
from sqlalchemy import select, bindparam, text
from pgvector.sqlalchemy import Vector
from investment_engine.math.similarity_backend import sa_bind_vector, sa_cosine_similarity_expr

class ThemeService:
    def __init__(self, db: Session, client: OpenAIClient):
        self.db = db
        self.client = client
    
    def get_embedded_query(self, criteria):
        theme = criteria["theme_summary"]
        keywords = list(criteria["keywords"])
        sectors = list(criteria["sectors"])
        query = f"{theme} Keywords: {', '.join(keywords)}. Sectors: {', '.join(sectors)}"
        return self.client.get_embeddings(query)
    
    def vector_search_within_candidates(
        self, 
        query_vec: list[float], 
        candidate_ids: list[int] | None = None, 
        exclude_ids: list[int] | None = None, 
        limit: int = 10, 
        probes: int = 10
    ):
        
        q_param = sa_bind_vector("q", query_vec)
        
        sim_expr = sa_cosine_similarity_expr(Security.description_embedding, q_param).label("similarity")
        
        self.db.execute(text(f"SET ivfflat.probes = {probes}"))
        stmt = select(Security, sim_expr).where(Security.description_embedding.isnot(None))

        if candidate_ids:
            stmt = stmt.where(Security.id.in_(candidate_ids))
        
        if exclude_ids:
            stmt = stmt.where(~Security.id.in_(exclude_ids))

        stmt = stmt.order_by(Security.description_embedding.cosine_distance(q_param)).limit(limit)
        rows = self.db.execute(stmt).all()
        
        return [
            {
                "id": row[0].id,
                "ticker": row[0].ticker,
                "name": row[0].name,
                "description": row[0].description,
                "industry": row[0].industry,
                "currency": row[0].currency,
                "exchange": row[0].exchange,
                "type": row[0].type,
                "market_cap_usd": row[0].market_cap_usd,
                "similarity": float(row[1])
            }
            for row in rows
        ]