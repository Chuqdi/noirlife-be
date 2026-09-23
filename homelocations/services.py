from django.utils import timezone
from utils.expo_notifications import send_push_notification
from utils.geo_utils import haversine_distance
from users.models import User
from .models import HomeLocation

# Must be within this distance of home to be considered "arrived"
HOME_RADIUS_METERS = 150

# Extra buffer beyond HOME_RADIUS_METERS required before confirming "left".
# This hysteresis gap prevents GPS jitter right at the boundary from
# flip-flopping the state (and spamming notifications) back and forth.
HOME_EXIT_BUFFER_METERS = 100
HOME_EXIT_RADIUS_METERS = HOME_RADIUS_METERS + HOME_EXIT_BUFFER_METERS

MAX_ACCEPTABLE_ACCURACY_METERS = 75


def evaluate_home_location_update(
    user: User,
    latitude: float,
    longitude: float,
    accuracy: float | None = None,
) -> dict:
    """
    Compares a location ping against the user's HomeLocation and updates
    is_home / left_home_at / arrived_home_at as appropriate. Sends a push
    notification exactly once per confirmed state transition.

    Returns a plain dict summarizing what happened.
    """
    result = {
        "has_home": False,
        "skipped": False,
        "skipped_reason": None,
        "left": False,
        "arrived": False,
        "is_home": None,
        "distance_to_home_m": None,
    }

    home = HomeLocation.objects.filter(user=user).first()
    print(home.coords)
    if home is None:
        result["skipped"] = True
        result["skipped_reason"] = "no_home_location_set"
        return result

    result["has_home"] = True

    home_lat, home_lng = _extract_coords(home.coords)
    if home_lat is None or home_lng is None:
        result["skipped"] = True
        result["skipped_reason"] = "invalid_home_coords"
        return result

    # --- Poor GPS fix: don't let a bad reading flip presence state ---
    if accuracy is not None and accuracy > MAX_ACCEPTABLE_ACCURACY_METERS:
        result["skipped"] = True
        result["skipped_reason"] = "low_accuracy"
        result["is_home"] = home.is_home
        return result

    distance_to_home = haversine_distance(latitude, longitude, home_lat, home_lng)
    result["distance_to_home_m"] = round(distance_to_home, 1)

    # --- First-ever reading for this user: establish baseline silently ---
    # We don't know their prior state, so we can't claim they "left" or
    # "arrived" — we just record where they currently are.
    if home.is_home is None:
        home.is_home = distance_to_home <= HOME_RADIUS_METERS
        if home.is_home:
            home.arrived_home_at = timezone.now()
        else:
            home.left_home_at = timezone.now()
        home.save(update_fields=["is_home", "arrived_home_at", "left_home_at"])
        result["is_home"] = home.is_home
        return result

    # --- Currently marked HOME: only care about a confirmed departure ---
    if home.is_home:
        if distance_to_home > HOME_EXIT_RADIUS_METERS:
            home.is_home = False
            home.left_home_at = timezone.now()
            home.save(update_fields=["is_home", "left_home_at"])
            result["left"] = True
            result["is_home"] = False

            if user.notification_token:
                send_push_notification(
                    token=user.notification_token,
                    title="Left home",
                    body="We noticed you've left home. Make sure to lock your destination for safety",
                )
        else:
            # Still within the buffer zone or still near home — no change.
            result["is_home"] = True
        return result

    # --- Currently marked AWAY: only care about a confirmed arrival ---
    if distance_to_home <= HOME_RADIUS_METERS:
        home.is_home = True
        home.arrived_home_at = timezone.now()
        home.save(update_fields=["is_home", "arrived_home_at"])
        result["arrived"] = True
        result["is_home"] = True

        if user.notification_token:
            send_push_notification(
                token=user.notification_token,
                title="Welcome home",
                body="Glad you're home safe.",
            )
    else:
        # Still away, outside the radius — no change.
        result["is_home"] = False

    return result


def _extract_coords(coords: dict | None) -> tuple[float | None, float | None]:
    """
    HomeLocation.coords is a loosely-typed JSONField. Support both
    {"latitude": ..., "longitude": ...} and {"lat": ..., "lng": ...}
    shapes so this doesn't break depending on how it was saved.
    """
    if not coords:
        return None, None

    lat = coords.get("latitude", coords.get("lat"))
    lng = coords.get("longitude", coords.get("lng"))

    if lat is None or lng is None:
        return None, None

    try:
        return float(lat), float(lng)
    except (TypeError, ValueError):
        return None, None