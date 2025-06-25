from pydantic import BaseModel
from typing import Optional


class FacilityBase(BaseModel):
    name: str
    region: str
    contact_number: Optional[str] = None


class FacilityCreate(FacilityBase):
    pass


class FacilityResponse(FacilityBase):
    id: int
    name: str
    region: str

    class Config:
        orm_mode = True
