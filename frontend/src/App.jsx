import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMapEvents } from "react-leaflet";
import axios from "axios";
import L from "leaflet";

const backendBase = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

function MapClickHandler({ onClick }) {
  useMapEvents({
    click(e) {
      onClick(e.latlng);
    }
  });
  return null;
}

export default function App() {
  const [ports, setPorts] = useState([]);
  const [carriers, setCarriers] = useState([]);
  const [selectedCarrierId, setSelectedCarrierId] = useState("");
  const [selectedMode, setSelectedMode] = useState("ocean");
  const [cargoType, setCargoType] = useState("general");
  const [origin, setOrigin] = useState(null);
  const [destination, setDestination] = useState(null);
  const [plan, setPlan] = useState(null);
  const [refuelResult, setRefuelResult] = useState(null);
  const [mapCenter, setMapCenter] = useState([20, 0]);

  useEffect(() => {
    axios.get(`${backendBase}/ports`).then(r => { setPorts(r.data); if (r.data.length) setMapCenter([r.data[0].lat, r.data[0].lon]); }).catch(()=>{});
    axios.get(`${backendBase}/carriers`).then(r => setCarriers(r.data)).catch(()=>{});
  }, []);

  const onMapClick = (latlng) => {
    if (!origin) {
      setOrigin({ lat: latlng.lat, lon: latlng.lng });
    } else if (!destination) {
      setDestination({ lat: latlng.lat, lon: latlng.lng });
    } else {
      // reset if both already chosen: set as origin
      setOrigin({ lat: latlng.lat, lon: latlng.lng });
      setDestination(null);
    }
  };

  const choosePortAsOrigin = (p) => {
    setOrigin({ lat: p.lat, lon: p.lon });
  };
  const choosePortAsDest = (p) => {
    setDestination({ lat: p.lat, lon: p.lon });
  };

  const runPlan = async () => {
    if (!origin || !destination) {
      alert("Pick origin and destination (click map or choose port).");
      return;
    }
    const payload = {
      transport_medium: selectedMode,
      cargo_type: cargoType,
      cargo_quantity: 100,
      unit: "tons",
      carrier_model: selectedCarrierId || undefined,
      origin: origin,
      destinations: [{ coord: destination, mode: selectedMode }],
      preferences: "cheapest"
    };
    const r = await axios.post(`${backendBase}/plan`, payload);
    setPlan(r.data);
    // center map on first leg
    setMapCenter([origin.lat, origin.lon]);
  };

  const runRefuel = async () => {
    if (!origin || !destination) {
      alert("Pick origin and destination first.");
      return;
    }
    if (!selectedCarrierId) {
      alert("Select a carrier model for the mode.");
      return;
    }
    const payload = {
      mode: selectedMode,
      carrier_model: selectedCarrierId,
      origin: origin,
      destination: destination,
      step_size: selectedMode === "ocean" ? 1.0 : 50.0,
      reserve: 0.1
    };
    const r = await axios.post(`${backendBase}/refuel-plan`, payload);
    setRefuelResult(r.data);
  };

  const center = mapCenter;

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ width: "360px", padding: 16, boxSizing: "border-box", background: "#f7f7f7", overflowY: "auto" }}>
        <h3>Interactive Logistics Planner</h3>

        <label>Mode</label>
        <select value={selectedMode} onChange={(e) => setSelectedMode(e.target.value)}>
          <option value="ocean">Ocean</option>
          <option value="air">Air</option>
          <option value="road">Road</option>
          <option value="rail">Rail</option>
        </select>

        <label style={{display:'block', marginTop:8}}>Carrier model</label>
        <select value={selectedCarrierId} onChange={(e) => setSelectedCarrierId(e.target.value)}>
          <option value="">(auto)</option>
          {carriers.filter(c => c.type === selectedMode).map(c => <option key={c.id} value={c.id}>{c.id} — {c.type}</option>)}
        </select>

        <label style={{display:'block', marginTop:8}}>Cargo type</label>
        <select value={cargoType} onChange={(e) => setCargoType(e.target.value)}>
          <option value="general">General</option>
          <option value="hazardous">Hazardous</option>
          <option value="perishable">Perishable</option>
          <option value="bulk">Bulk</option>
        </select>

        <div style={{marginTop:8}}>
          <strong>Origin:</strong><br/>
          {origin ? <span>{origin.lat.toFixed(4)}, {origin.lon.toFixed(4)}</span> : <span>click map or choose port</span>}
          <div style={{marginTop:4}}>
            <button onClick={()=>{ setOrigin(null); setDestination(null); }}>Reset picks</button>
          </div>
        </div>

        <div style={{marginTop:8}}>
          <strong>Destination:</strong><br/>
          {destination ? <span>{destination.lat.toFixed(4)}, {destination.lon.toFixed(4)}</span> : <span>click map or choose port</span>}
        </div>

        <div style={{marginTop:12}}>
          <button onClick={runPlan}>Compute Plan (multi-leg)</button>
          <button style={{marginLeft:8}} onClick={runRefuel}>Compute Optimal Refuel for Leg</button>
        </div>

        <h4 style={{marginTop:12}}>Seeded Ports (click to set)</h4>
        <div style={{maxHeight:200, overflowY:'auto'}}>
          <ul>
            {ports.map(p => (
              <li key={p.id} style={{marginBottom:6}}>
                <strong>{p.name}</strong><br/>
                <button onClick={() => choosePortAsOrigin(p)}>Use as Origin</button>
                <button style={{marginLeft:6}} onClick={() => choosePortAsDest(p)}>Use as Destination</button>
              </li>
            ))}
          </ul>
        </div>

        {plan && (
          <>
            <h4>Plan Summary</h4>
            <div>Route ID: {plan.route_id}</div>
            <div>Total distance (km): {plan.total_distance_km}</div>
            <div>Total cost (USD): {plan.total_cost_usd}</div>
            <div>Total fuel: {plan.total_fuel} {plan.total_fuel_unit}</div>

            <h5>Fuel Plan</h5>
            <ul>
              {plan.fuel_plan.map((s, i) => <li key={i}>{s.port} — {s.amount_tons_or_liters} @ ${s.price_per_unit_usd}/unit (${s.cost_usd})</li>)}
            </ul>
          </>
        )}

        {refuelResult && (
          <>
            <h4>Refuel Optimizer Result</h4>
            {refuelResult.error ? <div style={{color:'red'}}>{refuelResult.error}</div> : (
              <>
                <div>Total cost: ${refuelResult.total_cost}</div>
                <h5>Fuel actions</h5>
                <ul>
                  {refuelResult.fuel_plan.map((s, i) => (
                    <li key={i}>{s.node} — +{s.added_amount} @ ${s.price_per_unit} (cost ${s.cost})</li>
                  ))}
                </ul>
                <h5>Legs</h5>
                <ul>
                  {refuelResult.legs.map((l, i) => <li key={i}>{l.from} → {l.to} — {l.distance_nm} nm — {l.fuel_used} units</li>)}
                </ul>
              </>
            )}
          </>
        )}
      </div>

      <div style={{ flex: 1 }}>
        <MapContainer center={center} zoom={3} style={{ height: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <MapClickHandler onClick={onMapClick} />
          {ports.map(p => <Marker key={p.id} position={[p.lat, p.lon]}>
            <Popup>{p.name}<br/>${p.bunker_price}/t</Popup>
          </Marker>)}
          {origin && <Marker position={[origin.lat, origin.lon]}><Popup>Origin</Popup></Marker>}
          {destination && <Marker position={[destination.lat, destination.lon]}><Popup>Destination</Popup></Marker>}
          {plan && plan.leg_details && plan.leg_details.map((ld, i) => (
            <Polyline key={i} positions={[[ld.from_coord.lat, ld.from_coord.lon], [ld.to_coord.lat, ld.to_coord.lon]]} color="blue" />
          ))}
          {refuelResult && refuelResult.fuel_plan && refuelResult.fuel_plan.map((f, i) => {
            // best-effort find node coordinates from ports list
            const nodeName = f.node;
            const found = ports.find(p => p.name === nodeName);
            if (found) return <Marker key={"refuel-"+i} position={[found.lat, found.lon]}><Popup>{f.node}: +{f.added_amount}</Popup></Marker>;
            return null;
          })}
        </MapContainer>
      </div>
    </div>
  );
}