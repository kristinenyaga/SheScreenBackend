from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from lab_tests.models import LabTest
from lab_tests.schemas import LabTestCreate, LabTestOut, LabTestUpdate, LabTestStatus, FollowUpAssignment
from users.db import get_db
from datetime import datetime
from recommended_action.models import Recommendation

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
def update_lab_test_result(
    lab_test_id: int,
    data: LabTestUpdate,
    db: Session = Depends(get_db)
):
    lab_test = db.query(LabTest).filter(LabTest.id == lab_test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    update_data = data.model_dump(exclude_unset=True)

    if "result" in update_data:
        if "status" not in update_data:
            update_data["status"] = LabTestStatus.completed
        if update_data["status"] == LabTestStatus.completed:
            update_data["date_completed"] = datetime.utcnow()


    for key, value in update_data.items():
        setattr(lab_test, key, value)

    db.commit()
    db.refresh(lab_test)


    related_tests = db.query(LabTest).filter(
        LabTest.recommendation_id == lab_test.recommendation_id
    ).all()

    if all(t.status == LabTestStatus.completed for t in related_tests):
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == lab_test.recommendation_id
        ).first()
        if recommendation:
            recommendation.status = "results_entered"
            db.commit()  

    return lab_test



@router.patch("/{lab_test_id}/assign-follow-up", response_model=LabTestOut)
def assign_follow_up_to_lab_test(
    lab_test_id: int,
    data: FollowUpAssignment,
    db: Session = Depends(get_db)
):
    lab_test = db.query(LabTest).filter(LabTest.id == lab_test_id).first()
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    lab_test.follow_up_id = data.follow_up_id
    db.commit()
    db.refresh(lab_test)
    return lab_test
