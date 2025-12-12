# Replace your existing build_plan in this file with this updated version.
from app.models import PlanRequest, PlanResponse, FuelStop, LegDetail, Coordinate
from app.services.paperwork import generate_paperwork
from app.services.fuel_service import (
    get_bunker_price_for_port,
    get_diesel_price_for_region,
    get_jet_price_for_region,
)
from app.db import SessionLocal
from app.models_orm import Port, Plan, PlanLeg
from geoalchemy2.shape import to_shape
from app.services.utils import haversine_km, haversine_nm_coords
from math import ceil
import uuid
import heapq
import json
import os

# import refuel optimizer
from app.services.refuel_optimizer import find_optimal_refuel_route

KM_PER_NM = 1.852
HOURS_PER_DAY = 24.0


def load_carrier_profile(carrier_key: str):
    """Load a carrier model by its key."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "carriers.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        carriers = json.load(f)
    for mode, models in carriers.items():
        if carrier_key in models:
            return models[carrier_key]
    return None


def find_nearest_port(db, lat: float, lon: float):
    """Find nearest port to a coordinate."""
    ports = db.query(Port).all()
    nearest = None
    best_dist = float("inf")
    for p in ports:
        shp = to_shape(p.geom)
        d = haversine_km(lat, lon, shp.y, shp.x)
        if d < best_dist:
            best_dist = d
            nearest = p
    return nearest


def compute_leg_mode_info(mode: str, carrier: dict, a: Coordinate, b: Coordinate) -> dict:
    """Compute basic leg information: distance, time, fuel."""
    dist_km = haversine_km(a.lat, a.lon, b.lat, b.lon)
    dist_nm = dist_km / KM_PER_NM
    
    if mode == "ocean":
        speed_knots = carrier.get("service_speed_knots", 14.0)
        consumption = carrier.get("consumption_tons_per_nm", 0.1)
        time_hours = dist_nm / speed_knots
        fuel_needed = dist_nm * consumption
    elif mode == "air":
        speed_kmh = carrier.get("cruise_speed_kmh", 800.0)
        consumption = carrier.get("consumption_l_per_km", 0.05)
        time_hours = dist_km / speed_kmh
        fuel_needed = dist_km * consumption
    elif mode == "road":
        speed_kmh = carrier.get("cruise_speed_kmh", 70.0)
        consumption = carrier.get("consumption_l_per_km", 0.08)
        time_hours = dist_km / speed_kmh
        fuel_needed = dist_km * consumption
    elif mode == "rail":
        speed_kmh = carrier.get("cruise_speed_kmh", 40.0)
        consumption = carrier.get("consumption_l_per_km", 0.05)
        time_hours = dist_km / speed_kmh
        fuel_needed = dist_km * consumption
    else:
        speed_kmh = 50.0
        consumption = 0.1
        time_hours = dist_km / speed_kmh
        fuel_needed = dist_km * consumption
    
    return {
        "distance_km": dist_km,
        "distance_nm": dist_nm,
        "time_hours": time_hours,
        "fuel_needed": fuel_needed
    }


def iter_mode_first(model_type: str):
    """Iterate through models of a specific type."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "carriers.json")
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        carriers = json.load(f)
    if model_type in carriers:
        for key in carriers[model_type]:
            yield key


