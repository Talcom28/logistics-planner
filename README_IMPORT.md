# Importing Real-World Port / Airport / Station Datasets

This document explains how to obtain and import datasets so the refuel optimizer can make realistic stop decisions.

Recommended datasets and sources
- UN/LOCODE / World Port List
  - UN/LOCODE (UNECE): https://service.unece.org/trade/locode/
    - UN/LOCODE is authoritative but often requires manual download and may be distributed as zip/CSV.
  - World Port Index (NOAA) / OpenPorts:
    - NOAA World Port Index: https://msi.nga.mil/Publications/WPI
    - OpenPorts / General Index — commercial or scraped lists.
- Airports
  - OurAirports (public): https://ourairports.com/data/
    - Download `airports.csv` and use `app.services.data_importer.import_airports_from_ourairports`.
  - OpenFlights airports dataset: https://openflights.org/data.html
- Road / Rail Stations
  - Use OpenStreetMap extracts (Geofabrik) and filter nodes/ways with tags:
    - rail_station, fuel_station, motorway_service, truck_stop
  - Alternatively use curated CSV lists for truck stops or rail terminals.

Import steps (example)
1. Prepare your PostGIS-enabled database and ensure tables are created:
    - Start DB and run backend once to create tables: Base.metadata.create_all(bind=engine)

2. Download datasets:
    - OurAirports airports.csv -> place in /data/ourairports-airports.csv
    - UN/LOCODE or World Port Index -> place as /data/ports.csv (ensure latitude/longitude columns exist)

3. Run importer:
    - python -m app.services.data_importer import_airports --file data/ourairports-airports.csv
    - python -m app.services.data_importer import_ports --file data/ports.csv
    - python -m app.services.data_importer import_stations --file data/stations.csv

4. After import, verify ports/airports/stations via API:
    - GET /ports  (existing endpoint)
    - (you can add endpoints for /airports and /stations similarly if needed)

Notes & Caveats
- Some datasets need normalization (coordinate columns, different column names). The importer has parameters to adjust column names.
- Fuel prices are typically not included in raw port/airport lists. You may:
  - Augment records manually or via paid feeds (Platts, ClearLynx, airport fuel suppliers).
  - Seed default or region-based prices.
- For high-fidelity routing, combine port geometry with AIS lane data and routing graphs (not implemented here).