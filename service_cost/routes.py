from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from service_cost import models,schemas

router = APIRouter(prefix="/service-costs")


@router.post("/", response_model=schemas.ServiceCostResponse)
def create_service_cost(cost: schemas.ServiceCostCreate, db: Session = Depends(get_db)):
    db_cost = models.ServiceCost(**cost.dict())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@router.get("/", response_model=list[schemas.ServiceCostResponse])
def get_service_costs(db: Session = Depends(get_db)):
    return db.query(models.ServiceCost).all()


@router.get("/{cost_id}", response_model=schemas.ServiceCostResponse)
def get_service_cost(cost_id: int, db: Session = Depends(get_db)):
    cost = db.query(models.ServiceCost).filter(
        models.ServiceCost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Service cost not found")
    return cost


@router.patch("/{cost_id}", response_model=schemas.ServiceCostResponse)
def update_service_cost(cost_id: int, updates: schemas.ServiceCostUpdate, db: Session = Depends(get_db)):
    cost = db.query(models.ServiceCost).filter(
        models.ServiceCost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Service cost not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(cost, key, value)

    db.commit()
    db.refresh(cost)
    return cost


@router.delete("/{cost_id}")
def delete_service_cost(cost_id: int, db: Session = Depends(get_db)):
    cost = db.query(models.ServiceCost).filter(
        models.ServiceCost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Service cost not found")
    db.delete(cost)
    db.commit()
    return {"detail": "Service cost deleted"}
