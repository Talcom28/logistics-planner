from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from .db import Base
from sqlalchemy.orm import relationship

class Port(Base):
    __tablename__ = "ports"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unlocode = Column(String, nullable=True, index=True)
    country = Column(String, nullable=True)
    # geometry as POINT(lon lat)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    # mock last-known bunker price USD/ton
    bunker_price = Column(Float, nullable=True)
    # generic port fee baseline
    port_fee = Column(Float, nullable=True, default=5000.0)


class Airport(Base):
    __tablename__ = "airports"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    iata = Column(String, nullable=True, index=True)
    icao = Column(String, nullable=True, index=True)
    country = Column(String, nullable=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    # jet fuel price USD per liter (optional)
    jet_price_per_l = Column(Float, nullable=True)
    landing_fee = Column(Float, nullable=True, default=0.0)


class Station(Base):
    __tablename__ = "stations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    kind = Column(String, nullable=True)  # e.g., 'truck_stop', 'fuel_station', 'rail_terminal'
    country = Column(String, nullable=True)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    diesel_price_per_l = Column(Float, nullable=True)
    service_fee = Column(Float, nullable=True, default=0.0)


class AISWaypoint(Base):
    __tablename__ = "ais_waypoints"
    id = Column(Integer, primary_key=True, index=True)
    mmsi = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    sog = Column(Float, nullable=True)  # speed over ground
    cog = Column(Float, nullable=True)  # course over ground


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    request = Column(JSON, nullable=False)
    response = Column(JSON, nullable=True)


class PlanLeg(Base):
    __tablename__ = "plan_legs"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"))
    idx = Column(Integer, nullable=False)
    from_name = Column(String)
    to_name = Column(String)
    distance_nm = Column(Float)
    time_hours = Column(Float)
    fuel_needed_tons = Column(Float)
    extra = Column(JSON, nullable=True)