Updates summary
- Multi-modal support added (ocean, air, road, rail).
- Carriers library expanded (data/carriers.json) with representative models per medium.
- Optimizer extended to compute per-mode distances, fuel, time, simple refueling estimates and costs.
- New endpoint /carriers to list available carrier models.
- Frontend updated to let you choose transport mode and carrier model and visualize multi-modal legs.

Limitations / Next work
- Refueling / stop selection is approximate for road/air/rail; for world-scale accuracy integrate airport / gas station / railyard data and costs.
- For ocean routing we still use nearest ports DB; integrate full port list and AIS lane routing for higher fidelity.
- Fuel pricing is mocked. Replace services/fuel_service.py functions with real API connectors (Platts, ClearLynx, Barchart, Jet fuel suppliers).
- Add validation & more advanced multi-modal itinerary editing in the frontend.

Run
- Backend: docker-compose (if configured) or run uvicorn as before.
- Frontend: npm/yarn dev or build & serve as in previous instructions.

If you'd like, I can:
- Implement precise refuel-stop optimization using a state-space shortest-path (node, fuel) solver for each mode (optimal stops & costs).
- Import a full UN/LOCODE port list, IATA airport list, and an open stations dataset for road/rail to enable realistic stop selection.
- Replace mock fuel prices with live API connectors (please provide API credentials or choose providers).