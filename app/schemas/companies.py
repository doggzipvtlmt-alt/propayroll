from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    legal_name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass
