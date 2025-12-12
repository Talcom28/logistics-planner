"""
Dataset importer for:
- UN/LOCODE / World Port List (ports)
- IATA airport lists (OurAirports or OpenFlights)
- Open stations for road/rail (e.g., OpenStreetMap-derived node lists or OurAirports's 'airports.csv' for airports)

This script is a utility to download (or accept local files), parse, and insert records into PostGIS tables:
    ports -> Port
    airports -> Airport
    stations -> Station

Usage (examples):
    python -m app.services.data_importer import_ports --file path/to/UNLOCODE.csv
    python -m app.services.data_importer import_airports --file path/to/ourairports.csv
    python -m app.services.data_importer import_stations --file path/to/stations.csv

Notes:
- Some authoritative sources require registration or manual download (UN/LOCODE). For convenience use public datasets:
  - OurAirports airports.csv: https://ourairports.com/data/
  - OpenPorts / General Index — commercial or scraped lists.
  - OSM extracts (Geofabrik) or https://download.geofabrik.de/ for rail/truck stops; parsing OSM is more involved.

This importer uses SQLAlchemy session to insert records. It expects tables already created (use Base.metadata.create_all).
"""
import csv
import os
import argparse
import tempfile
import requests
from typing import Optional
from app.db import SessionLocal
from app.models_orm import Port, Airport, Station
from geoalchemy2.elements import WKTElement

def _download_if_url(path_or_url: str) -> str:
    if path_or_url.startswith('http://') or path_or_url.startswith('https://'):
        print(f"Downloading {path_or_url}...")
        r = requests.get(path_or_url, stream=True, timeout=30)
        r.raise_for_status()
        tf = tempfile.NamedTemporaryFile(delete=False)
        for chunk in r.iter_content(chunk_size=8192):
            tf.write(chunk)
        tf.close()
        return tf.name
    return path_or_url


def import_ports_from_csv(file_path: str, unlocode_col='UN/LOCODE', name_col='Name', lon_col='Longitude', lat_col='Latitude', country_col='Country', price_col=None):
    """Import ports CSV into `ports` table. Accepts local path or HTTP URL."""
    src = _download_if_url(file_path)
    db = SessionLocal()
    try:
        with open(src, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            count = 0
            to_commit = 0
            for row in reader:
                try:
                    lon = float(row.get(lon_col) or row.get('lon') or row.get('longitude'))
                    lat = float(row.get(lat_col) or row.get('lat') or row.get('latitude'))
                except Exception:
                    continue
                name = row.get(name_col) or row.get('NAME') or row.get('name') or ''
                unloc = row.get(unlocode_col) or ''
                country = row.get(country_col) or row.get('Country') or ''
                try:
                    bunker_price = float(row.get(price_col)) if price_col and row.get(price_col) else None
                except Exception:
                    bunker_price = None

                pt = WKTElement(f"POINT({lon} {lat})", srid=4326)

                # upsert by UN/LOCODE when available, otherwise insert
                existing = None
                if unloc:
                    existing = db.query(Port).filter(Port.unlocode == unloc).first()

                if existing is None:
                    port = Port(name=name, unlocode=unloc or None, country=country, geom=pt, bunker_price=bunker_price)
                    db.add(port)
                else:
                    existing.name = name or existing.name
                    existing.country = country or existing.country
                    existing.geom = pt
                    existing.bunker_price = bunker_price or existing.bunker_price

                count += 1
                to_commit += 1
                if to_commit >= 500:
                    db.commit()
                    to_commit = 0
            db.commit()
    finally:
        db.close()

    print(f"Imported/updated {count} ports from {file_path}")


def import_airports_from_ourairports(file_path: str):
    """
    OurAirports airports.csv fields include:
    id,name,latitude_deg,longitude_deg,elevation_ft,continent,iso_country,iso_region,municipality,iata,icao,timezone
    """
    src = _download_if_url(file_path)
    db = SessionLocal()
    try:
        with open(src, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            count = 0
            to_commit = 0
            for row in reader:
                try:
                    lon = float(row.get('longitude_deg'))
                    lat = float(row.get('latitude_deg'))
                except Exception:
                    continue
                name = row.get('name') or ''
                iata = row.get('iata') or None
                icao = row.get('icao') or None
                country = row.get('iso_country') or None
                pt = WKTElement(f"POINT({lon} {lat})", srid=4326)

                # upsert by IATA or ICAO where present
                existing = None
                if iata:
                    existing = db.query(Airport).filter(Airport.iata == iata).first()
                if existing is None and icao:
                    existing = db.query(Airport).filter(Airport.icao == icao).first()

                if existing is None:
                    airport = Airport(name=name, iata=iata, icao=icao, country=country, geom=pt)
                    db.add(airport)
                else:
                    existing.name = name or existing.name
                    existing.country = country or existing.country
                    existing.geom = pt

                count += 1
                to_commit += 1
                if to_commit >= 500:
                    db.commit()
                    to_commit = 0
            db.commit()
    finally:
        db.close()

    print(f"Imported/updated {count} airports from {file_path}")


def import_stations_from_csv(file_path: str, lon_col='lon', lat_col='lat', name_col='name', kind_col='kind', price_col=None):
    src = _download_if_url(file_path)
    db = SessionLocal()
    try:
        with open(src, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            count = 0
            to_commit = 0
            for row in reader:
                try:
                    lon = float(row.get(lon_col))
                    lat = float(row.get(lat_col))
                except Exception:
                    continue
                name = row.get(name_col) or ''
                kind = row.get(kind_col) or ''
                try:
                    diesel_price = float(row.get(price_col)) if price_col and row.get(price_col) else None
                except Exception:
                    diesel_price = None
                pt = WKTElement(f"POINT({lon} {lat})", srid=4326)

                # naive upsert by name + location
                existing = None
                if name:
                    existing = db.query(Station).filter(Station.name == name).first()

                if existing is None:
                    st = Station(name=name or None, kind=kind or None, country=row.get('country'), geom=pt, diesel_price_per_l=diesel_price)
                    db.add(st)
                else:
                    existing.kind = kind or existing.kind
                    existing.country = row.get('country') or existing.country
                    existing.geom = pt
                    existing.diesel_price_per_l = diesel_price or existing.diesel_price_per_l

                count += 1
                to_commit += 1
                if to_commit >= 500:
                    db.commit()
                    to_commit = 0
            db.commit()
    finally:
        db.close()

    print(f"Imported/updated {count} stations from {file_path}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')

    p_ports = sub.add_parser('import_ports')
    p_ports.add_argument('--file', required=True)

    p_air = sub.add_parser('import_airports')
    p_air.add_argument('--file', required=True)

    p_st = sub.add_parser('import_stations')
    p_st.add_argument('--file', required=True)

    args = parser.parse_args()
    if args.cmd == 'import_ports':
        import_ports_from_csv(args.file)
    elif args.cmd == 'import_airports':
        import_airports_from_ourairports(args.file)
    elif args.cmd == 'import_stations':
        import_stations_from_csv(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()