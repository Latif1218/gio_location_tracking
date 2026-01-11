from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.user_location_history import UserLocationHistory
from ..schemas.location_schema import UserLocationCreate
from sqlalchemy.orm import Session 
from ..database import get_db
from ..authentication.user_auth import get_current_user

router = APIRouter(
    prefix="/location", 
    tags=["location"]
)




@router.post("/update")
def update_user_location(
    location: UserLocationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
        
    # Create a new record
    new_location = UserLocationHistory(
        user_id=current_user.id,
        old_latitude=location.latitude,
        old_longitude=location.longitude
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    
    return {"status": "Location saved", "id": new_location.id}


