from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from users.db import get_db
from patient_profiles.models import PatientProfile
from patients import models as PatientModels
from patient_profiles.schemas import (
    PatientProfileCreate,
    PatientProfileUpdate,
    PatientProfileResponse,
)

router = APIRouter(prefix="/patient-profiles", tags=["Patient Profiles"])


@router.post("/", response_model=PatientProfileResponse)
def create_profile(profile_data: PatientProfileCreate, db: Session = Depends(get_db)):
    patient = db.query(PatientModels.Patient).filter(
        PatientModels.Patient.id == profile_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    profile = PatientProfile(**profile_data.dict(exclude_unset=True))
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/", response_model=List[PatientProfileResponse])
def get_all_profiles(db: Session = Depends(get_db)):
    return db.query(PatientProfile).all()


@router.get("/{patient_id}", response_model=PatientProfileResponse)
def get_profile_by_patient(patient_id: int, db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(
        PatientProfile.patient_id == patient_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{patient_id}", response_model=PatientProfileResponse)
def update_profile(patient_id: int, updates: PatientProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(
        PatientProfile.patient_id == patient_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in updates.dict(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{patient_id}")
def delete_profile(patient_id: int, db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(
        PatientProfile.patient_id == patient_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"detail": "Profile deleted successfully"}
