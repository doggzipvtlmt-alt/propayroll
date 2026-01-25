from pydantic import BaseModel, Field
from typing import Optional

class LeaveCreate(BaseModel):
    employee_id: str = Field(min_length=10)
    employee_name: Optional[str] = None
    leave_type: str
    start_date: str
    end_date: str
    reason: Optional[str] = None

class LeaveDecision(BaseModel):
    comment: Optional[str] = None
