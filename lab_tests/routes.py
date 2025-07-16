from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from lab_tests.models import LabTest
from lab_tests.schemas import LabTestCreate, LabTestOut, LabTestUpdate
from users.db import get_db

router = APIRouter(prefix="/lab-tests", tags=["Lab Tests"])


@router.post("/", response_model=LabTestOut)
def create_lab_test(data: LabTestCreate, db: Session = Depends(get_db)):
    lab_test = LabTest(**data.model_dump())
    db.add(lab_test)
    db.commit()
    db.refresh(lab_test)
    return lab_test


@router.get("/", response_model=List[LabTestOut])
def get_all_lab_tests(db: Session = Depends(get_db)):
    return db.query(LabTest).all()


@router.get("/by-patient/{patient_id}", response_model=List[LabTestOut])
def get_lab_tests_by_patient(patient_id: int, db: Session = Depends(get_db)):
    return db.query(LabTest).filter(LabTest.patient_id == patient_id).all()


@router.patch("/{lab_test_id}", response_model=LabTestOut)
def update_lab_test_result(lab_test_id: int, data: LabTestUpdate, db: Session = Depends(get_db)):
    lab_test = db.query(LabTest).filter(LabTest.id == lab_test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lab_test, key, value)

    # If result is updated, mark as completed and set completion date
    if data.result:
        lab_test.status = "completed"
        lab_test.date_completed = datetime.utcnow()

    db.commit()
    db.refresh(lab_test)
    return lab_test
