from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from users.db import Base


class PatientBillableItem(Base):
    __tablename__ = "patient_billable_items"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("cervical_cancer_services.id"), nullable=False)
    service_cost_id = Column(Integer, ForeignKey("service_costs.id"), nullable=True)

    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    paid = Column(Boolean, default=False)

    base_cost = Column(Float, nullable=True)
    nhif_covered = Column(Boolean, default=False)
    nhif_amount = Column(Float, default=0)
    patient_amount = Column(Float, default=0)

    patient = relationship("Patient", back_populates="billable_items")
    service = relationship("CervicalCancerService")
    service_cost = relationship("ServiceCost")
