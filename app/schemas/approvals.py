from pydantic import BaseModel, Field
from typing import Optional

class ApprovalCreate(BaseModel):
    entity_type: str = Field(min_length=2, max_length=50)
    entity_id: str = Field(min_length=1)
    workflow_key: str = Field(min_length=2, max_length=50)
    current_step: int = 1

class ApprovalDecision(BaseModel):
    comment: Optional[str] = None
