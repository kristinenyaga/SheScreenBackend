from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from users.db import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("cervical_cancer_services.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    quantity_used = Column(Float, nullable=False)
    date_used = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="usage_logs")
    service = relationship("CervicalCancerService", back_populates="usage_logs")
    resource = relationship("Resource", back_populates="usage_logs")
