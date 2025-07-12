from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from users.db import Base


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    risk_prediction_id = Column(Integer, ForeignKey("risk_predictions.id"), nullable=False)
    urgency = Column(String(20), default="Medium")
    notes = Column(Text)
    final_recommendation = Column(Text)
    is_override = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


    patient = relationship("Patient", back_populates="recommendations")
    risk_prediction = relationship("RiskPrediction", back_populates="recommendation")
