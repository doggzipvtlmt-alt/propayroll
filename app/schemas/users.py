from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = None
    role_key: str = Field(min_length=2, max_length=50)
    status: str = "active"
    dob: Optional[str] = None
    pin: Optional[str] = Field(default=None, min_length=4, max_length=12)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role_key: Optional[str] = None
    dob: Optional[str] = None
    pin: Optional[str] = Field(default=None, min_length=4, max_length=12)

class UserStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|inactive)$")
