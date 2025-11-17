from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

SixDigitCode = Annotated[str, 
    Field(pattern=r"^\d{6}$")
]

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)

class CodeVerifyRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    code: SixDigitCode
