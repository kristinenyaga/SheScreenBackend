from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class FacilityUserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    phone_number:str


class FacilityUserCreate(FacilityUserBase):
    hashed_password: str
    facility_id: int


class FacilityUserResponse(FacilityUserBase):
    id: int
    facility_id: int
