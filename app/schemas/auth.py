from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class LoginRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=6)


class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=20)
    role_requested: Literal["HR", "MD", "EMPLOYEE", "FINANCE"]
