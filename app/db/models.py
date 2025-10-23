from sqlalchemy import (
    Column, String, Float, Enum, ForeignKey, DateTime, func, Integer
)
from sqlalchemy.orm import relationship, declarative_base
import enum
from db.db import Base
from pgvector.sqlalchemy import Vector

class RiskLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class BasketStatus(enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"

class Basket(Base):
    __tablename__ = "baskets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    prompt_text = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(BasketStatus))

    # regions = Column(String)
    # include_sectors = Column(String)
    # exclude_sectors = Column(String)
    # market_cap_min_usd = Column(Float)
    # market_cap_max_usd = Column(Float)
    # risk_level = Column(Enum(RiskLevel))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
    currency = Column(String)
    exchange = Column(String)
    type = Column(String)
    market_cap_usd = Column(Float)
    
    holdings = relationship("Holding", back_populates="security")