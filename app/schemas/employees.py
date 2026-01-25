from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=2, max_length=50)
    full_name: str = Field(min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_name: Optional[str] = None
    join_date: Optional[str] = None
    status: str = "active"

class EmployeeUpdate(EmployeeCreate):
    pass
