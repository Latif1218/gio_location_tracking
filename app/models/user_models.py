from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, TIMESTAMP, text, DateTime
from ..database import Base
from sqlalchemy.orm import relationship
from cuid2 import Cuid
import datetime

cuid = Cuid()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String, nullable=False)
    phone_number = Column(String)
    verified: bool = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_management = Column(Boolean, default=False)
    two_fa_enabled = Column(Boolean, default=False)
    two_fa_method = Column(String)  # "email" or "sms"
    role = Column(String, default="user")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)