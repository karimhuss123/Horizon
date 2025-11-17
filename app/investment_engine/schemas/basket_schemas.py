from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional
from investment_engine.schemas.holding_schemas import HoldingIn, HoldingOut

class BasketGenerateRequest(BaseModel):
    user_prompt: str = Field(..., min_length=3, max_length=1000)

class BasketRegenerateRequest(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1500)
    holdings: List[HoldingIn] = Field(..., min_items=1, max_items=50)
    user_prompt: str = Field(..., min_length=3, max_length=1000)
    
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
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1500)
    status: str = Field(..., min_length=1, max_length=50)
    holdings: List[HoldingIn] = Field(..., min_items=1, max_items=50)
    
    @model_validator(mode="after")
    def check_holdings_total_weight(self):
        total = sum((h.weight_pct for h in self.holdings))
        if total != 100:
            raise ValueError(f"Holdings weight_pct must sum to 100 (got {total:.4f})")
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

class BasketSuggestionItem(BaseModel):
    security_id: int
    ticker: str
    name: str
    rationale: str
    action: str
    source_url: str

class AcceptRegenerationRequest(BaseModel):
    id: int