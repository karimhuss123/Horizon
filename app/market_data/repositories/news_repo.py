from sqlalchemy.orm import Session
from app.db.models import News
from app.market_data.repositories.security_repo import SecurityRepo

class NewsRepo:
    def __init__(self, db: Session):
        self.db = db
        self.securities = SecurityRepo(db)
    
    def get_news_by_url(self, url):
        return self.db.query(News).filter_by(url=url).first()

    def get_news_by_url_list(self, url_list):
        return (
            self.db.query(News)
            .filter(News.url.in_(url_list))
            .all()
        )
    
    def create_news(self, security_id, data):
        if not self.securities.get_security(security_id):
            return RuntimeError("Security does not exist.")
        
        # If news already exists in the DB
        if self.get_news_by_url(data["url"]):
            return
        
        news = News(
            security_id = security_id,
            title = data["title"],
            summary = data["summary"],
            url = data["url"],
            source = data["source"],
            published_at = data["published_at"],
            text_embedding = data["text_embedding"]
        )
        
        self.db.add(news)
        self.db.commit()
        return news