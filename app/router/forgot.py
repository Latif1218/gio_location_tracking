from fastapi import APIRouter, Depends, status, HTTPException
from ..authentication import user_auth
from sqlalchemy.orm import Session
from ..database import get_db, get_redis
from ..schemas import user_schemas
from ..models import user_models
from ..utils.otp_sender import generate_otp
from ..utils.email_sender import send_otp_email
from ..authentication import user_auth
from ..utils import hashing
from datetime import datetime, timedelta, timezone



router = APIRouter(
    prefix="/forgot",
    tags=["Forgot Password"]
)

@router.post("/forgot_pass", status_code=status.HTTP_200_OK)
def forgot_password(
    payload: user_schemas.ForgotPasswordRequest, 
    db: Session = Depends(get_db)
):
    user = db.query(user_models.User).filter(
        user_models.User.email == payload.email
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email dose not exist"
        )
        
    set_otp = generate_otp()
    db.query(user_models.PasswordResetCode).filter(
        user_models.PasswordResetCode.user_id == user.id,
        user_models.PasswordResetCode.used == False
    ).delete()
    
    otp_recode = user_models.PasswordResetCode(
        user_id = user.id,
        otp = set_otp,
        used = False,
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    
    db.add(otp_recode)
    db.commit()
    
    sent = send_otp_email(to_email= user.email, otp = set_otp)
    
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Faild to send otp email"
        )
    return{
        "status": "seccess",
        "message": f"Password reset otp sent to {user.email}"
    }
    
    
    
@router.post("/verify_otp", status_code=status.HTTP_200_OK)
def verify_otp(
    payload: user_schemas.OTPVerify, 
    db: Session = Depends(get_db)
):
    user = db.query(user_models.User).filter(
        user_models.User.email == payload.email
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email dose not exist"
        )
        
    otp_record = db.query(user_models.PasswordResetCode).filter(
        user_models.PasswordResetCode.user_id == user.id,
        user_models.PasswordResetCode.otp == payload.otp,
        user_models.PasswordResetCode.used == False,
        user_models.PasswordResetCode.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tnvalid or expired OTP"
        )
        
    otp_record.used = True
    db.commit()
    
    redis_session = get_redis()
    reset_key = redis_session.get_key("password_reset: {}:{}", payload.email, payload.otp)
    redis_session.set_with_expiry(reset_key, "verified", 600)
    
    return {
        "status": "success", 
        "message": "OTP verified successfully. you can now reset your password"
    }
    
    
    
    