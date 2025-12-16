from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import PlanRequest, PlanResponse
from app.services.optimizer import build_plan
from app.services.refuel_optimizer import find_optimal_refuel_route
from app.db import Base, engine, get_db
from sqlalchemy.orm import Session
from app.services.ports_loader import seed_ports
import os, json
from typing import Dict, Any
from pydantic import BaseModel

# create DB tables on startup if they don't exist (simple approach for MVP)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # On platforms without DB configured (e.g., first deploy), don't crash the app
    print(f"[warn] Skipping DB table creation: {e}")

app = FastAPI(title="Logistics Route Planner (Interactive Multi-Modal)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        db = next(get_db())
        seed_ports(db)
    except Exception as e:
        print(f"[warn] Skipping port seeding: {e}")


@app.post("/plan", response_model=PlanResponse)
def create_plan(req: PlanRequest):
    try:
        plan = build_plan(req)
        return plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class RefuelRequest(BaseModel):
    mode: str
    carrier_model: str
    origin: Dict[str, float]  # {"lat": .., "lon": ..}
    destination: Dict[str, float]
    step_size: float = 1.0
    reserve: float = 0.1
    max_nodes_considered: int = 200


@app.post("/refuel-plan")
def refuel_plan(req: RefuelRequest):
    """
    Runs the state-space refuel optimizer for a single leg.
    Returns: JSON result from find_optimal_refuel_route
    """
    try:
        # load carrier profile
        from app.services.optimizer import load_carrier_profile
        carrier = load_carrier_profile(req.carrier_model)
        if not carrier:
            raise HTTPException(status_code=404, detail="Carrier model not found")

        origin = (req.origin["lat"], req.origin["lon"])
        dest = (req.destination["lat"], req.destination["lon"])

        mode = req.mode
        # map fuel unit by mode
        fuel_unit = "tons" if mode == "ocean" else "liters"
        result = find_optimal_refuel_route(
            origin_coord=origin,
            dest_coord=dest,
            carrier_profile=carrier,
            mode=mode,
            fuel_unit=fuel_unit,
            step_size=req.step_size,
            reserve=req.reserve,
            max_nodes_considered=req.max_nodes_considered
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ports")
def list_ports(db: Session = Depends(get_db)):
    from app.models_orm import Port, Airport, Station
    rows = db.query(Port).all()
    out = []
    from geoalchemy2.shape import to_shape
    for r in rows:
        shp = to_shape(r.geom)
        out.append({
            "id": r.id,
            "name": r.name,
            "lon": shp.x,
            "lat": shp.y,
            "bunker_price": r.bunker_price,
            "port_fee": r.port_fee
        })
    return out


@app.get("/carriers")
def list_carriers():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "carriers.json")
    with open(path, "r") as f:
        carriers = json.load(f)
    # flatten into list with type field
    out = []
    for t, entries in carriers.items():
        for k, v in entries.items():
            item = v.copy()
            item["id"] = k
            item["type"] = t
            out.append(item)
    return out