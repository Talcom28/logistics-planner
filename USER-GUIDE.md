# Logistics Route Planner - User Guide

## What This Software Does

This is a logistics planning tool that helps you find the best routes for shipping cargo. It can plan routes across:
- **Ocean shipping** (cargo ships between ports)
- **Air freight** (planes between airports)
- **Road transport** (trucks between stations)
- **Rail transport** (trains between stations)
- **Combined routes** (using multiple types of transport)

The software calculates the cheapest or fastest route, figures out where to refuel, and tells you the total cost and time.

---

## What You Need Before Starting

### For Online Use (Simplest)
- **Web browser** (Chrome, Firefox, Edge, Safari)
- **Internet connection**
- **The website address** provided by your administrator

### For Running Your Own Copy
1. **A computer** running Windows, Mac, or Linux
2. **Python software** (version 3.11 or newer) - free download from python.org
3. **A database** to store port and airport information (PostgreSQL - can be hosted online for free)
4. **Optional: Docker** - makes installation easier by packaging everything together

---

## How to Access the Software

### Option 1: Use the Hosted Version (Easiest)
If your organization has already deployed this software:

1. Open your web browser
2. Go to the website address (URL) provided by your IT team
3. Add `/docs` to the end of the URL
4. You'll see an interactive page where you can:
   - Enter origin and destination locations
   - Choose transport type (ocean, air, road, rail)
   - Specify cargo details
   - Get route plans with costs and refueling stops

**Example:** If your URL is `https://logistics-planner.railway.app`, visit `https://logistics-planner.railway.app/docs`

### Option 2: Interactive Dashboard
Some setups include a visual dashboard:

1. Your IT team will provide a Streamlit URL
2. Open it in your browser
3. Use the sidebar to enter:
   - Starting point (latitude and longitude)
   - Destination point
   - Cargo type and weight
   - Transport method
4. Click "Plan Route" to see results with maps and charts

---

## Understanding the Results

When you request a route plan, you'll receive:

### Basic Information
- **Total Distance** - how far the cargo travels (in nautical miles or kilometers)
- **Total Time** - how long the journey takes (in hours or days)
- **Total Cost** - complete shipping cost in US dollars

### Route Details
- **Legs** - each segment of the journey (origin to port, port to port, etc.)
- **Mode** - type of transport for each leg (ocean, air, road, rail)
- **Fuel Needed** - amount of fuel for each leg

### Refueling Stops
If the journey requires refueling:
- **Location** - which port or station to refuel at
- **Amount** - how much fuel to purchase
- **Price** - cost per unit of fuel
- **Stop Fee** - additional charges for using the facility

---

## Common Tasks

### Planning a Simple Ocean Route
1. Enter your starting port coordinates
2. Enter your destination port coordinates
3. Specify cargo weight (in tons)
4. Select "ocean" as transport type
5. Submit the request
6. Review the suggested route, refueling stops, and total cost

### Planning a Multi-Modal Route
1. Start with origin coordinates
2. Add multiple destination points
3. For each destination, specify the transport mode
4. The software will calculate the best combination
5. You'll get separate cost breakdowns for each leg

### Comparing Carriers
1. Request a route plan with one carrier model
2. Note the total cost and time
3. Request the same route with a different carrier
4. Compare results to choose the most economical option

---

## What Information You Need to Provide

### Required Information
- **Origin location** - starting point (latitude and longitude coordinates)
- **Destination location** - end point (coordinates)
- **Cargo details**:
  - Type (general, hazardous, refrigerated, etc.)
  - Quantity/weight
  - Unit (tons, kilograms, etc.)
- **Transport preference** - ocean, air, road, rail, or automatic

### Optional Information
- **Specific carrier model** - if you have a preferred ship/plane/truck type
- **Priority** - cheapest route vs. fastest route
- **Special requirements** - refrigeration, hazmat handling, etc.

### Finding Coordinates
If you don't know the latitude and longitude:
- Use Google Maps: right-click a location and select the coordinates
- Major ports and airports have published coordinates online
- Your administrator can provide a list of common locations

---

## Troubleshooting

### "No route found"
- Check that your coordinates are correct (latitude: -90 to 90, longitude: -180 to 180)
- Verify that ports/airports exist near your locations
- Try increasing the search range in settings

### "Insufficient fuel capacity"
- The distance is too far for the selected carrier without refueling
- The software will suggest intermediate refueling stops
- Consider a carrier with larger fuel capacity

### "Database connection error"
- Contact your IT administrator
- The backend server may be down for maintenance
- Check your internet connection

### Results seem inaccurate
- Fuel prices may be outdated (administrators can update these)
- Port fees are estimates (actual fees may vary)
- Weather and traffic delays are not included in time estimates

---

## Data Management

### Ports and Stations
The database includes:
- **Ports** - seaports with bunkering facilities
- **Airports** - with refueling capabilities
- **Stations** - truck stops and rail terminals

Administrators can:
- Import new locations from CSV files
- Update fuel prices
- Add or remove facilities
- Set custom fees

### Carrier Models
Pre-loaded carrier types include:
- **Ocean**: Various ship sizes (Panamax, Capesize, container ships)
- **Air**: Cargo planes (Boeing 747F, Airbus A330F, etc.)
- **Road**: Truck configurations
- **Rail**: Train types

Custom carrier models can be added by editing the carrier configuration file.

---

## Support and Training

### Getting Help
- Contact your IT administrator for technical issues
- Refer to this guide for usage questions
- Check the `/docs` page for API documentation

### Training Resources
- Video tutorials (if provided by your organization)
- Sample route planning exercises
- User forums or internal chat channels

### Providing Feedback
- Report bugs or issues to your IT team
- Suggest new features or improvements
- Share successful use cases with your organization

---

## Security and Privacy

### Data Handling
- Route requests are processed in real-time
- No route plans are permanently stored unless you save them
- Coordinate data is not shared externally

### Access Control
- Some installations require login credentials
- Contact your administrator for account setup
- Keep your login information confidential

---

## Glossary

**Bunker/Bunkering** - Refueling a ship with marine fuel

**Cargo Quantity** - Weight or volume of goods being shipped

**Carrier Model** - Specific type of ship, plane, truck, or train with defined capacity and fuel consumption

**Coordinates** - Latitude and longitude numbers that specify a location on Earth

**Leg** - One segment of a multi-segment journey

**Multi-modal** - Using more than one type of transport (e.g., ship + truck)

**Nautical Mile (NM)** - Distance measurement used in shipping and aviation (1.852 km)

**Port Fee** - Charge for using a port's facilities

**Route Optimization** - Finding the most cost-effective or time-efficient path

**UNLOCODE** - UN/LOCODE is a geographic coding system for ports and other locations

---

## Quick Reference

**To plan a basic route:**
1. Open the web interface
2. Enter start and end coordinates
3. Choose transport type
4. Enter cargo weight
5. Click "Plan" or "Submit"

**To view all available ports:**
- Visit `/ports` endpoint
- Or check the ports list in your dashboard

**To see carrier options:**
- Visit `/carriers` endpoint
- Or review the dropdown menu in your interface

**To get help:**
- Contact your IT administrator
- Check this user guide
- Visit the `/docs` page for technical details

---

*Last updated: December 2025*
