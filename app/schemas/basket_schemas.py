from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class BasketGenerateRequest(BaseModel):
    user_prompt: str = Field(..., min_length=3)

class BasketUpdateRequest(BaseModel):
    basket_id: int

class BasketStatusChangeRequest(BaseModel):
    basket_id: int
    status: str

class HoldingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    ticker: Optional[str]
    name: Optional[str]
    weight_pct: float
    rationale: Optional[str] = None

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