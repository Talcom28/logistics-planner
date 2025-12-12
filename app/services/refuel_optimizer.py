"""
State-space (node, fuel) shortest-path solver for optimal refuelling.

This module provides a generic refuel optimizer that can be used for ocean/air/road/rail.
It discretizes fuel into steps and runs Dijkstra (best-first) over states:
    state = (node_id, fuel_level_index)

Transitions:
- Refuel at node: increase fuel level (pay price * added_amount + service/port fee once)
- Travel to neighbor node: if fuel >= fuel_needed, move with reduced fuel and cost 0 (fuel cost was paid when bunkered)

Notes / assumptions (MVP):
- Nodes must be pre-populated in DB: ports (for ocean), airports (for air), stations (for road/rail).
- Each node should expose a price per fuel unit (tons or liters) and a stop fee (port_fee, landing_fee, service_fee).
- Fuel discretization step is configurable (e.g., 1 ton or 100 liters); smaller step => more precise but slower.
- The solver assumes refuelling can be done up to full capacity at nodes.
- This returns cheapest plan given fuel prices and stop fees, with an optional limit on number of stops or time.

API:
    find_optimal_refuel_route(db, nodes, origin_coord, dest_coord, carrier_profile, mode,
                              fuel_unit='tons'|'liters', step_size=1.0, reserve=0.1)

Returns:
    dict with keys: total_cost, fuel_plan (list of {node, amount, price, cost}), path (node id list),
                    legs (list of dict with distance, fuel_used, etc.)
"""
from heapq import heappush, heappop
from collections import defaultdict, namedtuple
from math import ceil
from typing import List, Tuple, Dict, Any
from app.services.utils import haversine_nm_coords, haversine_km
from app.db import SessionLocal
from app.models_orm import Port, Airport, Station
from geoalchemy2.shape import to_shape

State = namedtuple("State", ["cost", "node_idx", "fuel_idx", "prev"])
Transition = namedtuple("Transition", ["to_node", "fuel_cost", "travel_fuel", "distance_nm", "time_hours"])

INF = float("inf")


def _load_nodes_for_mode(db, mode: str) -> List[Dict[str, Any]]:
    nodes = []
    if mode == "ocean":
        rows = db.query(Port).all()
        for r in rows:
            shp = to_shape(r.geom)
            nodes.append({
                "id": f"port:{r.id}",
                "type": "port",
                "obj_id": r.id,
                "name": r.name,
                "lat": shp.y,
                "lon": shp.x,
                "price_per_unit": float(r.bunker_price or 1e9),  # USD per ton
                "stop_fee": float(r.port_fee or 0.0),
            })
    elif mode == "air":
        rows = db.query(Airport).all()
        for r in rows:
            shp = to_shape(r.geom)
            nodes.append({
                "id": f"airport:{r.id}",
                "type": "airport",
                "obj_id": r.id,
                "name": r.name,
                "lat": shp.y,
                "lon": shp.x,
                "price_per_unit": float(r.jet_price_per_l or 1e9),  # USD per liter
                "stop_fee": float(r.landing_fee or 0.0),
            })
    elif mode in ("road", "rail"):
        rows = db.query(Station).all()
        for r in rows:
            shp = to_shape(r.geom)
            nodes.append({
                "id": f"station:{r.id}",
                "type": "station",
                "obj_id": r.id,
                "name": r.name or f"station:{r.id}",
                "lat": shp.y,
                "lon": shp.x,
                "price_per_unit": float(r.diesel_price_per_l or 1e9),  # USD per liter
                "stop_fee": float(r.service_fee or 0.0),
            })
    else:
        raise ValueError("Unsupported mode for node loading: " + str(mode))
    return nodes


def _nearest_node_index(nodes: List[Dict[str, Any]], lat: float, lon: float) -> int:
    best = None
    best_d = float("inf")
    for i, n in enumerate(nodes):
        d = haversine_km(lat, lon, n["lat"], n["lon"])
        if d < best_d:
            best_d = d
            best = i
    return best


