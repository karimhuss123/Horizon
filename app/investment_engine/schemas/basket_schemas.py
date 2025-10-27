from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional
from investment_engine.schemas.holding_schemas import HoldingIn, HoldingOut

class BasketGenerateRequest(BaseModel):
    user_prompt: str = Field(..., min_length=3)

class BasketRegenerateRequest(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    holdings: List[HoldingIn] = Field(..., min_items=1)
    user_prompt: str = Field(..., min_length=3)
    
    @model_validator(mode="after")
    def check_holdings_total_weight(self):
        total = sum((h.weight_pct for h in self.holdings))
        if total != 100:
            raise ValueError(f"Holdings weight_pct must sum to 100 (got {total:.4f})")
        return self

class BasketIdRequest(BaseModel):
    basket_id: int

class BasketUpdateRequest(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: str = Field(..., min_length=1)
    holdings: List[HoldingIn] = Field(..., min_items=1)
    
    @model_validator(mode="after")
    def check_holdings_total_weight(self):
        total = sum((h.weight_pct for h in self.holdings))
        if total != 100:
            raise ValueError(f"Holdings weight_pct must sum to 100 (got {total:.4f})")
        return self

class BasketRegenerationResponse(BaseModel):
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

class BasketSuggestionItem(BaseModel):
    ticker: str
    name: str
    rationale: str
    action: str
    source_url: str