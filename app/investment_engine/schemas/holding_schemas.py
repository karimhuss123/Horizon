from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional

class HoldingIn(BaseModel):
    ticker: str = Field(..., min_length=1)
    weight_pct: float = Field(..., ge=0.01)
    rationale: Optional[str] = None

class HoldingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    ticker: Optional[str]
    name: Optional[str]
    weight_pct: float
    rationale: Optional[str] = None