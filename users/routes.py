from datetime import timedelta
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from users import auth, models, schemas, security
from users.db import get_db
from users.risk_prediction import predict_risk, RiskPredictionData
from facility.models import Facility
from facility_resources.models import FacilityResource
from service.models import CervicalCancerService
from service_resource_requirement.models import ServiceResourceRequirement
from service_cost.models import ServiceCost
from chat.prompts import generate_context, qa_template
from groq import Groq

from dotenv import load_dotenv, find_dotenv
import os
import numpy as np

load_dotenv(find_dotenv())

client = Groq()

router = APIRouter()


# def find_facilities_with_screening_equipment(db: Session, screening_types: list, user_region: str = None):
#     facilities_with_services = []
    
#     equipment_mapping = {
#         "Pap Smear": ["Speculum", "Cytology Equipment", "Pap Smear Kit"],
#         "HPV DNA Test": ["HPV Testing Kit", "PCR Machine", "DNA Testing Equipment"], 
#         "HPV Vaccine": ["Vaccine Storage", "Refrigeration Unit", "HPV Vaccine"]
#     }
    
#     for screening_type in screening_types:
#         if screening_type in equipment_mapping:
#             equipment_names = equipment_mapping[screening_type]
            
#             # Build base query for facilities with required equipment
#             base_query = db.query(Facility).join(FacilityResource).filter(
#                 FacilityResource.category == ResourceCategory.equipment,
#                 FacilityResource.name.in_(equipment_names),
#                 FacilityResource.quantity_available > 0
#             ).distinct()
            
#             same_region_facilities = []
#             other_region_facilities = []
            
#             all_facilities = base_query.all()
            
#             for facility in all_facilities:
#                 facility_info = {
#                     "facility_id": facility.id,
#                     "facility_name": facility.name,
#                     "region": facility.region,
#                     "contact_number": facility.contact_number,
#                     "screening_type": screening_type,
#                     "available_equipment": [],
#                     "distance_priority": "same_region" if user_region and facility.region.lower() == user_region.lower() else "other_region"
#                 }
                
#                 available_equipment = db.query(FacilityResource).filter(
#                     FacilityResource.facility_id == facility.id,
#                     FacilityResource.category == ResourceCategory.equipment,
#                     FacilityResource.name.in_(equipment_names),
#                     FacilityResource.quantity_available > 0
#                 ).all()
                
#                 for equipment in available_equipment:
#                     facility_info["available_equipment"].append({
#                         "name": equipment.name,
#                         "quantity": equipment.quantity_available
#                     })
                
#                 if user_region and facility.region.lower() == user_region.lower():
#                     same_region_facilities.append(facility_info)
#                 else:
#                     other_region_facilities.append(facility_info)
            
#             facilities_with_services.extend(same_region_facilities)
#             facilities_with_services.extend(other_region_facilities)
    
#     return facilities_with_services

# @router.post("/recommended-facilities", response_model=list[schemas.FacilityResponse])
# def get_recommended_facilities(service_name: schemas.RecommendedFacilityQuery, db: Session = Depends(get_db)):
#     service = db.query(CervicalCancerService).filter(
#         CervicalCancerService.name == service_name.screening_type).first()
#     if not service:
#         raise HTTPException(status_code=404, detail="Service not found")
#     print("service",service.__dict__)
#     required_resources = db.query(ServiceResourceRequirement).filter(
#         ServiceResourceRequirement.service_id == service.id
#     ).all()


#     facilities = db.query(Facility).join(ServiceCost).filter(
#         ServiceCost.service_id == service.id).all()

#     recommended_facilities = []

#     for facility in facilities:
#         has_all_resources = True

#         for requirement in required_resources:
#             facility_resource = db.query(FacilityResource).filter_by(
#                 facility_id=facility.id,
#                 resource_type_id=requirement.resource_type_id
#             ).first()

#             if not facility_resource or facility_resource.quantity_available < requirement.required_quantity:
#                 has_all_resources = False
#                 break

#         if has_all_resources:
#             recommended_facilities.append(facility)

#     return recommended_facilities


