from pydantic import BaseModel, Field
from typing import List

class RoleCreate(BaseModel):
    key: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    permissions: List[str]

class RoleUpdate(RoleCreate):
    pass
