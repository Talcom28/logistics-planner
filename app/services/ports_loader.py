"""
Simple port loader for MVP: seeds a few major hubs with coordinates and sample bunker prices.

In production, load a full UN/World Port List with UN/LOCODEs and pricing feeds.
"""
from sqlalchemy.orm import Session
from app.models_orm import Port
from geoalchemy2.elements import WKTElement

SAMPLE_PORTS = [
    {"name": "Rotterdam", "unlocode": "NLRTM", "country": "NL", "lon": 4.136, "lat": 51.947, "bunker_price": 600.0, "port_fee": 5000.0},
    {"name": "Bremerhaven", "unlocode": "DEBRV", "country": "DE", "lon": 8.586, "lat": 53.543, "bunker_price": 605.0, "port_fee": 4800.0},
    {"name": "Singapore", "unlocode": "SGSIN", "country": "SG", "lon": 103.8198, "lat": 1.3521, "bunker_price": 620.0, "port_fee": 7000.0},
    {"name": "Hong Kong", "unlocode": "HKHKG", "country": "HK", "lon": 114.1095, "lat": 22.3964, "bunker_price": 610.0, "port_fee": 6500.0},
    {"name": "Shanghai", "unlocode": "CNSHG", "country": "CN", "lon": 121.4737, "lat": 31.2304, "bunker_price": 615.0, "port_fee": 7200.0},
]


def seed_ports(db: Session):
    existing = db.query(Port).count()
    if existing > 0:
        return
    for p in SAMPLE_PORTS:
        pt = WKTElement(f"POINT({p['lon']} {p['lat']})", srid=4326)
        port = Port(
            name=p["name"],
            unlocode=p["unlocode"],
            country=p["country"],
            geom=pt,
            bunker_price=p["bunker_price"],
            port_fee=p["port_fee"],
        )
        db.add(port)
    db.commit()