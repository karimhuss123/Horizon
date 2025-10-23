from pydantic import BaseModel, Field, ConfigDict, RootModel
from typing import List, Optional

class TickerItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int
    ticker: str = Field(..., min_length=1)
    name: Optional[str] = Field(None)