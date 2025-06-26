from pydantic import BaseModel
from typing import Optional

class ServiceCostBase(BaseModel):
  service_name:str
  base_cost:Optional[float]=None
  nhif_covered:bool=True
  out_of_pocket: Optional[float] = None
  insurance_copay_amount: Optional[float] = None


class ServiceCostCreate(ServiceCostBase):
    facility_id: int 


class ServiceCostUpdate(BaseModel):
    service_name: Optional[str] = None
    base_cost: Optional[float] = None
    nhif_covered: Optional[bool] = None
    out_of_pocket: Optional[float] = None
    insurance_copay_amount: Optional[float] = None


class ServiceCostResponse(ServiceCostBase):
    id: int
    facility_id: int

    class Config:
        from_attributes = True
