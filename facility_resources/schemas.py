from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ResourceCategory(str, Enum):
    equipment = "equipment"
    consumable = "consumable"
    medication = "medication"


class ResourceBase(BaseModel):
    quantity_available: int
    low_stock_threshold: Optional[int] = 5


class ResourceCreate(ResourceBase):
    facility_id: int


class ResourceResponse(ResourceBase):
    id: int
    facility_id: int
    resource_type_id:int


class ResourceUpdate(BaseModel):
    quantity_available: Optional[int] = None
    low_stock_threshold: Optional[int] = None

    class Config:
        from_attributes = True
