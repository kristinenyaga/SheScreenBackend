
from pydantic import BaseModel
from typing import Optional


class ResourceBase(BaseModel):
    name: str
    unit_of_measure: str
    quantity_available: int
    low_stock_threshold: int
    classification: Optional[str] = None
    resource_type: Optional[str] = None

class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    unit_of_measure: Optional[str] = None
    quantity_available: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    classification: Optional[str] = None
    resource_type: Optional[str] = None


class ResourceOut(ResourceBase):
    id: int
    classification:str
    resource_type:str

    class Config:
        orm_mode = True
