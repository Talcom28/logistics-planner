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
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);

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
      alert("Please select both a starting point and destination on the map.");
      return;
    }
    setLoading(true);
    try {
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
      setRefuelResult(null);
      // center map on first leg
      setMapCenter([origin.lat, origin.lon]);
    } catch (error) {
      alert("Error calculating route. Please try again.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const runRefuel = async () => {
    if (!origin || !destination) {
      alert("Please select both a starting point and destination first.");
      return;
    }
    if (!selectedCarrierId) {
      alert("Please select a specific vehicle model for detailed fuel planning.");
      return;
    }
    setLoading(true);
    try {
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
      setPlan(null);
    } catch (error) {
      alert("Error calculating fuel stops. Please try again.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const center = mapCenter;

  const styles = {
    container: { display: "flex", height: "100vh", fontFamily: "system-ui, -apple-system, sans-serif" },
    sidebar: { 
      width: "380px", 
      padding: "24px", 
      boxSizing: "border-box", 
      background: "linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%)", 
      overflowY: "auto",
      boxShadow: "2px 0 8px rgba(0,0,0,0.1)"
    },
    header: { 
      fontSize: "24px", 
      fontWeight: "700", 
      marginBottom: "24px", 
      color: "#1a1a1a",
      borderBottom: "3px solid #0066cc",
      paddingBottom: "12px"
    },
    section: { 
      background: "white", 
      padding: "16px", 
      borderRadius: "8px", 
      marginBottom: "16px",
      boxShadow: "0 2px 4px rgba(0,0,0,0.08)"
    },
    sectionTitle: { 
      fontSize: "14px", 
      fontWeight: "600", 
      marginBottom: "12px", 
      color: "#495057",
      textTransform: "uppercase",
      letterSpacing: "0.5px"
    },
    label: { 
      display: "block", 
      fontSize: "13px", 
      fontWeight: "500", 
      marginBottom: "6px", 
      color: "#495057" 
    },
    select: { 
      width: "100%", 
      padding: "10px", 
      fontSize: "14px", 
      border: "1px solid #ced4da", 
      borderRadius: "6px",
      marginBottom: "12px",
      background: "white",
      cursor: "pointer"
    },
    button: { 
      width: "100%", 
      padding: "12px", 
      fontSize: "15px", 
      fontWeight: "600",
      border: "none", 
      borderRadius: "6px", 
      cursor: "pointer",
      transition: "all 0.2s",
      marginBottom: "8px"
    },
    primaryButton: {
      background: "#0066cc",
      color: "white"
    },
    secondaryButton: {
      background: "#6c757d",
      color: "white"
    },
    successButton: {
      background: "#28a745",
      color: "white"
    },
    locationBadge: {
      background: "#e7f3ff",
      padding: "12px",
      borderRadius: "6px",
      fontSize: "13px",
      marginBottom: "8px",
      border: "1px solid #b3d9ff"
    },
    resultCard: {
      background: "#f0f8ff",
      padding: "16px",
      borderRadius: "8px",
      border: "2px solid #0066cc"
    },
    resultTitle: {
      fontSize: "16px",
      fontWeight: "700",
      marginBottom: "12px",
      color: "#0066cc"
    },
    resultItem: {
      padding: "8px 0",
      borderBottom: "1px solid #d1e7ff",
      fontSize: "14px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center"
    },
    resultLabel: {
      fontWeight: "600",
      color: "#495057"
    },
    resultValue: {
      color: "#1a1a1a"
    },
    toggleLink: {
      color: "#0066cc",
      cursor: "pointer",
      fontSize: "13px",
      textDecoration: "underline",
      marginTop: "8px",
      display: "inline-block"
    },
    portList: {
      maxHeight: "200px",
      overflowY: "auto",
      padding: "0",
      margin: "0"
    },
    portItem: {
      background: "white",
      padding: "10px",
      marginBottom: "8px",
      borderRadius: "6px",
      border: "1px solid #dee2e6"
    },
    portName: {
      fontWeight: "600",
      fontSize: "14px",
      marginBottom: "6px",
      color: "#1a1a1a"
    },
    smallButton: {
      padding: "6px 12px",
      fontSize: "12px",
      border: "none",
      borderRadius: "4px",
      background: "#0066cc",
      color: "white",
      cursor: "pointer",
      marginRight: "6px"
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.header}>
          📦 Logistics Planner
        </div>

        {/* Transport Mode Selection */}
        <div style={styles.section}>
          <div style={styles.sectionTitle}>🚚 Transport Method</div>
          <label style={styles.label}>How do you want to ship?</label>
          <select 
            value={selectedMode} 
            onChange={(e) => setSelectedMode(e.target.value)}
            style={styles.select}
          >
            <option value="ocean">🚢 Ocean Shipping</option>
            <option value="air">✈️ Air Freight</option>
            <option value="road">🚛 Road Transport</option>
            <option value="rail">🚂 Rail Transport</option>
          </select>

          {/* Advanced Options Toggle */}
          <button onClick={() => setShowAdvanced(!showAdvanced)} style={{...styles.toggleLink, border: 'none', background: 'none', padding: 0}}>
            {showAdvanced ? "▼ Hide" : "▶ Show"} Advanced Options
          </button>

          {showAdvanced && (
            <>
              <label style={{...styles.label, marginTop: "12px"}}>Vehicle Model (Optional)</label>
              <select 
                value={selectedCarrierId} 
                onChange={(e) => setSelectedCarrierId(e.target.value)}
                style={styles.select}
              >
                <option value="">(Automatic Selection)</option>
                {carriers.filter(c => c.type === selectedMode).map(c => 
                  <option key={c.id} value={c.id}>{c.id}</option>
                )}
              </select>

              <label style={styles.label}>Cargo Type</label>
              <select 
                value={cargoType} 
                onChange={(e) => setCargoType(e.target.value)}
                style={styles.select}
              >
                <option value="general">General Cargo</option>
                <option value="hazardous">Hazardous Materials</option>
                <option value="perishable">Perishable Goods</option>
                <option value="bulk">Bulk Cargo</option>
              </select>
            </>
          )}
        </div>

        {/* Location Selection */}
        <div style={styles.section}>
          <div style={styles.sectionTitle}>📍 Select Locations</div>
          <p style={{fontSize: "13px", color: "#6c757d", marginBottom: "12px"}}>
            Click on the map or choose from ports below
          </p>

          <div style={styles.locationBadge}>
            <strong>From:</strong><br/>
            {origin ? 
              <span style={{fontSize: "12px"}}>{origin.lat.toFixed(2)}°, {origin.lon.toFixed(2)}°</span> : 
              <span style={{color: "#6c757d"}}>Click map to select</span>
            }
          </div>

          <div style={styles.locationBadge}>
            <strong>To:</strong><br/>
            {destination ? 
              <span style={{fontSize: "12px"}}>{destination.lat.toFixed(2)}°, {destination.lon.toFixed(2)}°</span> : 
              <span style={{color: "#6c757d"}}>Click map to select</span>
            }
          </div>

          {(origin || destination) && (
            <button 
              onClick={() => { setOrigin(null); setDestination(null); setPlan(null); setRefuelResult(null); }}
              style={{...styles.button, ...styles.secondaryButton, fontSize: "13px", padding: "8px"}}
            >
              Clear Selections
            </button>
          )}
        </div>

        {/* Action Buttons */}
        <div style={styles.section}>
          <div style={styles.sectionTitle}>⚡ Calculate Route</div>
          <button 
            onClick={runPlan}
            disabled={loading || !origin || !destination}
            style={{
              ...styles.button, 
              ...styles.primaryButton,
              opacity: (loading || !origin || !destination) ? 0.5 : 1
            }}
          >
            {loading ? "Calculating..." : "Calculate Best Route"}
          </button>

          {showAdvanced && (
            <button 
              onClick={runRefuel}
              disabled={loading || !origin || !destination || !selectedCarrierId}
              style={{
                ...styles.button, 
                ...styles.successButton,
                opacity: (loading || !origin || !destination || !selectedCarrierId) ? 0.5 : 1
              }}
            >
              {loading ? "Calculating..." : "Optimize Fuel Stops"}
            </button>
          )}
        </div>

        {/* Available Ports */}
        {ports.length > 0 && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>🏖️ Quick Select Ports</div>
            <div style={styles.portList}>
              {ports.map(p => (
                <div key={p.id} style={styles.portItem}>
                  <div style={styles.portName}>{p.name}</div>
                  <button onClick={() => choosePortAsOrigin(p)} style={styles.smallButton}>
                    Set as From
                  </button>
                  <button onClick={() => choosePortAsDest(p)} style={styles.smallButton}>
                    Set as To
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results Display */}
        {plan && (
          <div style={{...styles.section, ...styles.resultCard}}>
            <div style={styles.resultTitle}>✅ Route Summary</div>
            
            <div style={styles.resultItem}>
              <span style={styles.resultLabel}>Distance:</span>
              <span style={styles.resultValue}>
                {plan.total_distance_km ? `${Math.round(plan.total_distance_km)} km` : 'N/A'}
              </span>
            </div>
            
            <div style={styles.resultItem}>
              <span style={styles.resultLabel}>Estimated Cost:</span>
              <span style={styles.resultValue}>
                ${plan.total_cost_usd ? Math.round(plan.total_cost_usd).toLocaleString() : 'N/A'}
              </span>
            </div>
            
            <div style={styles.resultItem}>
              <span style={styles.resultLabel}>Fuel Required:</span>
              <span style={styles.resultValue}>
                {plan.total_fuel ? `${Math.round(plan.total_fuel)} ${plan.total_fuel_unit || 'units'}` : 'N/A'}
              </span>
            </div>

            {plan.fuel_plan && plan.fuel_plan.length > 0 && (
              <>
                <div style={{...styles.sectionTitle, marginTop: "16px", marginBottom: "8px"}}>
                  ⛽ Fuel Stops
                </div>
                {plan.fuel_plan.map((s, i) => (
                  <div key={i} style={{fontSize: "13px", padding: "6px 0", borderBottom: "1px solid #d1e7ff"}}>
                    <strong>{s.port}</strong>
                    <br/>
                    <span style={{color: "#6c757d"}}>
                      Amount: {Math.round(s.amount_tons_or_liters)} units • Cost: ${Math.round(s.cost_usd)}
                    </span>
                  </div>
                ))}
              </>
            )}
          </div>
        )}

        {refuelResult && !refuelResult.error && (
          <div style={{...styles.section, ...styles.resultCard}}>
            <div style={styles.resultTitle}>⛽ Optimized Fuel Plan</div>
            
            <div style={styles.resultItem}>
              <span style={styles.resultLabel}>Total Fuel Cost:</span>
              <span style={styles.resultValue}>
                ${refuelResult.total_cost ? Math.round(refuelResult.total_cost).toLocaleString() : 'N/A'}
              </span>
            </div>

            {refuelResult.fuel_plan && refuelResult.fuel_plan.length > 0 && (
              <>
                <div style={{...styles.sectionTitle, marginTop: "16px", marginBottom: "8px"}}>
                  Refuel Stops
                </div>
                {refuelResult.fuel_plan.map((s, i) => (
                  <div key={i} style={{fontSize: "13px", padding: "6px 0", borderBottom: "1px solid #d1e7ff"}}>
                    <strong>{s.node}</strong>
                    <br/>
                    <span style={{color: "#6c757d"}}>
                      Add: {Math.round(s.added_amount)} units • Cost: ${Math.round(s.cost)}
                    </span>
                  </div>
                ))}
              </>
            )}
          </div>
        )}

        {refuelResult && refuelResult.error && (
          <div style={{...styles.section, background: "#fff3cd", border: "2px solid #ffc107"}}>
            <div style={{color: "#856404", fontSize: "14px"}}>
              ⚠️ {refuelResult.error}
            </div>
          </div>
        )}
      </div>

      <div style={{ flex: 1 }}>
        <MapContainer center={center} zoom={3} style={{ height: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <MapClickHandler onClick={onMapClick} />
          {ports.map(p => <Marker key={p.id} position={[p.lat, p.lon]}>
            <Popup>
              <strong>{p.name}</strong><br/>
              Fuel: ${p.bunker_price}/unit
            </Popup>
          </Marker>)}
          {origin && (
            <Marker position={[origin.lat, origin.lon]}>
              <Popup><strong>From</strong></Popup>
            </Marker>
          )}
          {destination && (
            <Marker position={[destination.lat, destination.lon]}>
              <Popup><strong>To</strong></Popup>
            </Marker>
          )}
          {plan && plan.leg_details && plan.leg_details.map((ld, i) => {
            const legPositions = [
              [ld.from_coord.lat, ld.from_coord.lon],
              [ld.to_coord.lat, ld.to_coord.lon]
            ];
            return (
              <Polyline 
                key={i} 
                positions={legPositions} 
                color="#0066cc" 
                weight={3} 
              />
            );
          })}
          {refuelResult && refuelResult.fuel_plan && refuelResult.fuel_plan.map((f, i) => {
            const nodeName = f.node;
            const found = ports.find(p => p.name === nodeName);
            if (found) return <Marker key={"refuel-"+i} position={[found.lat, found.lon]}>
              <Popup><strong>Fuel Stop</strong><br/>{f.node}<br/>+{Math.round(f.added_amount)} units</Popup>
            </Marker>;
            return null;
          })}
        </MapContainer>
      </div>
    </div>
  );
}