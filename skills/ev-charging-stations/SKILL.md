---
name: ev-charging-stations
description: Retrieve electric vehicle charging stations in the USA. Query by location, fuel type, network, or charger level. Automatically handles pagination for large result sets.
---

# EV Charging Stations Skill

## Description

This skill retrieves locations and attributes of alternative fuel stations (primarily EV charging) in the United States and Canada by accessing the ArcGIS Feature Service at the following URL:

```
https://rhvpkkiftonktxq3.svcs9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/Alternate_Fuel/FeatureServer/0
```

**Service Details:**
- Maximum record count: 10000
- Total records: 115,000+ stations
- Spatial reference: WKID 102100 (Web Mercator)
- Coverage: USA + Canada provinces

The service returns the following key fields:

**Location Information:**
- **Station_Name**: Name of the charging station
- **Address**: Street address
- **City**: City name
- **State**: 2-letter state/province abbreviation (e.g., "CA", "NM", "TX", "BC", "ON")
- **Zipcode**: Postal ZIP code
- **Latitude**: Latitude coordinate (decimal degrees)
- **Longitude**: Longitude coordinate (decimal degrees)

**Fuel/Charging Type:**
- **Fuel_Type**: Fuel type code
  - `ELEC` - Electric vehicle charging
  - `CNG` - Compressed Natural Gas
  - `LNG` - Liquefied Natural Gas
  - `LPG` - Liquefied Petroleum Gas (Propane)
  - `E85` - Ethanol blend (85% ethanol)
  - `BD` - Biodiesel
  - `HY` - Hydrogen
  - `RD` - Renewable Diesel

**EV Charging Details:**
- **EV_Level1_EVSE_Ports**: Number of Level 1 EVSE ports (120V, standard outlet)
- **EV_Level2_EVSE_Ports**: Number of Level 2 EVSE ports (240V, faster charging)
- **EV_DC_Fast_Ports**: Number of DC Fast Charge ports (rapid charging)
- **EV_Connector_Types**: Connector types available (e.g., "J1772", "CHADEMO", "TESLA", "CCS")
- **EV_Network**: Charging network name (e.g., "ChargePoint Network", "Tesla", "Electrify America", "Non-Networked")
- **EV_Pricing**: Pricing information
- **EV_Network_Link**: URL to station on network website

**Access Information:**
- **Accessability**: Access type (e.g., "public", "private")
- **Access_Details**: Access restrictions details
- **Access_Hours**: Days/hours of access
- **Current_Status**: Operational status (e.g., "Currently Available", "Planned", "Temporarily Unavailable")
- **Ownership_Type**: Ownership type

**Contact & Updates:**
- **Phone_Number**: Station phone number
- **Date_Last_Confirmed**: Date last verified/updated
- **Open_Date**: Date station opened
- **Station_Id**: Unique station identifier

## When to Use

Use this skill to:

- Find EV charging stations by location (state, city)
- Find stations by charging level (Level 1, Level 2, DC Fast Charge)
- Query stations by network (ChargePoint, Tesla, Electrify America, etc.)
- Find publicly accessible charging stations
- Analyze EV charging infrastructure coverage
- Find stations with specific connector types
- Query alternative fuel stations (CNG, biodiesel, E85, hydrogen, etc.)

## How to Use

### Step 1: Import Required Libraries

```python
import requests
import pandas as pd
```

### Step 2: Define the Query Function

**CRITICAL**: This function automatically handles pagination to retrieve ALL results, even when more than 10000 records match your query.

**IMPORTANT**: Do NOT use geometry/bbox parameters in queries. The service uses Web Mercator projection which causes coordinate mismatches. Filter by State field instead.

```python
def get_charging_stations(where_clause):
    """
    Query the ArcGIS Feature Service for EV charging stations.

    AUTOMATICALLY HANDLES PAGINATION - retrieves all results even if >10000.

    Parameters:
    -----------
    where_clause : str
        SQL-like WHERE clause to filter features (e.g., "State = 'CA'")

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing ALL queried charging station features
    """
    url = "https://rhvpkkiftonktxq3.svcs9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/Alternate_Fuel/FeatureServer/0"

    all_features = []
    offset = 0
    batch_size = 10000

    while True:
        params = {
            "where": where_clause,
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": batch_size
        }

        response = requests.get(url + "/query", params=params)
        data = response.json()

        if not data.get('features'):
            break

        all_features.extend(data['features'])

        if len(data['features']) < batch_size:
            break

        offset += batch_size

    if all_features:
        return pd.DataFrame([f['attributes'] for f in all_features])
    else:
        return pd.DataFrame()
```

### Step 3: Query Examples

#### Example 1: Find EV Charging Stations by State

