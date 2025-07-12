from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Date
from users.db import Base
from datetime import datetime, timezone


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True)

    is_sexually_active = Column(String(10))
    hpv_vaccinated = Column(String(10))
    has_children = Column(String(10))

    number_of_sexual_partners = Column(Integer, nullable=True)
    first_sexual_intercourse_age = Column(Integer, nullable=True)
    smoking_status = Column(String(100))
    stds_history = Column(String(100))
    hpv_result = Column(String(100))

    immune_compromised = Column(String(100))
    immune_condition_detail = Column(String(100))

    contraceptive_using = Column(String(100))
    contraceptive_use_years = Column(Integer, nullable=True)
    children_count = Column(Integer, nullable=True)
    first_pregnancy_age = Column(String(100))
    family_history = Column(String(100))

    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="profile")
