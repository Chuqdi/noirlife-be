from django.utils import timezone
from utils.expo_notifications import send_push_notification
from utils.geo_utils import distance_to_route_segment, haversine_distance
from users.models import User
from lockeddestinations.models import LockedDestination

ARRIVAL_RADIUS_METERS = 150
DRIFT_THRESHOLD_METERS = 500
MAX_ACCEPTABLE_ACCURACY_METERS = 75
NEAR_START_RADIUS_METERS = 200


def evaluate_location_update(
    user: User,
    lock: LockedDestination,
    latitude: float,
    longitude: float,
    accuracy: float | None = None,
) -> dict:
    """
    Compares a location ping against a user's LockedDestination and
    updates arrived_at / left_at / drifted_at as appropriate.
    Returns a plain dict summarizing what happened.
    """
    starting_coords = lock.starting_coords  # {"latitude": ..., "longitude": ...}
    ending_coords = lock.ending_coords      # {"lat": ..., "lng": ...}

    distance_to_destination = haversine_distance(
        latitude, longitude, ending_coords["lat"], ending_coords["lng"]
    )

    result = {
        "lock_id": lock.id,
        "distance_to_destination_m": round(distance_to_destination, 1),
        "arrived": False,
        "drifted": False,
        "left": False,
    }

    # --- Already arrived: only thing left to check is whether they've left ---
    if lock.arrived_at:
        if not lock.left_at and distance_to_destination > ARRIVAL_RADIUS_METERS:
            lock.left_at = timezone.now()
            lock.save(update_fields=["left_at"])
            result["left"] = True

            print("running left")
            send_push_notification(
                token=user.notification_token,
                body=f"You have left {lock.destination_name}. We will check up to make sure you get home safe.",
                title=f"Left {lock.destination_name}",
            )
        return result

    # --- Not yet arrived: check arrival first ---
    if distance_to_destination <= ARRIVAL_RADIUS_METERS:
        lock.arrived_at = timezone.now()
        lock.is_completed = True
        lock.save(update_fields=["arrived_at", "is_completed"])
        result["arrived"] = True

        print("running arrived")
        send_push_notification(
            token=user.notification_token,
            body=f"You have arrived at {lock.destination_name}. We will check up to make sure you leave on time.",
            title=f"Arrived {lock.destination_name}",
        )
        return result

    # --- Not arrived — check whether they're drifting toward a different destination ---
    if accuracy is not None and accuracy > MAX_ACCEPTABLE_ACCURACY_METERS:
        return result

    distance_from_start = haversine_distance(
        latitude, longitude, starting_coords["latitude"], starting_coords["longitude"]
    )

    if distance_from_start < NEAR_START_RADIUS_METERS:
        return result

    route_deviation = distance_to_route_segment(
        latitude,
        longitude,
        starting_coords["latitude"],
        starting_coords["longitude"],
        ending_coords["lat"],
        ending_coords["lng"],
    )
    result["route_deviation_m"] = round(route_deviation, 1)

    if route_deviation > DRIFT_THRESHOLD_METERS and not lock.drifted_at:
        lock.drifted_at = timezone.now()
        lock.save(update_fields=["drifted_at"])
        result["drifted"] = True

        print("running drifted")
        send_push_notification(
            token=user.notification_token,
            body=f"You have drifted from {lock.destination_name}. If this is expected, please reschedule another location",
            title=f"Drifted from {lock.destination_name}",
        )

    return result


def get_active_lock(user) -> LockedDestination | None:
    return (
        LockedDestination.objects.filter(
            user=user,
            # is_completed=False,
            is_cancelled=False,
        )
        .order_by("-date_time_started")
        .first()
    )