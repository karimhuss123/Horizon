import os, math
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db.db import get_db
from app.db.models import Security
from openai import OpenAI
from dotenv import load_dotenv

# To run (inside /app directory):
# python -m db.load_securities
# Note: make sure that table exists in database

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
MODEL = "text-embedding-3-small"

def clean_market_cap(x):
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return None
        return float(x)
    except:
        return None

def embed_texts(texts):
    """Takes a list of strings and returns list of embeddings (or None)."""
    # replace None with empty string
    valid_texts = [t or "" for t in texts]
    if not any(valid_texts):
        return [None] * len(texts)
    resp = client.embeddings.create(model=MODEL, input=valid_texts)
    return [d.embedding if (texts[i] and texts[i].strip()) else None for i, d in enumerate(resp.data)]

def main():
    # 1) connect to DB
    db_gen = get_db()
    db: Session = next(db_gen)

    try:
        # 2) load and clean CSV
        df = pd.read_csv(
            "./db/data/securities_data.csv",
            usecols=[
                "ticker", "name", "description", "industry", "currency",
                "exchange", "type", "market_cap_usd", "gics_sector", "region"
            ],
            dtype={"ticker": "string"},     # keep ticker as string
            keep_default_na=False           # do NOT treat 'NA'/'N/A' as NaN
        )
        
        df["market_cap_usd"] = df["market_cap_usd"].apply(clean_market_cap)
        df = df.where(pd.notnull(df), None)
        df.drop_duplicates(subset=['ticker'])
        

        records = df.to_dict(orient="records")
        chunk_size = 500
        total = 0

        # 3) process in chunks
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            descs = [r.get("description") for r in chunk]
            embs = embed_texts(descs)

            # attach embeddings to records
            for j, r in enumerate(chunk):
                r["description_embedding"] = embs[j]

            # 4) upsert to DB
            stmt = insert(Security).values(chunk)
            update_cols = {
                c.name: getattr(stmt.excluded, c.name)
                for c in Security.__table__.columns
                if c.name not in ("id", "ticker")
            }
            db.execute(
                stmt.on_conflict_do_update(
                    index_elements=[Security.ticker],
                    set_=update_cols
                )
            )
            db.commit()
            total += len(chunk)

        print(f"Upserted {total} securities (with embeddings) successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
