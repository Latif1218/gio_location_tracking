from pydantic import BaseModel

class UserLocationCreate(BaseModel):
    latitude: float
    longitude: float
