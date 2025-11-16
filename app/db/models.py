from sqlalchemy import (
    Column, String, Float, Enum, ForeignKey, DateTime, Integer, ARRAY, Boolean, func
)
from sqlalchemy.orm import relationship
import enum
from db.db import Base
from pgvector.sqlalchemy import Vector
from db.utils.time import current_datetime_utc

class RiskLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class BasketStatus(enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=current_datetime_utc)

class LoginCode(Base):
    __tablename__ = "login_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=current_datetime_utc)

    user = relationship("User")

class Basket(Base):
    __tablename__ = "baskets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    prompt_text = Column(String, nullable=False)
    description = Column(String)
    description_embedding = Column(Vector(1536))
    status = Column(Enum(BasketStatus))

    keywords = Column(ARRAY(String), nullable=True)
    sectors = Column(ARRAY(String), nullable=True)
    regions = Column(ARRAY(String), nullable=True)
    market_cap_min_usd = Column(Float)
    market_cap_max_usd = Column(Float)
    
    # risk_level = Column(Enum(RiskLevel))
    
    created_at = Column(DateTime(timezone=True), default=current_datetime_utc)
    updated_at = Column(DateTime(timezone=True), onupdate=current_datetime_utc)

    holdings = relationship("Holding", back_populates="basket", cascade="all, delete-orphan")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True)
    basket_id = Column(Integer, ForeignKey("baskets.id", ondelete="CASCADE"))
    security_id = Column(Integer, ForeignKey("securities.id"))
    weight_pct = Column(Float, nullable=False)
    rationale = Column(String)
    
    @property
    def ticker(self) -> str | None:
        return self.security.ticker if self.security else None
    @property
    def name(self) -> str | None:
        return self.security.name if self.security else None

    basket = relationship("Basket", back_populates="holdings")
    security = relationship("Security", back_populates="holdings")


class Security(Base):
    __tablename__ = "securities"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    description = Column(String)
    description_embedding = Column(Vector(1536))
    industry = Column(String)
    gics_sector = Column(String)
    region = Column(String)
    currency = Column(String)
    exchange = Column(String)
    type = Column(String)
    market_cap_usd = Column(Float)
    
    news = relationship("News", back_populates="security", cascade="all, delete-orphan", single_parent=True)
    holdings = relationship("Holding", back_populates="security")

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False, index=True)
    title = Column(String)
    summary = Column(String)
    url = Column(String, unique=True)
    source = Column(String)
    published_at = Column(DateTime(timezone=True))
    text_embedding = Column(Vector(1536))
    injected_at = Column(DateTime(timezone=True), default=current_datetime_utc)
    
    security = relationship("Security", back_populates="news")