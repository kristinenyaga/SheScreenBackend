from pydantic import BaseModel, EmailStr
from typing import Optional,List
from enum import Enum
from datetime import date


class UserRole(str, Enum):
    PATIENT = "PATIENT"
    STAFF = "STAFF"


class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: EmailStr
    date_of_birth: date | None = None
    is_parent: bool = False
    region: Optional[str] = None  
    role: UserRole = UserRole.PATIENT


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_parent: Optional[bool] = None
    region: Optional[str] = None

class RiskAssessmentUpdate(BaseModel):
    number_of_sexual_partners: int
    first_sexual_intercourse_age: int
    smoking_status: str
    stds_history: str

class RiskAssessmentCreate(BaseModel):
    number_of_sexual_partners: int
    first_sexual_intercourse_age: int
    smoking_status: str
    stds_history: str
    hpv_test_result: str = "Negative"  # Default to Negative if not provided
    hpv_vaccinated: bool = False  # Default to False if not provided

class UserIn(BaseModel):
    email:EmailStr
    password: str

class UserInDBBase(UserBase):
    id: int


class UserInDB(UserInDBBase):
    hashed_password: str

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
    screening_type:str
    

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

class UserLocation(BaseModel):
    region: Optional[str]
    message: str


class FacilityRecommendations(BaseModel):
    nearby_facilities: list[RecommendedFacility]
    other_facilities: list[RecommendedFacility]
    total_count: int


class PredictionResult(BaseModel):
    cluster: int
    interpretation: str
    screening_recommendations: ScreeningRecommendation


class RiskPredictionSummary(BaseModel):
    risk_level: str
    next_steps: list[str]
    reason: str
    additional_services: list[str]
    # location_note: str


class RecommendedFacilitiesResponse(BaseModel):
    nearby_facilities: List[FacilityResponse]
    other_facilities: List[FacilityResponse]
    total_count: int

class RiskPredictionResponse(BaseModel):
    user_id: int
    user_location: UserLocation
    risk_assessment: dict
    prediction: PredictionResult
    recommended_facilities: RecommendedFacilitiesResponse
    summary: RiskPredictionSummary

class RiskPredictionInDB(BaseModel):
    id: int
    user_id: int
    # Risk assessment data
    number_of_sexual_partners: int
    first_sexual_intercourse_age: int
    smoking_status: str
    stds_history: str
    hpv_test_result: str
    hpv_vaccinated: bool
    age_at_assessment: int
    # Prediction results
    cluster: int
    interpretation: str
    risk_level: str
    recommended_screenings: Optional[str]
    reason: Optional[str]
    urgency: Optional[str]
    frequency: Optional[str]
    additional_services: Optional[str]
    created_at: date



class RiskPredictionHistory(BaseModel):
    predictions: list[RiskPredictionInDB]
    total_count: int
    latest_prediction: Optional[RiskPredictionInDB]

    class Config:
        from_attributes = True
