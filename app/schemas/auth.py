from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    company_id: str = Field(min_length=5)
    identifier: str = Field(min_length=3)
    dob_or_pin: str = Field(min_length=2)
