import jwt
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from ..schemas import user_schemas
from ..models import user_models
from ..database import get_db
from ..utils.hashing import verify_password
from typing import Optional, Annotated
from datetime import datetime, timedelta, timezone
from ..config import JWT_SECRET_KEY


SECRET_KEY = JWT_SECRET_KEY
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5  


def get_user(db: Session, username: str):
    user = db.query(user_models.User).filter(user_models.User.email == username).first()
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def get_current_user(
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db)                 
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers = {"www-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
        token_data = user_schemas.TokenData(id=user_id)
        
    except IndentationError:
        raise credentials_exception
    
    user = db.query(user_models.User).filter(user_models.User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[user_schemas.User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
        