```python
# Query for EV charging stations in California
# State field uses 2-letter abbreviations
where_clause = "State = 'CA' AND Fuel_Type = 'ELEC'"
ca_stations = get_charging_stations(where_clause)

print(f"Found {len(ca_stations)} EV charging stations in California")
print(ca_stations[['Station_Name', 'City', 'EV_Level2_EVSE_Ports', 'EV_DC_Fast_Ports']].head())
```

#### Example 2: Find DC Fast Charging Stations

```python
# Query for stations with DC Fast Charging in New Mexico
where_clause = "State = 'NM' AND EV_DC_Fast_Ports > 0"
dc_fast_stations = get_charging_stations(where_clause)

print(f"Found {len(dc_fast_stations)} DC Fast Charging stations in New Mexico")
```

#### Example 3: Find Stations by Network

```python
# Find ChargePoint stations
where_clause = "EV_Network LIKE '%ChargePoint%'"
chargepoint_stations = get_charging_stations(where_clause)

print(f"Found {len(chargepoint_stations)} ChargePoint stations")
```

#### Example 4: Find Tesla Superchargers

```python
# Find Tesla charging stations
where_clause = "EV_Network LIKE '%Tesla%' OR Station_Name LIKE '%Tesla%'"
tesla_stations = get_charging_stations(where_clause)

print(f"Found {len(tesla_stations)} Tesla charging locations")
```

#### Example 5: Find Public Charging Stations

```python
# Find publicly accessible EV stations in Texas
where_clause = "State = 'TX' AND Fuel_Type = 'ELEC' AND Accessability = 'public'"
public_stations = get_charging_stations(where_clause)

print(f"Found {len(public_stations)} public EV charging stations in Texas")
```

#### Example 6: Find Stations with Multiple Fast Chargers

```python
# Find stations with 4+ DC Fast Chargers (major charging hubs)
where_clause = "EV_DC_Fast_Ports >= 4"
charging_hubs = get_charging_stations(where_clause)

print(f"Found {len(charging_hubs)} major charging hubs (4+ DC Fast Chargers)")
print(charging_hubs[['Station_Name', 'City', 'State', 'EV_DC_Fast_Ports']].sort_values('EV_DC_Fast_Ports', ascending=False).head(10))
```

#### Example 7: Find Alternative Fuel Stations (Non-EV)

```python
# Find CNG (Compressed Natural Gas) stations
where_clause = "Fuel_Type = 'CNG'"
cng_stations = get_charging_stations(where_clause)

print(f"Found {len(cng_stations)} CNG fueling stations")
```

#### Example 8: Find Stations by City

```python
# Find EV stations in a specific city
where_clause = "City = 'Los Angeles' AND State = 'CA' AND Fuel_Type = 'ELEC'"
la_stations = get_charging_stations(where_clause)

print(f"Found {len(la_stations)} EV charging stations in Los Angeles")
```

#### Example 9: Find Recently Added Stations

```python
# Find stations opened in 2024 or later
where_clause = "Open_Date >= '2024-01-01' AND Fuel_Type = 'ELEC'"
recent_stations = get_charging_stations(where_clause)

print(f"Found {len(recent_stations)} EV charging stations opened since 2024")
```

#### Example 10: Find Stations by Connector Type

```python
# Find stations with CCS connectors
where_clause = "EV_Connector_Types LIKE '%CCS%'"
ccs_stations = get_charging_stations(where_clause)

print(f"Found {len(ccs_stations)} stations with CCS connectors")
```

## Notes

### State Field Format

**IMPORTANT**: The `State` field contains **2-letter abbreviations**, not full names:

- **Format**: 2-letter state/province abbreviations
- **USA examples**: `CA`, `TX`, `NY`, `NM`, `FL`, etc.
- **Canada examples**: `BC`, `ON`, `QC`, `AB`, etc.
- **Query pattern**:
  - `"State = 'CA'"` for California
  - `"State = 'NM'"` for New Mexico
  - `"State = 'BC'"` for British Columbia
- **Multiple states**: Use OR
  - `"State = 'CA' OR State = 'OR' OR State = 'WA'"`

### Fuel Type Values

- `ELEC` - Electric vehicle charging
- `CNG` - Compressed Natural Gas
- `LNG` - Liquefied Natural Gas
- `LPG` - Liquefied Petroleum Gas (Propane)
- `E85` - Ethanol blend (85% ethanol)
- `BD` - Biodiesel
- `HY` - Hydrogen
- `RD` - Renewable Diesel

### EV Charging Level Fields

- **EV_Level1_EVSE_Ports**: Level 1 (120V, 2-5 miles/hour)
- **EV_Level2_EVSE_Ports**: Level 2 (240V, 10-60 miles/hour)
- **EV_DC_Fast_Ports**: DC Fast (480V+, 60-100+ miles in 20 min)

