from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from users.db import get_db
from symptom_log import models, schemas
from typing import List
from datetime import date
from patients import models as patient_models  
from patients import auth
router = APIRouter(prefix="/symptom-logs", tags=["Symptom Logs"])


@router.post("/", response_model=schemas.SymptomLogOut)
def create_symptom_log(
    entry: schemas.SymptomLogCreate,
    db: Session = Depends(get_db),
    current_user: patient_models.Patient = Depends(auth.get_current_user)
):
    log = models.SymptomLog(
        patient_id=current_user.id,
        symptom=entry.symptom,
        severity=entry.severity,
        notes=entry.notes
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/", response_model=List[schemas.SymptomLogOut])
def list_symptom_logs(
    db: Session = Depends(get_db),
    current_user: patient_models.Patient = Depends(auth.get_current_user),
    for_date: date = None
):
    query = db.query(models.SymptomLog).filter(
        models.SymptomLog.patient_id == current_user.id)
    if for_date:
        query = query.filter(models.SymptomLog.date == for_date)
    return query.order_by(models.SymptomLog.date.desc()).all()
