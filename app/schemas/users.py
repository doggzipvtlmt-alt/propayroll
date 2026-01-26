from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = None
    role_key: str = Field(min_length=2, max_length=50)
    status: str = "active"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role_key: Optional[str] = None

class UserStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|inactive)$")
