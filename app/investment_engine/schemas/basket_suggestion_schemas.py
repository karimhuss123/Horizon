from pydantic import BaseModel, StringConstraints
from typing import Annotated

NonEmptyLongStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]

class BasketSuggestionItem(BaseModel):
    security_id: int
    ticker: str
    name: NonEmptyLongStr
    rationale: NonEmptyLongStr
    action: str
    source_url: str