def find_optimal_refuel_route(origin_coord: Tuple[float, float],
                              dest_coord: Tuple[float, float],
                              carrier_profile: Dict[str, Any],
                              mode: str,
                              fuel_unit: str,
                              step_size: float = 1.0,
                              reserve: float = 0.1,
                              max_nodes_considered: int = 200) -> Dict[str, Any]:
    """
    origin_coord/dest_coord: (lat, lon)
    carrier_profile: contains fuel_capacity (tons or liters) and consumption per distance:
        for ocean: consumption_tons_per_nm
        for road/rail: consumption_l_per_km or consumption_l_per_100km
        for air: consumption_kg_per_hr + conversion to liters handled outside or provide consumption_l_per_km
    fuel_unit: 'tons' or 'liters'
    step_size: in same unit as fuel_unit (e.g., 1 ton or 100 liters)
    """
    db = next(SessionLocal())

    nodes = _load_nodes_for_mode(db, mode)

    # Add origin and destination as virtual nodes (no price unless nearest node used to bunker)
    nodes.insert(0, {
        "id": "origin",
        "type": "origin",
        "obj_id": None,
        "name": "Origin",
        "lat": origin_coord[0],
        "lon": origin_coord[1],
        "price_per_unit": None,
        "stop_fee": 0.0
    })
    nodes.append({
        "id": "destination",
        "type": "destination",
        "obj_id": None,
        "name": "Destination",
        "lat": dest_coord[0],
        "lon": dest_coord[1],
        "price_per_unit": None,
        "stop_fee": 0.0
    })

    # limit nodes considered to keep runtime reasonable
    if len(nodes) > max_nodes_considered:
        nodes = nodes[:max_nodes_considered]

    N = len(nodes)
    origin_idx = 0
    dest_idx = N - 1

    # consumption by distance: we will use fuel_needed = consumption_rate * distance (in appropriate units)
    if mode == "ocean":
        consumption_per_nm = carrier_profile.get("consumption_tons_per_nm")
        capacity = carrier_profile.get("fuel_capacity_tons")
        # fuel unit must be 'tons'
    elif mode == "air":
        # expect carrier_profile to optionally provide consumption_l_per_km (preferred)
        consumption_per_km = carrier_profile.get("consumption_l_per_km")
        if consumption_per_km is None:
            # fallback compute from kg/hr and cruise speed (approx)
            kg_hr = carrier_profile.get("consumption_kg_per_hr")
            speed_kmh = carrier_profile.get("cruise_speed_kmh", 800.0)
            # kg to liters ~ /0.8
            consumption_per_km = (kg_hr / speed_kmh) / 0.8
        capacity = carrier_profile.get("fuel_capacity_l")
    elif mode in ("road", "rail"):
        # consumption in liters per km (or per 100 km)
        if "consumption_l_per_km" in carrier_profile:
            consumption_per_km = carrier_profile["consumption_l_per_km"]
        elif "consumption_l_per_100km" in carrier_profile:
            consumption_per_km = carrier_profile["consumption_l_per_100km"] / 100.0
        else:
            raise ValueError("Carrier profile missing consumption for road/rail")
        capacity = carrier_profile.get("fuel_capacity_l")
    else:
        raise ValueError("Unsupported mode: " + str(mode))

    # discretize fuel levels: indices 0..M corresponding to amount = idx * step_size
    max_steps = int(ceil(capacity / step_size))
    # require reserve
    reserve_amount = reserve * capacity

    # Build adjacency matrix with travel fuel required and distance/time
    edges = [[] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            a = nodes[i]
            b = nodes[j]
            # compute distance in appropriate units
            if mode == "ocean":
                d_nm = haversine_nm_coords(a["lat"], a["lon"], b["lat"], b["lon"])
                fuel_needed = d_nm * consumption_per_nm
                time_hours = d_nm / carrier_profile.get("service_speed_knots", 14.0)
                edges[i].append(Transition(to_node=j, fuel_cost=0.0, travel_fuel=fuel_needed, distance_nm=d_nm, time_hours=time_hours))
            else:
                # road/rail/air use km
                d_km = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
                fuel_needed = d_km * consumption_per_km
                # time heuristics
                if mode == "air":
                    speed = carrier_profile.get("cruise_speed_kmh", 800.0)
                elif mode == "road":
                    speed = 70.0
                else:
                    speed = 40.0
                time_hours = d_km / speed
                edges[i].append(Transition(to_node=j, fuel_cost=0.0, travel_fuel=fuel_needed, distance_nm=d_km / 1.852, time_hours=time_hours))

    # Dijkstra over (node, fuel_idx)
    # cost[state] = total USD cost incurred so far (bunkering payments + stop fees)
    # when we 'travel' fuel is consumed but cost doesn't increment (we assume fuel was paid when bunkered)
    start_fuel_idx = int(ceil(capacity / step_size))  # we allow starting fully bunkered
    start_state = (origin_idx, start_fuel_idx)
    pq = []
    # (cost, node_idx, fuel_idx, prev_node, prev_fuel_idx, action)
    heappush(pq, (0.0, origin_idx, start_fuel_idx, None, None, "start"))
    dist = defaultdict(lambda: INF)
    prev = dict()
    dist[(origin_idx, start_fuel_idx)] = 0.0

    target_state = None

    while pq:
        cost_u, u_node, u_fuel_idx, u_prev_node, u_prev_fuel_idx, action = heappop(pq)
        if cost_u > dist[(u_node, u_fuel_idx)]:
            continue
        # if we are at destination and have at least reserve fuel (or zero is acceptable), finish
        fuel_amount = u_fuel_idx * step_size
        if u_node == dest_idx and fuel_amount >= reserve_amount:
            target_state = (u_node, u_fuel_idx)
            break

        # Option 1: from node u, try to refuel to higher fuel levels (if node sells fuel)
        node_obj = nodes[u_node]
        price = node_obj.get("price_per_unit")
        stop_fee = node_obj.get("stop_fee", 0.0)
        # only allow refuel on nodes that have price (not origin/destination unless they have price)
        if price is not None and price < 1e8:
            # allow topping up to full capacity
            for new_idx in range(u_fuel_idx + 1, max_steps + 1):
                added_amount = (new_idx - u_fuel_idx) * step_size
                added_cost = added_amount * price
                # charge stop fee once when we first refuel at this node from a non-refuel state.
                # To avoid charging stop_fee repeatedly for incremental actions, we'll include stop_fee only
                # when the prev action was not a refuel at same node. For simplicity we add it the first time we refuel.
                # Here we look at prev state; since we don't track prev action in dist key, we'll conservatively add stop_fee.
                # This makes costs slightly pessimistic but safe.
                new_cost = cost_u + added_cost + stop_fee
                if new_cost < dist[(u_node, new_idx)]:
                    dist[(u_node, new_idx)] = new_cost
                    prev[(u_node, new_idx)] = (u_node, u_fuel_idx, "refuel", added_amount, price, stop_fee)
                    heappush(pq, (new_cost, u_node, new_idx, u_node, u_fuel_idx, "refuel"))

        # Option 2: travel to neighbors if enough fuel
        for trans in edges[u_node]:
            v = trans.to_node
            required_fuel = trans.travel_fuel
            required_idx = int(ceil(required_fuel / step_size))
            if u_fuel_idx >= required_idx:
                v_fuel_idx = u_fuel_idx - required_idx
                # arriving at v may incur an implicit stop fee later if refuelling; travel itself does not add cost
                new_cost = cost_u
                if new_cost < dist[(v, v_fuel_idx)]:
                    dist[(v, v_fuel_idx)] = new_cost
                    prev[(v, v_fuel_idx)] = (u_node, u_fuel_idx, "travel", trans.distance_nm, trans.time_hours, required_fuel)
                    heappush(pq, (new_cost, v, v_fuel_idx, u_node, u_fuel_idx, "travel"))

    if target_state is None:
        return {"error": "No feasible route found with given capacity/step/reserve."}

    # reconstruct path states
    path_states = []
    cur = target_state
    while cur in prev:
        rec = prev[cur]
        path_states.append((cur, rec))
        cur = (rec[0], rec[1])
    path_states = list(reversed(path_states))

    # Build human-friendly plan: nodes visited and refuel actions
    fuel_plan = []
    visited_nodes = []
    legs = []
    # start from origin full tank
    # Walk through path_states to collect refuel actions and travels
    cur_node = origin_idx
    cur_fuel = start_fuel_idx * step_size
    for state, rec in path_states:
        node_idx, fuel_idx = state
        action = rec[2]
        if action == "refuel":
            added_amount = rec[3]
            price = rec[4]
            stop_fee = rec[5]
            fuel_plan.append({
                "node": nodes[node_idx]["name"],
                "node_id": nodes[node_idx]["id"],
                "added_amount": round(added_amount, 3),
                "price_per_unit": float(price),
                "cost": round(added_amount * price + stop_fee, 2),
                "stop_fee": float(stop_fee)
            })
            cur_fuel += added_amount
        elif action == "travel":
            distance_nm = rec[3]
            time_hours = rec[4]
            used = rec[5]
            prev_node_idx = rec[0]
            legs.append({
                "from": nodes[prev_node_idx]["name"],
                "to": nodes[node_idx]["name"],
                "distance_nm": round(distance_nm, 2),
                "time_hours": round(time_hours, 2),
                "fuel_used": round(used, 3)
            })
            cur_fuel -= used
        cur_node = node_idx

    # compute total cost
    total_cost = 0.0
    for f in fuel_plan:
        total_cost += f["cost"]

    result = {
        "total_cost": round(total_cost, 2),
        "fuel_plan": fuel_plan,
        "legs": legs,
        "path_nodes": [nodes[origin_idx]["name"]] + [p["to"] for p in legs],
        "final_fuel_amount": cur_fuel
    }
    return result