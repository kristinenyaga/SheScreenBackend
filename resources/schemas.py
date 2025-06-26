from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ResourceCategory(str, Enum):
    equipment = "equipment"
    consumable = "consumable"
    medication = "medication"


class ResourceBase(BaseModel):
    name: str
    category: ResourceCategory
    quantity_available: int
    unit_of_measure: str
    low_stock_threshold: Optional[int] = 5


class ResourceCreate(ResourceBase):
    facility_id: int


class ResourceResponse(ResourceBase):
    id: int
    facility_id: int


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ResourceCategory] = None
    quantity_available: Optional[int] = None
    unit: Optional[str] = None
    low_stock_threshold: Optional[int] = None

    class Config:
        from_attributes = True
