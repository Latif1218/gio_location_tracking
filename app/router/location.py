from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.user_location_history import UserLocationHistory
from ..schemas.location_schema import UserLocationCreate
from sqlalchemy.orm import Session 
from ..database import get_db
from ..authentication.user_auth import get_current_user
from geopy.distance import geodesic

router = APIRouter(
    prefix="/location", 
    tags=["location"]
)


MAX_DISTANCE = 5


@router.post("/update")
def update_user_location(
    location: UserLocationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    user_id = current_user.id
    
    record = db.query(UserLocationHistory).filter(
        UserLocationHistory.user_id==user_id
    ).order_by(
        UserLocationHistory.create_at.desc()
    ).first()
    
    if not record:
        new_record = UserLocationHistory(
            user_id=user_id,
            login_latitude=location.latitude,
            login_longitude=location.longitude,
            current_latitude=location.latitude,
            current_longitude=location.longitude,
            distance_from_login=0,
            is_present=1
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return {"status": "first login location saved", "distance_from_login": 0}

    else:
        login_point = (record.login_latitude, record.login_longitude)
        current_point = (location.latitude, location.longitude)
        distance = geodesic(login_point, current_point).meters
        
        is_present = 1 if distance <= MAX_DISTANCE else 0
        
        new_record = UserLocationHistory(
            user_id=user_id,
            login_latitude=record.login_latitude,
            login_longitude=record.login_longitude,
            current_latitude=location.latitude,
            current_longitude=location.longitude,
            distance_from_login=distance,
            is_present=is_present
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        
        return {
            "status": "location updated",
            "distance_from_login": distance,
            "is_present": is_present
        }
                   
                   
    # Create a new record
    # new_location = UserLocationHistory(
    #     user_id=current_user.id,
    #     old_latitude=location.latitude,
    #     old_longitude=location.longitude
    # )
    # db.add(new_location)
    # db.commit()
    # db.refresh(new_location)
    
    # return {"status": "Location saved", "id": new_location.id}



