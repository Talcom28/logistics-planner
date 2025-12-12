from pydantic import BaseModel, Field, conlist
from typing import List, Optional, Any, Literal


class Coordinate(BaseModel):
    lat: float
    lon: float


class Destination(BaseModel):
    coord: Coordinate
    mode: Optional[Literal["ocean", "air", "road", "rail"]] = None
    name: Optional[str] = None


class PlanRequest(BaseModel):
    # transport_medium is the default if per-leg mode not provided.
    transport_medium: Optional[Literal["ocean", "air", "road", "rail", "multi-modal"]] = Field(
        "ocean", description="Default transport medium; individual destinations can override via mode"
    )
    cargo_type: str = Field(..., example="bulk")
    cargo_quantity: float = Field(..., example=500.0)
    unit: str = Field(..., example="tons")
    carrier_model: Optional[str] = Field(None, example="bulkcarrier-75000DWT")
    origin: Coordinate
    # destinations is a list of Destination objects (each may specify mode); legacy support: accept simple list of coords
    destinations: List[Destination] = Field(..., min_items=1)
    preferences: Optional[str] = Field("cheapest", example="cheapest")
    constraints: Optional[dict] = None


class FuelStop(BaseModel):
    port: str
    amount_tons_or_liters: float
    price_per_unit_usd: float
    cost_usd: float


class LegDetail(BaseModel):
    from_coord: Coordinate
    to_coord: Coordinate
    mode: str
    distance_km: float
    distance_nm: float
    time_hours: float
    fuel_needed: float
    fuel_unit: str
    port_fees_usd: float = 0.0


class PlanResponse(BaseModel):
    route_id: str
    total_distance_km: float
    total_distance_nm: float
    total_time_hours: float
    total_fuel: float
    total_fuel_unit: str
    total_cost_usd: float
    fuel_plan: List[FuelStop]
    stops: int
    risk_score: float
    paperwork: List[str]
    leg_details: List[LegDetail]
    raw: Optional[Any] = None