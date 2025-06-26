from sqlalchemy import Column,Integer,String,ForeignKey,Boolean
from sqlalchemy.orm import relationship
from users.db import Base

class FacilityUser(Base):
  __tablename__='facility_users'

  id = Column(Integer,primary_key=True,index=True)
  first_name = Column(String(50), nullable=True)
  last_name = Column(String(50), nullable=True)   
  phone_number = Column(String(20), unique=True,nullable=True)  
  email = Column(String(100), unique=True, index=True,nullable=False)  
  role = Column(String(100), nullable=False,)
  hashed_password = Column(String(255))

  facility_id =Column(Integer,ForeignKey("facilities.id"))
  facility =relationship("Facility",back_populates="users")
  created_care_plans=relationship("CarePlan",back_populates="creator")
