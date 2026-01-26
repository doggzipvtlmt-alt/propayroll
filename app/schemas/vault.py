from pydantic import BaseModel, Field
from typing import Optional, List

class VaultCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    username: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    password: str = Field(min_length=1)
    tags: List[str] = []

class VaultUpdate(BaseModel):
    title: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    tags: Optional[List[str]] = None

class VaultResetSecret(BaseModel):
    notes: Optional[str] = None
    password: Optional[str] = None
