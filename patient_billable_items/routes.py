from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from users.db import get_db
from patient_billable_items import schemas
from patient_billable_items.models import PatientBillableItem
from typing import List, Optional

router = APIRouter(prefix="/billable-items", tags=["Billing"])

# Create billable item


@router.post("/", response_model=schemas.PatientBillableItemOut)
def create_billable_item(
    item_data: schemas.PatientBillableItemCreate,
    db: Session = Depends(get_db)
):
    item = PatientBillableItem(**item_data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# Get all billable items (with optional filters)


@router.get("/", response_model=List[schemas.PatientBillableItemOut])
def list_billable_items(
    patient_id: Optional[int] = Query(None),
    invoice_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(PatientBillableItem)
    if patient_id:
        query = query.filter(PatientBillableItem.patient_id == patient_id)
    if invoice_id:
        query = query.filter(PatientBillableItem.invoice_id == invoice_id)
    return query.all()

# Get single billable item


@router.get("/{item_id}", response_model=schemas.PatientBillableItemOut)
def get_billable_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(PatientBillableItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=schemas.PatientBillableItemOut)
def update_billable_item(
    item_id: int,
    item_data: schemas.PatientBillableItemUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(PatientBillableItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item_data.dict(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.get("/by-patient/{patient_id}", response_model=schemas.PatientBillableItemSummary)
def get_billable_items_with_total(patient_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(PatientBillableItem)
        .filter(PatientBillableItem.patient_id == patient_id)
        .all()
    )

    total = sum(item.patient_amount for item in items if item.patient_amount)

    return {
        "items": items,
        "total_cost": round(total, 2)
    }


@router.patch("/mark-paid/{item_id}", response_model=schemas.PatientBillableItemOut)
def mark_item_as_paid(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(PatientBillableItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.paid = True
    db.commit()
    db.refresh(item)
    return item
