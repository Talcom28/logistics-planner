"""Shared utility functions for logistics services (haversine, etc.)."""
from math import radians, sin, cos, sqrt, atan2

KM_PER_NM = 1.852


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points on Earth."""
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def haversine_nm_coords(lat1, lon1, lat2, lon2):
    """Calculate distance in nautical miles between two points on Earth."""
    return haversine_km(lat1, lon1, lat2, lon2) / KM_PER_NM
