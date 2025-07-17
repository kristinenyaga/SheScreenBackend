from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey,Boolean,Float,Text
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
    follow_up_plans = relationship("FollowUp", back_populates="patient")



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
    
    follow_up_plans = relationship(
        "FollowUp", back_populates="risk_prediction")  


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    risk_prediction_id = Column(Integer, ForeignKey("risk_predictions.id"), nullable=True)
    
    # Input data
    age = Column(Integer, nullable=False)
    number_of_sexual_partners = Column(Integer, nullable=False)
    first_sexual_intercourse_age = Column(Integer, nullable=False)
    smoking_status = Column(String(10), nullable=False)
    stds_history = Column(String(10), nullable=False)
    hpv_current_test_result = Column(String(20), nullable=False)
    pap_smear_result = Column(String(20), nullable=False)
    screening_type_last = Column(String(50), nullable=True)
    
    # results
    category = Column(String(100), nullable=False)
    options = Column(Text, nullable=False)  # JSON string of options
    context = Column(Text, nullable=True)   # JSON string of context
    confidence = Column(Float, nullable=False)
    method = Column(String(50), nullable=False, default="ML model")  # ML model or clinical_rules
    prediction_label = Column(Integer, nullable=True)
    prediction_probabilities = Column(Text, nullable=True)  # JSON string of probabilities
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    patient = relationship("Patient", back_populates="follow_up_plans")
    risk_prediction = relationship("RiskPrediction", back_populates="follow_up_plans")
