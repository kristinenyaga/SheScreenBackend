from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class LabTestStatus(str, Enum):
    pending = "pending"
    completed = "completed"


class LabTestCreate(BaseModel):
    recommendation_id: int
    service_id: int
    patient_id: int
    ordered_by_id: int


class LabTestUpdate(BaseModel):
    result: Optional[str]
    status: Optional[LabTestStatus]
    entered_by_id: Optional[int]

# schemas.py

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


class SimpleUser(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class LabTestOut(BaseModel):
    id: int
    recommendation_id: int
    service: SimpleService
    patient: SimplePatient
    result: Optional[str]
    status: LabTestStatus
    ordered_by: SimpleUser
    entered_by_id: Optional[int]
    date_ordered: datetime
    date_completed: Optional[datetime]

    class Config:
        orm_mode = True
