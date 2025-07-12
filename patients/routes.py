from passlib.context import CryptContext
import string
import secrets
from fastapi import APIRouter, HTTPException, Depends, Query,status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from users.db import get_db
from patients.schemas import PatientCreate, PatientOut, PatientUpdate
from datetime import timedelta
from datetime import date

from fastapi.security import OAuth2PasswordRequestForm

from patients import auth, models, schemas, security
from users.db import get_db
from patients.risk_prediction import predict_risk, RiskPredictionData
from chat.prompts import generate_context, qa_template
from chat.conversation_cache import conversation_cache
from messages import models as messages_models
from groq import Groq

from dotenv import load_dotenv, find_dotenv
import os
import numpy as np

load_dotenv(find_dotenv())

client = Groq()
router = APIRouter(prefix="/patients")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_random_password(length: int = 10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def get_password_hash(password: str):
    return pwd_context.hash(password)


@router.post("/", response_model=PatientOut)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    raw_password = generate_random_password()
    hashed_password = get_password_hash(raw_password)

    db_patient = models.Patient(
        **patient.model_dump(),
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    # email or SMS utility here
    # send_password_to_user(email=patient.email, password=raw_password)

    return db_patient

@router.get("/", response_model=List[PatientOut])
def get_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Patient).offset(skip).limit(limit).all()


@router.get("/{id}", response_model=PatientOut)
def get_patient(id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="models.Patient not found")
    return patient


@router.put("/{id}", response_model=PatientOut)
def update_patient(id: int, patient_update: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="models.Patient not found")
    for field, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{id}")
def delete_patient(id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="models.Patient not found")
    db.delete(patient)
    db.commit()
    return {"detail": "models.Patient deleted successfully"}


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    patient = db.query(models.Patient).filter(
        models.Patient.email == form_data.username).first()
    if not patient or not patient.hashed_password or not security.verify_password(form_data.password, patient.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": patient.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.patch("/profile", response_model=schemas.PatientOut)
def update_profile(
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: models.Patient = Depends(auth.get_current_user)
):
    db_patient = db.query(models.Patient).filter(
        models.Patient.id == current_user.id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="models.Patient not found")

    update_data = patient_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/profile", response_model=schemas.PatientOut)
def get_logged_in_patient(current_user: models.Patient = Depends(auth.get_current_user)):
    return current_user


@router.get("/conversation")
async def read_conversation(
    query: str,
    include_history: bool = False,
    include_context: bool = False,
    current_user: models.Patient = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_user = auth.get_user(db, email=current_user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="models.Patient not found")

    # Get previous conversation context
    conversation_context = conversation_cache.get_recent_context(
        current_user.id, max_messages=6)

    context = generate_context(db_user)

    enhanced_prompt = qa_template.format(
        email=db_user.email,
        context=context,
        question=query
    )

    # Add conversation history if available
    if conversation_context:
        enhanced_prompt += f"\n\nPrevious conversation context:\n{conversation_context}\n\nPlease consider this context when responding."

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

    def structure_response(query: str, raw_response: str) -> dict:
        intent = classify_intent(query)

        clean_response = raw_response.strip()

        return {
            "intent": intent,
            "response": clean_response,
            "formatted": format_for_display(intent, clean_response),
            "conversation_count": conversation_cache.get_conversation_count(current_user.id) + 2,
            "conversation_history": get_conversation_history_data(current_user.id) if include_history else None,
            "conversation_context": conversation_cache.get_recent_context(current_user.id, 10) if include_context else None
        }

    def format_for_display(intent: str, response: str):
        title_map = {
            "definition": "Information",
            "symptoms": "Symptoms",
            "treatment": "Treatment",
            "prevention": "Prevention",
            "support": "Support",
            "generic": "SheScreenAI"
        }

        return {
            "title": title_map.get(intent, "SheScreenAI"),
            "message": response
        }

    try:
        completion = client.chat.completions.create(
            model="compound-beta",
            messages=[
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": query}
            ]
        )
        raw_response = completion.choices[0].message.content

        # conversation to memory cache
        conversation_cache.add_message(
            current_user.id, query, is_bot_message=False)
        conversation_cache.add_message(
            current_user.id, raw_response, is_bot_message=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM service error: {e}")

    return structure_response(query, raw_response)


@router.post("/risk-assessment", response_model=schemas.RiskPredictionInDB)
async def create_risk_assessment(
    risk_data: schemas.RiskAssessmentCreate,
    db: Session = Depends(get_db),
):
    patient = db.query(models.Patient).filter(models.Patient.id == risk_data.patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="models.Patient not found")

    if not patient.date_of_birth:
        raise HTTPException(
            status_code=400, detail="models.Patient must have a date of birth")

    if risk_data.smoking_status not in ["Yes", "No"]:
        raise HTTPException(
            status_code=400, detail="Smoking status must be 'Yes' or 'No'")
    if risk_data.stds_history not in ["Yes", "No"]:
        raise HTTPException(
            status_code=400, detail="STDs history must be 'Yes' or 'No'")
    if risk_data.hpv_test_result not in ["Positive", "Negative", "Unknown"]:
        raise HTTPException(
            status_code=400, detail="HPV test result must be 'Positive', 'Negative', or 'Unknown'")
    if risk_data.number_of_sexual_partners < 0:
        raise HTTPException(
            status_code=400, detail="Number of sexual partners cannot be negative")
    if risk_data.first_sexual_intercourse_age < 0:
        raise HTTPException(
            status_code=400, detail="First sexual intercourse age cannot be negative")

    # Calculate age
    today = date.today()
    age = today.year - patient.date_of_birth.year - (
        (today.month, today.day) < (
            patient.date_of_birth.month, patient.date_of_birth.day)
    )
    # Create prediction data
    prediction_data = RiskPredictionData(
        age=float(age),
        number_of_sexual_partners=risk_data.number_of_sexual_partners,
        first_sexual_intercourse=risk_data.first_sexual_intercourse_age,
        smoking_status=risk_data.smoking_status,
        stds_history=risk_data.stds_history,
        hpv_test_result=risk_data.hpv_test_result,
        hpv_vaccinated=risk_data.hpv_vaccinated
    )

    # Get risk prediction
    prediction_result = predict_risk(prediction_data)
    screening_recommendations = prediction_result.get(
        "screening_recommendations", {})

    # Save to database
    db_prediction = models.RiskPrediction(
        patient_id=risk_data.patient_id,
        number_of_sexual_partners=risk_data.number_of_sexual_partners,
        first_sexual_intercourse_age=risk_data.first_sexual_intercourse_age,
        smoking_status=risk_data.smoking_status,
        stds_history=risk_data.stds_history,
        hpv_test_result=risk_data.hpv_test_result,
        hpv_vaccinated=risk_data.hpv_vaccinated,
        age_at_assessment=age,
        cluster=prediction_result.get("cluster"),
        interpretation=prediction_result.get("interpretation"),
        risk_level=screening_recommendations.get("urgency", "Unknown"),
        recommended_screenings=",".join(
            screening_recommendations.get("recommended_screenings", [])),
        reason=screening_recommendations.get("reason"),
        urgency=screening_recommendations.get("urgency"),
        frequency=screening_recommendations.get("frequency"),
        additional_services=",".join(
            screening_recommendations.get("additional_services", [])),
        created_at=date.today()
    )

    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    return db_prediction


@router.get("/risk-prediction/{patient_id}", response_model=schemas.RiskPredictionResponse)
async def get_risk_prediction(
    patient_id:int,
    db: Session = Depends(get_db)
):
    
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()

    # Get latest risk prediction
    latest_prediction = db.query(models.RiskPrediction).filter(
        models.RiskPrediction.patient_id == patient_id
    ).order_by(models.RiskPrediction.created_at.desc()).first()

    if not latest_prediction:
        raise HTTPException(
            status_code=400,
            detail="No risk assessment found. Please create a risk assessment first."
        )

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
        "stds_history": latest_prediction.stds_history,
        "hpv_test_result": latest_prediction.hpv_test_result,
        "hpv_vaccinated": latest_prediction.hpv_vaccinated
    }

    # Get facility recommendations
    recommended_screenings = screening_recommendations.get(
        "recommended_screenings", [])

    return {
        "patient_id": patient.id,
        "risk_assessment": risk_data,
        "prediction": prediction_result,
        "summary": {
            "risk_level": screening_recommendations.get("urgency", "Unknown"),
            "next_steps": screening_recommendations.get("recommended_screenings", []),
            "reason": screening_recommendations.get("reason", ""),
            "additional_services": screening_recommendations.get("additional_services", []),
            # "location_note": f"Found {len(same_region_facilities)} facilities in your region ({db_user.region})" if db_user.region and same_region_facilities else "Consider updating your region for better facility recommendations"
        }
    }


# @router.get("/risk-prediction/{patient_id}", response_model=schemas.RiskPredictionHistory)
# async def get_risk_prediction_history(
#     patient_id: int,
#     db: Session = Depends(get_db)
# ):
#     predictions = db.query(models.RiskPrediction).filter(
#         models.RiskPrediction.patient_id == patient_id
#     ).order_by(models.RiskPrediction.created_at.desc()).all()

#     latest_prediction = predictions[0] if predictions else None

#     return {
#         "predictions": predictions,
#         "total_count": len(predictions),
#         "latest_prediction": latest_prediction
#     }


@router.get("/conversation-history")
async def get_conversation_history(
    current_user: models.Patient = Depends(auth.get_current_user)
):
    """Get user's cached conversation history"""
    conversations = conversation_cache.get_conversation(current_user.id)

    formatted_conversations = []
    for msg in conversations:
        formatted_conversations.append({
            "content": msg.content,
            "is_bot_message": msg.is_bot_message,
            "timestamp": msg.timestamp.isoformat(),
            "role": "bot" if msg.is_bot_message else "user"
        })

    return {
        "patient_id": current_user.id,
        "conversation_count": len(conversations),
        "messages": formatted_conversations
    }


@router.get("/conversation-context")
async def get_conversation_context(
    current_user: models.Patient = Depends(auth.get_current_user),
    max_messages: int = 10
):
    context = conversation_cache.get_recent_context(
        current_user.id, max_messages)

    return {
        "patient_id": current_user.id,
        "context": context,
        "message_count": conversation_cache.get_conversation_count(current_user.id)
    }


@router.delete("/clear-conversation")
async def clear_conversation(
    current_user: models.Patient = Depends(auth.get_current_user)
):
    message_count = conversation_cache.get_conversation_count(current_user.id)
    conversation_cache.clear_user_conversation(current_user.id)

    return {
        "message": f"Conversation history cleared successfully ({message_count} messages removed)",
        "patient_id": current_user.id,
        "cleared_messages": message_count
    }

def get_conversation_history_data(user_id: int):
    conversations = conversation_cache.get_conversation(user_id)

    formatted_conversations = []
    for msg in conversations:
        formatted_conversations.append({
            "content": msg.content,
            "is_bot_message": msg.is_bot_message,
            "timestamp": msg.timestamp.isoformat(),
            "role": "bot" if msg.is_bot_message else "user"
        })

    return {
        "message_count": len(conversations),
        "messages": formatted_conversations
    }

