from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class FacilityUserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    phone_number:str


class LoginRequest(BaseModel):
    email: EmailStr
    hashed_password: str


class TokenData(BaseModel):
    email: Optional[str] = None
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class FacilityUserCreate(FacilityUserBase):
    hashed_password: str
    facility_id: int


class FacilityUserResponse(FacilityUserBase):
    id: int
    facility_id: int

    class Config:
        from_attributes = True
