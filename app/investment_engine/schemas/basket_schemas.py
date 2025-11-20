from pydantic import BaseModel, Field, ConfigDict, model_validator, StringConstraints
from typing import List, Optional, Annotated
from investment_engine.schemas.holding_schemas import HoldingIn, HoldingOut
from db.models import BasketStatus
from core.errors.messages import messages

PromptStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1000)]
NameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
DescriptionStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1500)]
NonEmptyLongStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]

class BasketGenerateRequest(BaseModel):
    user_prompt: PromptStr

class BasketRegenerateRequest(BaseModel):
    id: int = Field(..., gt=0)
    name: NameStr
    description: DescriptionStr
    holdings: List[HoldingIn] = Field(..., min_items=1, max_items=25)
    user_prompt: PromptStr
    
    @model_validator(mode="after")
    def check_holdings_total_weight(self):
        total = sum((h.weight_pct for h in self.holdings))
        if total != 100:
            raise ValueError(messages.total_holding_weights_not_100)
        return self

class BasketIdRequest(BaseModel):
    basket_id: int = Field(..., gt=0)

class AcceptRegenerationRequest(BaseModel):
    id: int = Field(..., gt=0)

class BasketUpdateRequest(BaseModel):
    id: int = Field(..., gt=0)
    name: NameStr
    description: DescriptionStr
    status: BasketStatus
    holdings: List[HoldingIn] = Field(..., min_items=1, max_items=50)
    
    @model_validator(mode="after")
    def check_holdings_total_weight(self):
        total = sum((h.weight_pct for h in self.holdings))
        if total != 100:
            raise ValueError(messages.total_holding_weights_not_100)
        return self

    @model_validator(mode="after")
    def check_unique_tickers(self):
        seen = set()
        for h in self.holdings:
            key = h.ticker.strip().upper()
            if key in seen:
                raise ValueError(messages.duplicate_tickers.format(ticker=h.ticker))
            seen.add(key)
        return self

class BasketRegenerationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    holdings: List[HoldingOut]

class BasketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int
    name: str
    description: Optional[str] = None
    keywords: Optional[List[str]]
    sectors: Optional[List[str]]
    regions: Optional[List[str]]
    status: Optional[str] = None
    holdings: List[HoldingOut]

class BasketListResponse(BaseModel):
    items: List[BasketResponse]
    total: int
