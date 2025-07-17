from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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

    class Config:
        orm_mode = True
