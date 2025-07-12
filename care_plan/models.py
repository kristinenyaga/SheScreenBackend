from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from users.db import Base


class CarePlan(Base):
    __tablename__ = "care_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    hpv_result = Column(String(100))
    pap_smear_result = Column(String(100))
    recommended_action = Column(String(255))
    screening_type = Column(String(100))
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="care_plans")
    creator = relationship("User", back_populates="created_care_plans")