@router.post("/register", response_model=schemas.UserInDBBase)
async def register(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(user_in.password)

    db_user = models.User(
        email=user_in.email,
        first_name="", 
        last_name="",  
        phone_number="", 
        date_of_birth=None, 
        is_parent=False,
        role=models.UserRole.PATIENT,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username).first()
    if not user or not security.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.patch("/profile",response_model=schemas.UserInDBBase)
async def profile(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
        db_user = db.query(models.User).filter(
            models.User.id == current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


@router.get("/profile", response_model=schemas.UserInDBBase)
async def get_loggedin_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.get("/conversation")
async def read_conversation(
    query: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_user = auth.get_user(db, email=current_user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    context = generate_context(db_user)
    prompt = qa_template.format(
        email=db_user.email,
        context=context,
        question=query
    )

    def classify_intent(query: str) -> str:
        q = query.lower()
        if "what is" in q or "definition" in q:
            return "definition"
        elif "symptom" in q:
            return "symptoms"
        elif "treatment" in q or "treat" in q:
            return "treatment"
        elif "prevent" in q or "vaccine" in q:
            return "prevention"
        elif "help" in q or "support" in q or "feel" in q:
            return "support"
        else:
            return "generic"
        
    def structure_response(query: str, raw_response: str, user: str) -> dict:
        intent = classify_intent(query)

        return {
            "user": user,
            "intent": intent,
            "response": raw_response.strip(),
            "formatted": format_for_display(intent, raw_response.strip(), user)
        }

    def format_for_display(intent: str, response: str, user: str):
        if intent in ["definition", "symptoms", "treatment", "prevention"]:
            return {
                "title": f"{intent.capitalize()} Info",
                "message": response
            }
        elif intent == "support":
            return {
                "title": "Support",
                "message": f"{user}, here's some encouragement and guidance:\n\n{response}"
            }
        else:
            return {
                "title": "Answer",
                "message": response
            }
        
    try:
        completion = client.chat.completions.create(
            model="compound-beta",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ]
        )
        raw_response = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM service error: {e}")

    return structure_response(query, raw_response, db_user.email)


def get_recommended_facilities(screening_type: str, db: Session, user_region: str):
    service = db.query(CervicalCancerService).filter(
        CervicalCancerService.name == screening_type).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    required_resources = db.query(ServiceResourceRequirement).filter(
        ServiceResourceRequirement.service_id == service.id
    ).all()

    facilities = db.query(Facility).join(ServiceCost).filter(
        ServiceCost.service_id == service.id
    ).all()

    nearby_facilities = []
    other_facilities = []

    for facility in facilities:
        has_all_resources = True

        for requirement in required_resources:
            facility_resource = db.query(FacilityResource).filter_by(
                facility_id=facility.id,
                resource_type_id=requirement.resource_type_id
            ).first()

            if not facility_resource or facility_resource.quantity_available < requirement.required_quantity:
                has_all_resources = False
                break

        if has_all_resources:
            cost = db.query(ServiceCost).filter_by(
                facility_id=facility.id,
                service_id=service.id
            ).first()

            facility_data = {
                "id": facility.id,
                "name": facility.name,
                "region": facility.region,
                "contact_number": facility.contact_number,
                "service_cost": cost
            }
            print(facility_data)

            if facility.region == user_region:
                nearby_facilities.append(facility_data)
            else:
                other_facilities.append(facility_data)

    return {
        "nearby_facilities": nearby_facilities,
        "other_facilities": other_facilities,
        "total_count": len(nearby_facilities) + len(other_facilities)
    }

@router.post("/risk-assessment", response_model=schemas.RiskPredictionInDB)
async def create_risk_assessment(
    risk_data: schemas.RiskAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new risk assessment and get prediction"""
    db_user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not db_user.date_of_birth:
        raise HTTPException(status_code=400, detail="Date of birth is required for risk assessment")
    
    if risk_data.smoking_status not in ["Yes", "No"]:
        raise HTTPException(status_code=400, detail="Smoking status must be 'Yes' or 'No'")
    if risk_data.stds_history not in ["Yes", "No"]:
        raise HTTPException(status_code=400, detail="STDs history must be 'Yes' or 'No'")
    if risk_data.number_of_sexual_partners < 0:
        raise HTTPException(status_code=400, detail="Number of sexual partners cannot be negative")
    if risk_data.first_sexual_intercourse_age < 0:
        raise HTTPException(status_code=400, detail="First sexual intercourse age cannot be negative")
    
    # Calculate age
    today = date.today()
    age = today.year - db_user.date_of_birth.year - (
        (today.month, today.day) < (db_user.date_of_birth.month, db_user.date_of_birth.day)
    )
    
    # Create prediction data
    prediction_data = RiskPredictionData(
        age=float(age),
        number_of_sexual_partners=risk_data.number_of_sexual_partners,
        first_sexual_intercourse=risk_data.first_sexual_intercourse_age,
        smoking_status=risk_data.smoking_status,
        stds_history=risk_data.stds_history
    )
    
    # Get risk prediction
    prediction_result = predict_risk(prediction_data)
    screening_recommendations = prediction_result.get("screening_recommendations", {})
    
    # Save to database
    db_prediction = models.RiskPrediction(
        user_id=db_user.id,
        number_of_sexual_partners=risk_data.number_of_sexual_partners,
        first_sexual_intercourse_age=risk_data.first_sexual_intercourse_age,
        smoking_status=risk_data.smoking_status,
        stds_history=risk_data.stds_history,
        age_at_assessment=age,
        cluster=prediction_result.get("cluster"),
        interpretation=prediction_result.get("interpretation"),
        risk_level=screening_recommendations.get("urgency", "Unknown"),
        recommended_screenings=",".join(screening_recommendations.get("recommended_screenings", [])),
        reason=screening_recommendations.get("reason"),
        urgency=screening_recommendations.get("urgency"),
        frequency=screening_recommendations.get("frequency"),
        additional_services=",".join(screening_recommendations.get("additional_services", [])),
        created_at=date.today()
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction

@router.get("/risk-prediction", response_model=schemas.RiskPredictionResponse)
async def get_risk_prediction(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get latest risk prediction
    latest_prediction = db.query(models.RiskPrediction).filter(
        models.RiskPrediction.user_id == current_user.id
    ).order_by(models.RiskPrediction.created_at.desc()).first()
    
    if not latest_prediction:
        raise HTTPException(
            status_code=400, 
            detail="No risk assessment found. Please create a risk assessment first."
        )
    
    # Rebuild the prediction result for the response
    screening_recommendations = {
        "recommended_screenings": latest_prediction.recommended_screenings.split(",") if latest_prediction.recommended_screenings else [],
        "reason": latest_prediction.reason or "",
        "urgency": latest_prediction.urgency or "Unknown",
        "frequency": latest_prediction.frequency or "",
        "additional_services": latest_prediction.additional_services.split(",") if latest_prediction.additional_services else []
    }
    
    prediction_result = {
        "cluster": latest_prediction.cluster,
        "interpretation": latest_prediction.interpretation,
        "screening_recommendations": screening_recommendations
    }
    
    risk_data = {
        "age": float(latest_prediction.age_at_assessment),
        "number_of_sexual_partners": latest_prediction.number_of_sexual_partners,
        "first_sexual_intercourse": latest_prediction.first_sexual_intercourse_age,
        "smoking_status": latest_prediction.smoking_status,
        "stds_history": latest_prediction.stds_history
    }
    
    # Get facility recommendations
    recommended_screenings = screening_recommendations.get("recommended_screenings", [])
    
    if recommended_screenings:
        result = get_recommended_facilities(
            screening_type="HPV Vaccine",
            db=db,
            user_region=db_user.region
            )
        
        print("result",result)
    
    
    return {
        "user_id": db_user.id,
        "user_location": {
            "region": db_user.region,
            "message": f"Showing facilities in {db_user.region} first" if db_user.region else "Please update your region for location-based recommendations"
        },
        "risk_assessment": risk_data,
        "prediction": prediction_result,
        "recommended_facilities": {
            "nearby_facilities": result["nearby_facilities"],
            "other_facilities": result["other_facilities"],
            "total_count": result["total_count"]
        },
        "summary": {
            "risk_level": screening_recommendations.get("urgency", "Unknown"),
            "next_steps": screening_recommendations.get("recommended_screenings", []),
            "reason": screening_recommendations.get("reason", ""),
            "additional_services": screening_recommendations.get("additional_services", []),
            # "location_note": f"Found {len(same_region_facilities)} facilities in your region ({db_user.region})" if db_user.region and same_region_facilities else "Consider updating your region for better facility recommendations"
        }
    }


@router.get("/risk-prediction-history", response_model=schemas.RiskPredictionHistory)
async def get_risk_prediction_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    predictions = db.query(models.RiskPrediction).filter(
        models.RiskPrediction.user_id == current_user.id
    ).order_by(models.RiskPrediction.created_at.desc()).all()
    
    latest_prediction = predictions[0] if predictions else None
    
    return {
        "predictions": predictions,
        "total_count": len(predictions),
        "latest_prediction": latest_prediction
    }