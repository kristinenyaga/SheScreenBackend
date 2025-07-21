from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from users.db import get_db
from usage_log import models,schemas
from resources import models as ResourceModels
router = APIRouter(prefix="/usage-logs", tags=["Usage Logs"])


@router.post("/", response_model=schemas.UsageLogRead)
def create_usage_log(log: schemas.UsageLogCreate, db: Session = Depends(get_db)):
    usage = models.UsageLog(**log.dict())
    db.add(usage)


    resource = db.query(ResourceModels.Resource).filter(
        ResourceModels.Resource.id == usage.resource_id).first()
    if resource.resource_type == "consumable":
        if resource.quantity_available < usage.quantity_used:
            raise HTTPException(status_code=400, detail="Not enough stock")
        resource.quantity_available -= usage.quantity_used

    db.commit()
    db.refresh(usage)
    return usage


@router.get("/", response_model=list[schemas.UsageLogRead])
def list_usage_logs(db: Session = Depends(get_db)):
    return db.query(models.UsageLog).all()
