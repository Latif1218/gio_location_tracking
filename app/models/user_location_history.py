from sqlalchemy import Column, Float, TIMESTAMP, text, Integer, ForeignKey, Date, Boolean
from ..database import Base
from sqlalchemy.orm import relationship
from cuid2 import Cuid
from datetime import datetime, timezone

    
class UserFixedLocation(Base):
    __tablename__ = "user_fixed_location"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    fixed_latitude   = Column(Float, nullable=True)   
    fixed_longitude  = Column(Float, nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False) 
    change_request_pending = Column(Boolean, default=False, nullable=False)
    requested_latitude = Column(Float, nullable=True)
    requested_longitude = Column(Float, nullable=True)
    requested_at = Column(TIMESTAMP(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(TIMESTAMP(timezone=True), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship(
    "User",
    back_populates="locations",  
    foreign_keys="[UserFixedLocation.user_id]" 
)
    
class UserAttendance(Base):
    __tablename__ = "user_attendance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    attendance_date = Column(Date, nullable=False)
    current_latitude = Column(Float)
    current_longitude = Column(Float)
    distance = Column(Float)
    is_present = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))