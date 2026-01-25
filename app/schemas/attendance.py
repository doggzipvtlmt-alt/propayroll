from pydantic import BaseModel
from typing import Optional

class AttendanceCreate(BaseModel):
    date: str
    employee_id: str
    employee_name: Optional[str] = None
    department: Optional[str] = None
    status: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
