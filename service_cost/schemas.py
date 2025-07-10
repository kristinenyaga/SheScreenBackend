from pydantic import BaseModel
from typing import Optional

class ServiceCostBase(BaseModel):
  base_cost:Optional[float]=None
  nhif_covered:bool=True
  out_of_pocket: Optional[float] = None
  insurance_copay_amount: Optional[float] = None


class ServiceCostCreate(ServiceCostBase):
    facility_id: int 
    service_id: int



class ServiceCostUpdate(BaseModel):
    base_cost: Optional[float] = None
    nhif_covered: Optional[bool] = None
    out_of_pocket: Optional[float] = None
    insurance_copay_amount: Optional[float] = None


class CervicalCancerServiceBase(BaseModel):
    name: str
    description: str | None = None

class ServiceCostResponse(ServiceCostBase):
    id: int
    facility_id: int
    service: CervicalCancerServiceBase


    class Config:
        from_attributes = True
