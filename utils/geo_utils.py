import math

EARTH_RADIUS_METERS = 6371000


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points, in meters."""
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    h = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(d_lng / 2) ** 2
    )
    return EARTH_RADIUS_METERS * 2 * math.asin(math.sqrt(h))


def _to_local_xy(lat: float, lng: float, origin_lat: float, origin_lng: float) -> tuple[float, float]:
    """Project a lat/lng to a flat x/y plane (meters) relative to an origin.
    Fine for distances up to a few tens of km — no need for full great-circle math."""
    lat_rad = math.radians(origin_lat)
    d_lat = math.radians(lat - origin_lat)
    d_lng = math.radians(lng - origin_lng)
    x = d_lng * math.cos(lat_rad) * EARTH_RADIUS_METERS
    y = d_lat * EARTH_RADIUS_METERS
    return x, y


def distance_to_route_segment(
    point_lat: float,
    point_lng: float,
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
) -> float:
    """Shortest distance (meters) from `point` to the line segment start->end.
    Clamped so points "beyond" either end just measure to that endpoint."""
    px, py = _to_local_xy(point_lat, point_lng, start_lat, start_lng)
    ax, ay = 0.0, 0.0
    bx, by = _to_local_xy(end_lat, end_lng, start_lat, start_lng)

    ab_x, ab_y = bx - ax, by - ay
    ap_x, ap_y = px - ax, py - ay
    ab_len_sq = ab_x ** 2 + ab_y ** 2

    t = 0.0 if ab_len_sq == 0 else (ap_x * ab_x + ap_y * ab_y) / ab_len_sq
    t = max(0.0, min(1.0, t))

    closest_x = ax + ab_x * t
    closest_y = ay + ab_y * t
    dx, dy = px - closest_x, py - closest_y
    return math.sqrt(dx ** 2 + dy ** 2)