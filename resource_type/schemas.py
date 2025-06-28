from pydantic import BaseModel
from typing import Optional


class ResourceTypeBase(BaseModel):
    name: str
    unit_of_measure: str


class ResourceTypeCreate(ResourceTypeBase):
    pass


class ResourceTypeUpdate(BaseModel):
    name: Optional[str] = None
    unit_of_measure: Optional[str] = None


class ResourceTypeResponse(ResourceTypeBase):
    id: int

    class Config:
        from_attributes = True
