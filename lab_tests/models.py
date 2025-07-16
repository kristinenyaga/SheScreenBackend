from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from users.db import Base
import enum


class LabTestStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)

    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("cervical_cancer_services.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    result = Column(String(50), nullable=True)  # "Positive", "Negative"
    status = Column(Enum(LabTestStatus), default=LabTestStatus.pending)

    ordered_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entered_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    date_ordered = Column(DateTime, default=datetime.utcnow)
    date_completed = Column(DateTime, nullable=True)


    recommendation = relationship("Recommendation", back_populates="lab_tests")
    service = relationship("CervicalCancerService")
    patient = relationship("Patient", back_populates="lab_tests")
    ordered_by = relationship("User", foreign_keys=[ordered_by_id])
    entered_by = relationship("User", foreign_keys=[entered_by_id])
