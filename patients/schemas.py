from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import date, datetime



class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    area_of_residence: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None



class PatientCreate(PatientBase):
    created_by_id: int



class PatientUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    area_of_residence: Optional[str]
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class PatientOut(PatientBase):
    id: int
    created_by_id: int
    created_at: datetime
    patient_code: str


    model_config = {
        "from_attributes": True
    }



class PatientWithRisk(PatientOut):
    risk_level: Optional[str] = None

    class Config:
        from_attributes = True

class RiskAssessmentUpdate(BaseModel):
    number_of_sexual_partners: int
    first_sexual_intercourse_age: int
    smoking_status: str
    stds_history: str


class RiskAssessmentCreate(BaseModel):
    patient_id: int
    number_of_sexual_partners: int
    first_sexual_intercourse_age: int
    smoking_status: str
    stds_history: str
    hpv_test_result: str = "Negative"  # Default to Negative if not provided
    hpv_vaccinated: bool = False  # Default to False if not provided


class PatientIn(BaseModel):
    email: EmailStr
    password: str




class TokenData(BaseModel):
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


# Risk Prediction Response Schemas
class ScreeningRecommendation(BaseModel):
    recommended_screenings: list[str]
    reason: str
    urgency: str
    frequency: str
    additional_services: list[str]


class FacilityEquipment(BaseModel):
    name: str
    quantity: int


class RecommendedFacility(BaseModel):
    facility_id: int
    facility_name: str
    region: str
    contact_number: Optional[str]
    screening_type: str
    available_equipment: list[FacilityEquipment]
    distance_priority: str


class RecommendedFacilityQuery(BaseModel):
    screening_type: str


class ServiceCostResponse(BaseModel):
    base_cost: Optional[float]
    nhif_covered: bool
    out_of_pocket: Optional[float]
    insurance_copay_amount: Optional[float]


class FacilityResponse(BaseModel):
    id: int
    name: str
    region: str
    contact_number: str
    service_cost: Optional[ServiceCostResponse]



class PredictionResult(BaseModel):
    interpretation: str
    screening_recommendations: ScreeningRecommendation
    risk_probability: float
    
class RiskPredictionSummary(BaseModel):
    risk_level: str
    next_steps: list[str]
    reason: str
    additional_services: list[str]
    availability:list[dict]
    # location_note: str


class RiskPredictionResponse(BaseModel):
    id: int
    patient_id: int
    risk_assessment: dict
    prediction: PredictionResult
    summary: RiskPredictionSummary



class RiskPredictionInDB(BaseModel):
    id: int
    patient_id: int
    # Risk assessment data
    number_of_sexual_partners: int
    first_sexual_intercourse_age: int
    smoking_status: str
    stds_history: str
    hpv_test_result: str
    hpv_vaccinated: bool
    age_at_assessment: int
    # Prediction results
    interpretation: str
    risk_level: str
    recommended_screenings: Optional[str]
    reason: Optional[str]
    urgency: Optional[str]
    frequency: Optional[str]
    additional_services: Optional[str]
    created_at: date
    risk_probability: float




class RiskPredictionHistory(BaseModel):
    predictions: list[RiskPredictionInDB]
    total_count: int
    latest_prediction: Optional[RiskPredictionInDB]

    class Config:
        from_attributes = True