def build_plan(req: PlanRequest, carrier_profile: dict = None) -> PlanResponse:
    db = next(SessionLocal())
    from app.services.ports_loader import seed_ports

    seed_ports(db)

    # prepare nodes list as before
    destinations = req.destinations
    nodes = []
    origin = Coordinate(lat=req.origin.lat, lon=req.origin.lon)
    nodes.append({"coord": origin, "mode": None, "name": "Origin"})

    for d in destinations:
        nodes.append({"coord": d.coord, "mode": d.mode or req.transport_medium, "name": d.name or "Dest"})

    # prepare default carrier if not provided (existing logic)
    if req.carrier_model:
        selected_carrier = load_carrier_profile(req.carrier_model)
    else:
        # auto-pick default for primary transport medium
        path = os.path.join(os.path.dirname(__file__), "..", "data", "carriers.json")
        with open(path, "r") as f:
            carriers_all = json.load(f)
        selected_carrier = None
        if req.transport_medium in carriers_all:
            first_key = next(iter(carriers_all[req.transport_medium]))
            selected_carrier = carriers_all[req.transport_medium][first_key]
        else:
            first_cat = next(iter(carriers_all))
            first_model = next(iter(carriers_all[first_cat]))
            selected_carrier = carriers_all[first_cat][first_model]

    leg_details = []
    total_distance_km = 0.0
    total_distance_nm = 0.0
    total_time_hours = 0.0
    total_fuel_amount = 0.0
    total_cost = 0.0
    fuel_plan = []
    stops = 0

    # iterate legs; for each leg we compute basic metrics and, when supported, call precise refuel optimizer
    for idx in range(len(nodes) - 1):
        a = nodes[idx]["coord"]
        b = nodes[idx + 1]["coord"]
        mode = nodes[idx + 1]["mode"] or req.transport_medium

        # choose carrier for this leg (if selected_carrier matches mode use it; else pick default for that mode)
        carrier = selected_carrier
        if carrier.get("type") != mode:
            # attempt to load a carrier matching the mode
            try:
                candidate_key = next(iter_mode_first(model_type=mode))
                if candidate_key:
                    candidate = load_carrier_profile(candidate_key)
                    if candidate:
                        carrier = candidate
            except Exception:
                carrier = selected_carrier  # fallback

        # compute coarse leg info
        info = compute_leg_mode_info(mode, carrier, a, b)

        # For modes supported by the refuel optimizer, call it to get precise refuel plan for this leg.
        if mode in {"ocean", "air", "road", "rail"}:
            # call refuel optimizer for this single leg
            try:
                # choose step_size heuristics by mode
                if mode == "ocean":
                    step_size = 1.0  # 1 ton increments
                    fuel_unit = "tons"
                elif mode == "air":
                    step_size = 100.0  # liters resolution
                    fuel_unit = "liters"
                else:
                    step_size = 50.0  # liters for road/rail
                    fuel_unit = "liters"

                refuel_result = find_optimal_refuel_route(
                    origin_coord=(a.lat, a.lon),
                    dest_coord=(b.lat, b.lon),
                    carrier_profile=carrier,
                    mode=mode,
                    fuel_unit=fuel_unit,
                    step_size=step_size,
                    reserve=0.1,
                    max_nodes_considered=200
                )
                # Merge results: add fuel plan entries and leg(s)
                if "fuel_plan" in refuel_result:
                    # each entry has node, added_amount, price_per_unit, cost
                    for entry in refuel_result["fuel_plan"]:
                        # normalize keys for response model
                        fuel_plan.append(FuelStop(
                            port=entry.get("node"),
                            amount_tons_or_liters=round(entry.get("added_amount"), 3),
                            price_per_unit_usd=round(entry.get("price_per_unit"), 3),
                            cost_usd=round(entry.get("cost"), 2)
                        ))
                        total_cost += float(entry.get("cost", 0.0))
                # legs
                if "legs" in refuel_result:
                    for leg in refuel_result["legs"]:
                        leg_details.append(LegDetail(
                            from_coord=Coordinate(lat=a.lat, lon=a.lon),
                            to_coord=Coordinate(lat=b.lat, lon=b.lon),
                            mode=mode,
                            distance_km=round(info["distance_km"], 2),
                            distance_nm=round(info["distance_nm"], 2),
                            time_hours=round(info["time_hours"], 2),
                            fuel_needed=round(info["fuel_needed"], 3),
                            fuel_unit=fuel_unit,
                            port_fees_usd=0.0
                        ))
                        total_distance_km += info["distance_km"]
                        total_distance_nm += info["distance_nm"]
                        total_time_hours += info["time_hours"]
                        total_fuel_amount += info["fuel_needed"]
                else:
                    # fallback: add coarse info
                    leg_details.append(LegDetail(
                        from_coord=a,
                        to_coord=b,
                        mode=mode,
                        distance_km=round(info["distance_km"], 2),
                        distance_nm=round(info["distance_nm"], 2),
                        time_hours=round(info["time_hours"], 2),
                        fuel_needed=round(info["fuel_needed"], 3),
                        fuel_unit=fuel_unit,
                        port_fees_usd=0.0
                    ))
                    total_distance_km += info["distance_km"]
                    total_distance_nm += info["distance_nm"]
                    total_time_hours += info["time_hours"]
                    total_fuel_amount += info["fuel_needed"]

            except Exception as e:
                # if refuel optimizer fails, fallback to simple heuristics (previous logic)
                leg_details.append(LegDetail(
                    from_coord=a,
                    to_coord=b,
                    mode=mode,
                    distance_km=round(info["distance_km"], 2),
                    distance_nm=round(info["distance_nm"], 2),
                    time_hours=round(info["time_hours"], 2),
                    fuel_needed=round(info["fuel_needed"], 3),
                    fuel_unit=("tons" if mode == "ocean" else "liters"),
                    port_fees_usd=0.0
                ))
                total_distance_km += info["distance_km"]
                total_distance_nm += info["distance_nm"]
                total_time_hours += info["time_hours"]
                total_fuel_amount += info["fuel_needed"]
        else:
            # unsupported mode: add simple dimensions
            leg_details.append(LegDetail(
                from_coord=a,
                to_coord=b,
                mode=mode,
                distance_km=round(info["distance_km"], 2),
                distance_nm=round(info["distance_nm"], 2),
                time_hours=round(info["time_hours"], 2),
                fuel_needed=round(info["fuel_needed"], 3),
                fuel_unit=("tons" if mode == "ocean" else "liters"),
                port_fees_usd=0.0
            ))
            total_distance_km += info["distance_km"]
            total_distance_nm += info["distance_nm"]
            total_time_hours += info["time_hours"]
            total_fuel_amount += info["fuel_needed"]

    # simplistic risk score
    risk_score = min(100.0, 10.0 + 0.005 * total_distance_km + (20.0 if req.cargo_type.lower() in {"hazardous", "dangerous"} else 0.0))

    paperwork = generate_paperwork(req.cargo_type)

    route_id = str(uuid.uuid4())
    response_payload = {
        "route_id": route_id,
        "total_distance_km": round(total_distance_km, 2),
        "total_distance_nm": round(total_distance_nm, 2),
        "total_time_hours": round(total_time_hours, 2),
        "total_fuel": round(total_fuel_amount, 3),
        "total_fuel_unit": ("tons" if any(ld.fuel_unit == "tons" for ld in leg_details) else "liters"),
        "total_cost_usd": round(total_cost, 2),
        "fuel_plan": [s.dict() for s in fuel_plan],
        "stops": len(fuel_plan),
        "risk_score": round(risk_score, 2),
        "paperwork": paperwork,
        "leg_details": [ld.dict() for ld in leg_details],
    }

    # persist plan
    plan = Plan(route_id=route_id, request=json.loads(json.dumps(req.dict())), response=response_payload)
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # persist legs
    for idx, ld in enumerate(leg_details):
        pl = PlanLeg(plan_id=plan.id, idx=idx, from_name=str(ld.from_coord.dict()), to_name=str(ld.to_coord.dict()), distance_nm=ld.distance_nm, time_hours=ld.time_hours, fuel_needed_tons=ld.fuel_needed if ld.fuel_unit == "tons" else None, extra=None)
        db.add(pl)
    db.commit()

    return PlanResponse(**response_payload)