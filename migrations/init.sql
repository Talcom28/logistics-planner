-- Run this script once after DB is ready (or use Alembic for migrations)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ports, ais_waypoints, plans and plan_legs created by SQLAlchemy if you prefer