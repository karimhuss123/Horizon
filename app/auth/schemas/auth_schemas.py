from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

SixDigitCode = Annotated[str, 
    Field(pattern=r"^\d{6}$")
]

class LoginRequest(BaseModel):
    email: EmailStr

class CodeVerifyRequest(BaseModel):
    email: EmailStr
    code: SixDigitCode
