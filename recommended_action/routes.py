from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from recommended_action.schemas import RecommendationCreate, RecommendationOut
from recommended_action.models import Recommendation
from users.db import get_db

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationOut)
def create_recommendation(data: RecommendationCreate, db: Session = Depends(get_db)):
    rec = Recommendation(**data.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/by-patient/{patient_id}", response_model=list[RecommendationOut])
def get_patient_recommendations(patient_id: int, db: Session = Depends(get_db)):
    return db.query(Recommendation).filter(Recommendation.patient_id == patient_id).all()
