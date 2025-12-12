"""
Interactive Streamlit app for Logistics Route Planner.
Connects to the FastAPI backend at http://localhost:8000.
"""
import streamlit as st
import requests
import json
from typing import List, Dict, Any

st.set_page_config(page_title="Logistics Route Planner", layout="wide")

st.title("🚚 Logistics Route Planner (Interactive)")
st.write("Plan multi-modal logistics routes with fuel optimization.")

# Backend URL
BACKEND_URL = st.sidebar.text_input("Backend URL", "http://localhost:8000")

# Sidebar: Input parameters
st.sidebar.header("Route Parameters")

origin_lat = st.sidebar.number_input("Origin Latitude", value=40.7128)
origin_lon = st.sidebar.number_input("Origin Longitude", value=-74.0060)
dest_lat = st.sidebar.number_input("Destination Latitude", value=51.5074)
dest_lon = st.sidebar.number_input("Destination Longitude", value=-0.1278)

cargo_type = st.sidebar.text_input("Cargo Type", "general")
cargo_qty = st.sidebar.number_input("Cargo Quantity", min_value=1.0, value=100.0)
transport_mode = st.sidebar.selectbox("Transport Mode", ["ocean", "air", "road", "rail", "multi-modal"])
carrier_model = st.sidebar.text_input("Carrier Model (optional)", "")

# Main area: Show available ports & carriers
col1, col2 = st.columns(2)

with col1:
    if st.button("Load Available Ports"):
        try:
            resp = requests.get(f"{BACKEND_URL}/ports", timeout=5)
            if resp.status_code == 200:
                ports = resp.json()
                st.write(f"**Available Ports ({len(ports)})**")
                for p in ports[:10]:
                    st.write(f"- {p['name']} (Bunker: ${p.get('bunker_price', 'N/A')}/ton)")
            else:
                st.error(f"Backend returned {resp.status_code}")
        except requests.exceptions.ConnectionError:
            st.error(f"Cannot connect to backend at {BACKEND_URL}")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("Load Available Carriers"):
        try:
            resp = requests.get(f"{BACKEND_URL}/carriers", timeout=5)
            if resp.status_code == 200:
                carriers = resp.json()
                st.write(f"**Available Carriers ({len(carriers)})**")
                for c in carriers[:10]:
                    st.write(f"- {c.get('id')} ({c.get('type')})")
            else:
                st.error(f"Backend returned {resp.status_code}")
        except requests.exceptions.ConnectionError:
            st.error(f"Cannot connect to backend at {BACKEND_URL}")
        except Exception as e:
            st.error(f"Error: {e}")

# Plan button
st.header("Generate Plan")
if st.button("Plan Route"):
    payload = {
        "origin": {"lat": origin_lat, "lon": origin_lon},
        "destinations": [{"coord": {"lat": dest_lat, "lon": dest_lon}, "mode": transport_mode}],
        "cargo_type": cargo_type,
        "cargo_quantity": cargo_qty,
        "unit": "tons",
        "transport_medium": transport_mode,
        "carrier_model": carrier_model if carrier_model else None,
        "preferences": "cheapest"
    }
    
    try:
        with st.spinner("Planning route..."):
            resp = requests.post(f"{BACKEND_URL}/plan", json=payload, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            st.success("Route planned successfully!")
            
            # Display summary
            st.subheader("Route Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Distance (NM)", f"{result.get('total_distance_nm', 0):.1f}")
            col2.metric("Time (hrs)", f"{result.get('total_time_hours', 0):.1f}")
            col3.metric("Fuel Needed", f"{result.get('total_fuel', 0):.1f} {result.get('total_fuel_unit', 'units')}")
            col4.metric("Total Cost", f"${result.get('total_cost_usd', 0):.2f}")
            
            # Leg details
            if result.get("leg_details"):
                st.subheader("Leg Details")
                for i, leg in enumerate(result["leg_details"]):
                    st.write(f"**Leg {i+1}** ({leg['mode']})")
                    st.write(f"- Distance: {leg['distance_nm']:.1f} NM / {leg['distance_km']:.1f} km")
                    st.write(f"- Time: {leg['time_hours']:.1f} hours")
                    st.write(f"- Fuel: {leg['fuel_needed']:.1f} {leg['fuel_unit']}")
            
            # Fuel stops
            if result.get("fuel_plan"):
                st.subheader("Fuel Stops")
                for i, stop in enumerate(result["fuel_plan"]):
                    st.write(f"**Stop {i+1}**: {stop['port']}")
                    st.write(f"- Amount: {stop['amount_tons_or_liters']:.1f}")
                    st.write(f"- Price/unit: ${stop['price_per_unit_usd']:.2f}")
                    st.write(f"- Cost: ${stop['cost_usd']:.2f}")
            
            # Raw JSON (collapsible)
            with st.expander("View Raw JSON"):
                st.json(result)
        else:
            st.error(f"Error from backend: {resp.status_code}")
            st.write(resp.text)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to backend at {BACKEND_URL}. Is it running?")
    except requests.exceptions.Timeout:
        st.error("Request timed out. Backend may be slow or unavailable.")
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.info("**How to run the backend**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`")
