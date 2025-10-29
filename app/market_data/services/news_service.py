from market_data.repositories.news_repo import NewsRepo
from clients.openai_client import OpenAIClient
from sqlalchemy.orm import Session
from datetime import datetime
import yfinance as yf

class NewsService:
    def __init__(self, db: Session, client: OpenAIClient):
        self.db = db
        self.news = NewsRepo(db)
        self.client = client
    
    def process_news_for_securities(self, securities):
        news_added_array = []
        for security in securities:
            news = self.get_news(security["ticker"])
            news_added = self.process_news(security["id"], news)
            news_added_array.append(news_added)
        return news_added_array
    
    def get_news(self, ticker):
        yf_data = yf.Ticker(ticker)
        return yf_data.news

    def process_news(self, security_id, news):
        if not news:
            return
        urls = [self.normalize_url(item["content"]["canonicalUrl"]["url"]) for item in news]
        missing_urls = self.get_missing_urls(urls)
        if not missing_urls:
            return
        missing_news = [item for item, url in zip(news, urls) if url in missing_urls]
        text_to_embed_list = [" ".join([item["content"]["title"], item["content"]["summary"]]) for item in missing_news]
        text_embeddings_list, _ = self.client.get_embeddings_batch(text_to_embed_list)
        output_list = []
        for item, embedding in zip(missing_news, text_embeddings_list):
            contents = item["content"]
            data = {
                "title": contents["title"],
                "summary": contents["summary"],
                "url": self.normalize_url(contents["canonicalUrl"]["url"]),
                "source": contents["provider"]["displayName"] + "-" + contents["provider"]["url"],
                "published_at": datetime.fromisoformat(contents["pubDate"].replace("Z", "+00:00")),
                "text_embedding": embedding
            }
            news_obj = self.news.create_news(security_id, data)
            output_list.append(news_obj)
        return output_list
    
    def get_missing_urls(self, urls):
        input_set = set(urls)
        existing_news = self.news.get_news_by_url_list(urls)
        existing_urls_set = {self.normalize_url(news.url) for news in existing_news}
        return input_set - existing_urls_set

    def normalize_url(self, url):
        return url.strip().split("?")[0] # Make lowercase (?)