from sqlalchemy import Column, Float, TIMESTAMP, text, Integer, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship
from cuid2 import Cuid
import datetime





class UserLocationHistory(Base):
    __tablename__ = "first_user_location_history"

    id = Column(Integer, primary_key=True, index=True)  
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    login_latitude = Column(Float, nullable=False)      
    login_longitude = Column(Float, nullable=False)
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    distance_from_login = Column(Float, nullable=True)
    is_present = Column(Float, default=1)
    create_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user = relationship(
        "User", 
        back_populates="locations"
    )