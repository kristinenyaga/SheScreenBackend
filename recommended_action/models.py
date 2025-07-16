from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from users.db import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    risk_prediction_id = Column(Integer, ForeignKey( "risk_predictions.id"), nullable=False)


    test_recommendations = Column(String(500))
    non_test_recommendations = Column(String(500))
    additional_services = Column(String(500))
    ai_recommendation = Column(String(500))
    referral = Column(String(255))

    notes = Column(Text)
    status = Column(String(100), default="awaiting_test_results", nullable=False)
    urgency = Column(String(20), default="Medium")
    is_override = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="recommendations")
    risk_prediction = relationship("RiskPrediction", back_populates="recommendation")
    lab_tests = relationship("LabTest", back_populates="recommendation")
