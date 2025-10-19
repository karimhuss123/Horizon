from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional

class HoldingIn(BaseModel):
    ticker: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    weight_pct: float = Field(..., ge=0.01)
    rationale: Optional[str] = None

class BasketGenerateRequest(BaseModel):
    user_prompt: str = Field(..., min_length=3)

class BasketRegenerateRequest(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    holdings: List[HoldingIn] = Field(..., min_items=1)
    
    @model_validator(mode="after")
    def check_holdings_total_weight(self):
        total = sum((h.weight_pct for h in self.holdings))
        if total != 100:
            raise ValueError(f"Holdings weight_pct must sum to 100 (got {total:.4f})")
        return self
    
    user_prompt: str = Field(..., min_length=3)

class BasketStatusUpdateRequest(BaseModel):
    basket_id: int

class BasketDeleteRequest(BaseModel):
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

class HoldingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    ticker: Optional[str]
    name: Optional[str]
    weight_pct: float
    rationale: Optional[str] = None

class BasketRegenerationResponse(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    holdings: List[HoldingOut]

class BasketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    holdings: List[HoldingOut]

class BasketListResponse(BaseModel):
    items: List[BasketResponse]
    total: int