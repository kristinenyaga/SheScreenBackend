from pydantic import BaseModel
from datetime import datetime


class Resource(BaseModel):
    name: str
    unit_of_measure: str
    quantity_available: int
    low_stock_threshold: int
    classification:str
    resource_type:str


class SimplePatient(BaseModel):
    id: int
    first_name: str
    last_name: str
    patient_code: str

    class Config:
        orm_mode = True


class SimpleService(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class UsageLogBase(BaseModel):
    patient_id: int
    service_id: int
    resource_id: int
    quantity_used: float


class UsageLogCreate(UsageLogBase):
    pass


class UsageLogRead(BaseModel):
    id: int
    date_used: datetime
    resource:Resource
    patient:SimplePatient
    service:SimpleService

    class Config:
        orm_mode = True
