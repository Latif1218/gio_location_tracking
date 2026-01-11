from sqlalchemy import Column, Float, TIMESTAMP, text, Integer, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship
from cuid2 import Cuid
import datetime





class UserLocationHistory(Base):
    __tablename__ = "first_user_location_history"

    id = Column(Integer, primary_key=True, index=True)  # Auto increment ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_latitude = Column(Float)
    old_longitude = Column(Float)
    min_distance = Column(Float, nullable=True)
    create_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user = relationship(
        "User", 
        back_populates="locations"
    )
