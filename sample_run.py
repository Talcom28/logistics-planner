import requests
import json

API_URL = "http://127.0.0.1:8000/plan"

payload = {
  "transport_medium": "ocean",
  "cargo_type": "hazardous",
  "cargo_quantity": 500,
  "unit": "tons",
  "carrier_model": "bulkcarrier-75000DWT",
  "origin": {"lat": 51.947, "lon": 4.136},   # Rotterdam approx
  "destinations": [
    {"coord": {"lat": 30.0444, "lon": 31.2357}, "mode": "ocean"},   # Suez / near
    {"coord": {"lat": 31.2304, "lon": 121.4737}, "mode": "ocean"}   # Shanghai approx
  ],
  "preferences": "cheapest"
}

if __name__ == "__main__":
    r = requests.post(API_URL, json=payload)
    print("Status:", r.status_code)
    print(json.dumps(r.json(), indent=2))