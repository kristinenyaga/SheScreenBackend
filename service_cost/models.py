from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from users.db import Base


class ServiceCost(Base):
    __tablename__ = "service_costs"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("cervical_cancer_services.id"), nullable=False)
    base_cost = Column(Float, nullable=True)
    nhif_covered = Column(Boolean, default=False)
    out_of_pocket = Column(Float, nullable=True)
    insurance_copay_amount = Column(Float, nullable=True)

    facility = relationship("Facility", back_populates="service_costs")
    service = relationship("CervicalCancerService",back_populates="service_costs")
