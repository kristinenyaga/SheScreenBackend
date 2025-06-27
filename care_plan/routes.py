from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from care_plan import models,schemas

router = APIRouter(prefix="/care-plans")

@router.post("/",response_model=schemas.CarePlanResponse)
def create_care_plans(plan:schemas.CarePlanCreate,db:Session=Depends(get_db)):
  db_plan = models.CarePlan(**plan.model_dump())
  db.add(db_plan)
  db.commit()
  db.refresh(db_plan)
  return db_plan


@router.get("/user/{user_id}", response_model=schemas.CarePlanResponse)
def get_care_plan_by_user_id(user_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.CarePlan).filter(
        models.CarePlan.user_id == user_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Care Plan not found")
    return plan


@router.delete("/{care_plan_id}")
def delete_care_plan(care_plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.CarePlan).filter(
        models.CarePlan.id == care_plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Care Plan not found")
    db.delete(plan)
    db.commit()
    return {"detail": "Care Plan deleted"}
