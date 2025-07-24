from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from users.db import Base


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    symptom = Column(String(100), nullable=False)
    severity = Column(Integer) 
    notes = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="symptom_logs")
