from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey,Boolean,Float
from sqlalchemy.orm import relationship
from datetime import datetime
from datetime import datetime, timezone
from users.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    area_of_residence = Column(String(250), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(250),unique=True, nullable=True)
    phone_number = Column(String(100), nullable=True)
    patient_code = Column(String(20), unique=True, index=True, nullable=False)


    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    created_by= relationship("User", back_populates="patients")
    risk_predictions = relationship("RiskPrediction", back_populates="patient")
    profile = relationship("PatientProfile", back_populates="patient", uselist=False)
    care_plans = relationship("CarePlan", back_populates="patient")

    received_messages = relationship("Message", back_populates="receiver_patient")
    recommendations = relationship("Recommendation", back_populates="patient")
    lab_tests = relationship("LabTest", back_populates="patient")
    billable_items = relationship("PatientBillableItem", back_populates="patient")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Risk assessment input data
    number_of_sexual_partners = Column(Integer, nullable=False)
    first_sexual_intercourse_age = Column(Integer, nullable=False)
    smoking_status = Column(String(10), nullable=False)
    stds_history = Column(String(10), nullable=False)
    hpv_test_result = Column(String(20), nullable=False, default="Negative")
    hpv_vaccinated = Column(Boolean, nullable=False, default=False)
    age_at_assessment = Column(Integer, nullable=False)

    # Prediction results
    interpretation = Column(String(255), nullable=False)
    risk_level = Column(String(50), nullable=False)  # High, Medium, Low
    risk_probability = Column(Float,nullable=False)

    # Screening recommendations
    recommended_screenings = Column(String(500), nullable=True)
    reason = Column(String(1000), nullable=True)
    urgency = Column(String(50), nullable=True)
    frequency = Column(String(200), nullable=True)
    additional_services = Column(String(500), nullable=True)

    created_at = Column(Date, nullable=False)

    patient = relationship(
        "Patient", back_populates="risk_predictions", uselist=False)
    
    recommendation = relationship(
        "Recommendation", back_populates="risk_prediction", uselist=False)


