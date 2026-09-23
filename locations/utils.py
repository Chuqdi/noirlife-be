from users.models import User
from .models import UserLocationPing
from typing import TypedDict, Optional
class LocationPayload(TypedDict):
    latitude: float
    longitude: float
    accuracy: Optional[float]
    
    
    
    
def updateUserLocation(user:User, coordinates:LocationPayload):
    location, _ = UserLocationPing.objects.update_or_create(
        user=user,
        defaults={**coordinates},
    )
    return location