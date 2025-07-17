from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CervicalCancerServiceOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class PatientBillableItemBase(BaseModel):
    patient_id: int
    service_id: int
    service_cost_id: Optional[int] = None

    base_cost: Optional[float] = None
    nhif_covered: bool = False
    nhif_amount: float = 0
    patient_amount: float = 0
    paid: bool = False


class PatientBillableItemCreate(PatientBillableItemBase):
    pass


class PatientBillableItemUpdate(BaseModel):
    paid: Optional[bool]


class PatientBillableItemOut(PatientBillableItemBase):
    id: int
    date_created: datetime
    service: Optional[CervicalCancerServiceOut]

    class Config:
        orm_mode = True


class PatientBillableItemSummary(BaseModel):
    items: list[PatientBillableItemOut]
    total_cost: float

    class Config:
        orm_mode = True
