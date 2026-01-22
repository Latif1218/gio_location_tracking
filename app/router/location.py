from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models.user_location_history import UserFixedLocation, UserAttendance
from ..schemas.location_schema import UserLocationCreate
from ..database import get_db
from ..authentication.user_auth import get_current_user
from geopy.distance import geodesic
from datetime import date, datetime

router = APIRouter(
    prefix="/location",
    tags=["location"]
)

MAX_DISTANCE = 5.0


@router.post("/set-fixed-location", status_code=status.HTTP_200_OK)
def set_fixed_location(
    location: UserLocationCreate,
    current_user = Depends(get_current_user),  
    db: Session = Depends(get_db)
):
    fixed = db.query(UserFixedLocation).filter_by(user_id=current_user.id).first()

    if fixed:
        if fixed.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Office location is already locked. To change, send a request to authority."
            )
        fixed.fixed_latitude = location.latitude
        fixed.fixed_longitude = location.longitude
        fixed.updated_at = datetime.utcnow()
        fixed.is_locked = True 
    else:

        fixed = UserFixedLocation(
            user_id=current_user.id,
            fixed_latitude=location.latitude,
            fixed_longitude=location.longitude,
            is_locked=True,  
            updated_at=datetime.utcnow()
        )
        db.add(fixed)

    db.commit()
    db.refresh(fixed)
    return {"message": "Office location set/updated and now locked successfully"}


@router.post("/mark-attendance", status_code=status.HTTP_200_OK)
def mark_attendance(
    location: UserLocationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()

    fixed = db.query(UserFixedLocation).filter_by(user_id=current_user.id).first()
    if not fixed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fixed office location not set yet. Please set it first."
        )

    if not fixed.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Office location must be locked first."
        )

    fixed_point = (fixed.fixed_latitude, fixed.fixed_longitude)
    current_point = (location.latitude, location.longitude)
    distance = geodesic(fixed_point, current_point).meters

    is_present = distance <= MAX_DISTANCE

    existing = db.query(UserAttendance).filter_by(
        user_id=current_user.id,
        attendance_date=today
    ).first()

    if existing:
        existing.current_latitude = location.latitude
        existing.current_longitude = location.longitude
        existing.distance = distance
        existing.is_present = is_present
    else:
        attendance = UserAttendance(
            user_id=current_user.id,
            attendance_date=today,
            current_latitude=location.latitude,
            current_longitude=location.longitude,
            distance=distance,
            is_present=is_present
        )
        db.add(attendance)

    db.commit()
    return {
        "date": str(today),
        "distance": round(distance, 2),
        "is_present": is_present,
        "message": "Present" if is_present else "Absent (moved more than 5m)"
    }


@router.get("/status", status_code=status.HTTP_200_OK)
def get_location_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fixed = db.query(UserFixedLocation).filter_by(user_id=current_user.id).first()
    if not fixed:
        return {
            "is_locked": False,
            "change_request_pending": False,
            "fixed_latitude": None,
            "fixed_longitude": None
        }

    return {
        "is_locked": fixed.is_locked,
        "change_request_pending": fixed.change_request_pending,
        "fixed_latitude": fixed.fixed_latitude,
        "fixed_longitude": fixed.fixed_longitude
    }


@router.post("/request-location-change", status_code=status.HTTP_200_OK)
def request_location_change(
    location: UserLocationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fixed = db.query(UserFixedLocation).filter_by(user_id=current_user.id).first()
    if not fixed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fixed location found. Set it first."
        )

    if not fixed.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is not locked yet."
        )

    fixed.requested_latitude = location.latitude
    fixed.requested_longitude = location.longitude
    fixed.change_request_pending = True
    fixed.requested_at = datetime.utcnow()
    db.commit()

    return {"message": "Location change request sent to authority. Waiting for approval."}





























# @router.post("/set-base-location", status_code=status.HTTP_200_OK)
# def set_base_location(
#     location: LocationRequest,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
    
#     # delete old base if exists
#     db.query(UserLocationHistory).filter(
#         UserLocationHistory.user_id == current_user.id
#     ).delete()

#     record = UserLocationHistory(
#         user_id=current_user.id,
#         base_latitude=location.latitude,
#         base_longitude=location.longitude,
#         current_latitude=location.latitude,
#         current_longitude=location.longitude,
#         distance_from_base=0,
#         is_present=1
#     )

#     db.add(record)
#     db.commit()

#     return {"message": "Base location set & locked"}




# @router.post("/mark-attendance")
# def mark_attendance(
#     location: LocationRequest,
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     today = date.today()

#     already = db.query(UserLocationHistory).filter(
#         UserLocationHistory.user_id == current_user.id,
#         UserLocationHistory.attendance_date == today
#     ).first()

#     if already:
#         return {"message": "Attendance already marked today"}

#     base = db.query(UserLocationHistory).filter(
#         UserLocationHistory.user_id == current_user.id
#     ).first()

#     if not base:
#         return {"error": "Base location not set"}

#     base_point = (base.base_latitude, base.base_longitude)
#     current_point = (location.latitude, location.longitude)

#     distance = geodesic(base_point, current_point).meters
#     is_present = 1 if distance <= MAX_DISTANCE else 0

#     record = UserLocationHistory(
#         user_id=current_user.id,
#         base_latitude=base.base_latitude,
#         base_longitude=base.base_longitude,
#         current_latitude=location.latitude,
#         current_longitude=location.longitude,
#         distance_from_base=distance,
#         is_present=is_present,
#         attendance_date=today
#     )

#     db.add(record)
#     db.commit()

#     return {
#         "distance": distance,
#         "is_present": is_present
#     }



