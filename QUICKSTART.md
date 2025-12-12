# 🚀 Quick Start Guide

## 1-Minute Setup (Docker)

```bash
cd c:\Users\ashva\Downloads\Chat
docker-compose up
```

Then open:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

## 5-Minute Manual Setup

### Prerequisites
- Python 3.11+
- PostgreSQL with PostGIS
- Node.js 18+ (for frontend)

### Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set database URL (or use docker postgres)
# Windows PowerShell:
$env:DATABASE_URL="postgresql+psycopg2://logistics:logistics@localhost:5432/logistics"

# Linux/Mac bash:
export DATABASE_URL="postgresql+psycopg2://logistics:logistics@localhost:5432/logistics"

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Opens on http://localhost:5173
```

## Test It Out

### Option 1: Interactive Web UI
1. Open http://localhost:3000
2. Select transport mode (Ocean, Air, Road, Rail)
3. Choose carrier model
4. Click map to set origin & destination
5. Click "Compute Plan"

### Option 2: API Call
```bash
python sample_run.py
```

### Option 3: cURL
```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "transport_medium": "ocean",
  "cargo_type": "hazardous",
  "cargo_quantity": 500,
  "unit": "tons",
  "carrier_model": "bulkcarrier-75000DWT",
  "origin": {"lat": 51.947, "lon": 4.136},
  "destinations": [
    {
      "coord": {"lat": 31.2304, "lon": 121.4737},
      "mode": "ocean"
    }
  ]
}
EOF
```

## Available Carriers

### Ocean (3 models)
- `bulkcarrier-75000DWT` - General bulk cargo
- `containership-20000TEU` - Containerized goods
- `tanker-crude-300000` - Liquid cargo

### Air (3 models)
- `boeing-777F` - Wide-body freighter
- `airbus-A380F` - Super-large freighter
- `cessna-208-caravan` - Small cargo

### Road (3 models)
- `articulated-truck-40T` - Long-haul semi
- `box-truck-7.5T` - European distribution
- `van-3.5T` - Last-mile delivery

### Rail (2 models)
- `freight-locomotive-diesel` - Powered unit
- `boxcar-60T` - Freight wagon

## Response Example

```json
{
  "route_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "total_distance_km": 10700.5,
  "total_distance_nm": 5783.2,
  "total_time_hours": 738.6,
  "total_fuel": 856.0,
  "total_fuel_unit": "tons",
  "total_cost_usd": 512400.0,
  "fuel_plan": [
    {
      "port": "Rotterdam",
      "amount_tons_or_liters": 750.0,
      "price_per_unit_usd": 600.0,
      "cost_usd": 450000.0
    }
  ],
  "stops": 1,
  "risk_score": 35.5,
  "paperwork": [
    "Bill of Lading",
    "Commercial Invoice",
    "Packing List",
    "IMDG Declaration",
    "Safety Data Sheet (SDS)",
    "UN Number documentation"
  ],
  "leg_details": [
    {
      "from_coord": {"lat": 51.947, "lon": 4.136},
      "to_coord": {"lat": 31.2304, "lon": 121.4737},
      "mode": "ocean",
      "distance_km": 10700.5,
      "distance_nm": 5783.2,
      "time_hours": 738.6,
      "fuel_needed": 856.0,
      "fuel_unit": "tons",
      "port_fees_usd": 0.0
    }
  ]
}
```

## Environment Variables

### Backend
```bash
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
PYTHONUNBUFFERED=1
```

### Frontend (vite)
```bash
VITE_BACKEND_URL=http://localhost:8000
```

## Common Issues

### "No feasible route found"
- Carrier fuel capacity too small for distance
- Try longer-range carrier or add refuel stops
- Check that ports/airports exist in database

### Database connection errors
- Ensure PostgreSQL + PostGIS running
- Check DATABASE_URL environment variable
- Verify credentials match docker-compose.yml

### Frontend can't reach API
- Ensure backend running on port 8000
- Check CORS is enabled (should be by default)
- Verify VITE_BACKEND_URL points to correct API

## Import Real Data

```bash
# After database is running and tables created:

# Import UN/LOCODE ports
python -m app.services.data_importer import_ports \
  --file data/ports.csv

# Import OurAirports data
python -m app.services.data_importer import_airports \
  --file data/airports.csv

# Import road/rail stations
python -m app.services.data_importer import_stations \
  --file data/stations.csv
```

See [README_IMPORT.md](README_IMPORT.md) for dataset sources.

## Useful Links

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Source Code**: [app/](app/)
- **Data Model**: [app/models.py](app/models.py)
- **ORM Models**: [app/models_orm.py](app/models_orm.py)

## Next Steps

1. ✅ API works? → Import real port/airport data
2. ✅ UI works? → Customize styling in frontend/src/App.jsx
3. ✅ Routes optimize? → Connect live fuel pricing APIs
4. ✅ All good? → Deploy to production with docker-compose

## Need Help?

- **Error logs**: Check backend console output (uvicorn)
- **Database issues**: Connect with `psql` and inspect tables
- **Frontend issues**: Check browser console (F12)
- **API issues**: Visit http://localhost:8000/docs for interactive testing

Happy routing! 🌍✈️🚢🚚🚂