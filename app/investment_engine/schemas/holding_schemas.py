from pydantic import BaseModel, Field, ConfigDict, StringConstraints
from typing import Optional, Annotated

TickerStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
RationaleStr = Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)]

class HoldingIn(BaseModel):
    ticker: TickerStr
    weight_pct: float = Field(..., ge=0.01)
    rationale: Optional[RationaleStr] = None
    model_config = ConfigDict(extra="forbid")

class HoldingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    security_id: Optional[int]
    ticker: str
    name: str
    weight_pct: float = Field(..., ge=0.01, le=100)
    rationale: Optional[str] = None