**Query patterns**:
```python
# Stations with any Level 2 charging
where = "EV_Level2_EVSE_Ports > 0"

# Stations with DC Fast Charging
where = "EV_DC_Fast_Ports > 0"

# Major charging hubs
where = "EV_DC_Fast_Ports >= 4"

# Stations with ONLY Level 2 (no fast charging)
where = "EV_Level2_EVSE_Ports > 0 AND (EV_DC_Fast_Ports IS NULL OR EV_DC_Fast_Ports = 0)"
```

### EV Network Field Values

Common networks:
- ChargePoint Network
- Tesla
- Electrify America
- EVgo Network
- Blink Network
- Non-Networked

**Query patterns**:
```python
where = "EV_Network LIKE '%ChargePoint%'"
where = "EV_Network LIKE '%Tesla%'"
where = "EV_Network = 'Non-Networked'"
```

### Accessibility Field Values

- `public` - Open to the general public
- `private` - Restricted access

**Query pattern**:
```python
where = "Accessability = 'public'"
```

### Status Field Values

- `Currently Available` - Operational
- `Planned` - Not yet open
- `Temporarily Unavailable` - Offline

**Query pattern**:
```python
where = "Current_Status = 'Currently Available'"
```

### WHERE Clause Tips

- Use 2-letter state codes: `"State = 'CA'"` not `"State = 'California'"`
- Use exact Fuel_Type codes: `"Fuel_Type = 'ELEC'"` not LIKE (unless needed)
- Filter for public access: `"Accessability = 'public'"`
- Filter operational stations: `"Current_Status = 'Currently Available'"`
- Combine EV charging levels: `"EV_DC_Fast_Ports > 0 OR EV_Level2_EVSE_Ports >= 4"`
- Use numeric comparisons: `"EV_DC_Fast_Ports >= 2"`
- Date comparisons: `"Open_Date >= '2023-01-01'"`
- Enclose string values in single quotes
- Use `1=1` to match all features (no filtering)

### Complete Example: Analyze EV Charging Infrastructure

```python
import requests
import pandas as pd

def get_charging_stations(where_clause):
    url = "https://rhvpkkiftonktxq3.svcs9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/Alternate_Fuel/FeatureServer/0"

    all_features = []
    offset = 0
    batch_size = 10000

    while True:
        params = {
            "where": where_clause,
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": batch_size
        }

        response = requests.get(url + "/query", params=params)
        data = response.json()

        if not data.get('features'):
            break

        all_features.extend(data['features'])

        if len(data['features']) < batch_size:
            break

        offset += batch_size

    if all_features:
        return pd.DataFrame([f['attributes'] for f in all_features])
    else:
        return pd.DataFrame()

# Query for operational EV charging stations in California
where_clause = "State = 'CA' AND Fuel_Type = 'ELEC' AND Current_Status = 'Currently Available'"
ca_ev_stations = get_charging_stations(where_clause)

print(f"Found {len(ca_ev_stations)} operational EV charging stations in California\n")

# Charging level distribution
level2_count = len(ca_ev_stations[ca_ev_stations['EV_Level2_EVSE_Ports'] > 0])
dc_fast_count = len(ca_ev_stations[ca_ev_stations['EV_DC_Fast_Ports'] > 0])

print(f"Stations by charging capability:")
print(f"  With Level 2 charging: {level2_count}")
print(f"  With DC Fast Charging: {dc_fast_count}")

# Total charger counts
total_level2 = ca_ev_stations['EV_Level2_EVSE_Ports'].fillna(0).sum()
total_dc_fast = ca_ev_stations['EV_DC_Fast_Ports'].fillna(0).sum()

print(f"\nTotal chargers:")
print(f"  Level 2 chargers: {int(total_level2)}")
print(f"  DC Fast Chargers: {int(total_dc_fast)}")

# Network distribution
print(f"\nTop 5 charging networks:")
network_counts = ca_ev_stations['EV_Network'].value_counts().head(5)
for network, count in network_counts.items():
    print(f"  {network}: {count} stations")

# Public access
public_count = len(ca_ev_stations[ca_ev_stations['Accessability'] == 'public'])
print(f"\nPublic access stations: {public_count} ({public_count/len(ca_ev_stations)*100:.1f}%)")

# Top 10 cities
print(f"\nTop 10 cities by number of charging stations:")
city_counts = ca_ev_stations['City'].value_counts().head(10)
for city, count in city_counts.items():
    print(f"  {city}: {count} stations")

# Largest charging hubs
hubs = ca_ev_stations[ca_ev_stations['EV_DC_Fast_Ports'] >= 4]
print(f"\nLargest charging hubs (4+ DC Fast Chargers):")
top_hubs = hubs.nlargest(5, 'EV_DC_Fast_Ports')[['Station_Name', 'City', 'EV_DC_Fast_Ports']]
for idx, row in top_hubs.iterrows():
    print(f"  {row['Station_Name']} ({row['City']}): {int(row['EV_DC_Fast_Ports'])} DC Fast Ports")
```
