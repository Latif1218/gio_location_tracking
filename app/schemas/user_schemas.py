from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="password must be between 8 to 128 characters")
    role: str = "user"
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v 
    
    
class UserRespons(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    } 
    
    
class UserToken(BaseModel):
    access_token : str
    token_type : str

    model_config = {
        "from_attributes": True
    }
    
    
    
class UserLogin(BaseModel):
    email : EmailStr
    password : str 
    
    
class TokenData(BaseModel):
    id : Optional[int] = None
    
    
    
class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128, description="password must be between 8 to 128 characters")
    model_config = {
        "extra": "forbid"
    }
    
    
    
    
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    model_config = {
        "extra": "forbid"
    }
    
    
    
class OTPVerify(BaseModel):
    email : EmailStr
    otp: str 
    model_config = {
        "extra": "forbid"
    }
    
    @field_validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v
    
    
    
class PasswoedUpdateWithoutToken(BaseModel):
    email : EmailStr
    otp : str
    new_password: str = Field(..., min_length=8, max_length=128, description="password must be between 8 to 128 characters")
    model_config = {
        "extra": "forbid"
    }