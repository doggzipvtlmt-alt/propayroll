from pydantic import BaseModel
from typing import Any, List

class PaginatedResult(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
