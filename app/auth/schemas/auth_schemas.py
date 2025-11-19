from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing import Annotated

SixDigitCode = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^\d{6}$", min_length=6, max_length=6)]

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)

class CodeVerifyRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    code: SixDigitCode
