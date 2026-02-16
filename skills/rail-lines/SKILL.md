---
name: rail-lines
description: Retrieve North American rail network lines. Query by location, railroad owner, track rights, network type, or passenger service. Automatically handles pagination for large result sets.
---

# Rail Network Lines Skill

## Description

This skill retrieves rail network line data for the United States, Canada, and Mexico by accessing the ArcGIS Feature Service at the following URL:

```
https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_North_American_Rail_Network_Lines/FeatureServer/0
```

**Service Details:**
- Maximum record count: 2000
- Coverage: United States, Canada, Mexico
- Data source: NTAD (National Transportation Atlas Database) North American Rail Network Lines

The service returns the following key fields:

**Location Information:**
- **STATEAB**: 2-letter state/province abbreviation (e.g., "CA", "TX", "BC", "ON")
- **STFIPS**: State FIPS code (2-digit)
- **CNTYFIPS**: County FIPS code (3-digit)
- **STCNTYFIPS**: Combined state-county FIPS code (5-digit)
- **COUNTRY**: Country code (`US`, `CA`, `MX`)
- **TIMEZONE**: Time zone code (`E`-Eastern, `C`-Central, `M`-Mountain, `P`-Pacific, `A`-Atlantic, `N`-Newfoundland, `G`-GMT+10, `U`-GMT+9.5)

**Network Information:**
- **FRAARCID**: FRA (Federal Railroad Administration) Arc ID
- **FRFRANODE**: From FRA Node ID
- **TOFRANODE**: To FRA Node ID
- **FRADISTRCT**: FRA District code (1-9, 99 for outside US)
- **DIVISION**: Railroad division name
- **SUBDIV**: Subdivision name
- **BRANCH**: Branch name
- **YARDNAME**: Yard name
- **NET**: Network type code
- **STRACNET**: STRACNET designation

**Track Information:**
- **RROWNER1**: Primary railroad owner code (AAR code)
- **RROWNER2**: Secondary railroad owner code
- **RROWNER3**: Tertiary railroad owner code
- **TRKRGHTS1-9**: Track rights codes (up to 9 railroads with rights)
- **TRACKS**: Number of tracks at this location
- **MILES**: Segment length in miles
- **KM**: Segment length in kilometers

**Passenger Service:**
- **PASSNGR**: Passenger service code

## When to Use

Use this skill to:

- Find rail lines by state, province, or country
- Find rail lines owned by specific railroads (UP, BNSF, CSX, NS, etc.)
- Find lines with passenger service (Amtrak, commuter)
- Find STRACNET designated lines (strategic rail network)
- Analyze rail network coverage and connectivity
- Find rail yards and division points
- Calculate total track miles by owner or region
- Query industrial leads and branch lines

## How to Use

### Step 1: Import Required Libraries

```python
import requests
import pandas as pd
import geopandas as gpd
```

### Step 2: Define the Query Function

**CRITICAL**: This function automatically handles pagination to retrieve ALL results, even when more than 2000 records match your query.

```python
def get_rail_lines(where_clause):
    """
    Query the ArcGIS Feature Service for rail network lines.

    AUTOMATICALLY HANDLES PAGINATION - retrieves all results even if >2000.

    Parameters:
    -----------
    where_clause : str
        SQL-like WHERE clause to filter features (e.g., "STATEAB = 'CA'")

    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing ALL queried rail line features with geometry
    """
    url = "https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_North_American_Rail_Network_Lines/FeatureServer/0"

    all_features = []
    offset = 0
    batch_size = 2000

    while True:
        params = {
            "where": where_clause,
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson",
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
        return gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
```

### Step 3: Query Examples

#### Example 1: Find Rail Lines by State

```python
# Query for rail lines in California
where_clause = "STATEAB = 'CA'"
ca_rail = get_rail_lines(where_clause)

print(f"Found {len(ca_rail)} rail line segments in California")
total_miles = ca_rail['MILES'].sum()
print(f"Total track miles: {total_miles:.1f}")
```

#### Example 2: Find Rail Lines by Owner

```python
# Find Union Pacific owned lines (UP AAR code)
where_clause = "RROWNER1 = 'UP'"
up_lines = get_rail_lines(where_clause)

print(f"Found {len(up_lines)} Union Pacific line segments")
up_miles = up_lines['MILES'].sum()
print(f"Total UP miles: {up_miles:.1f}")
```

#### Example 3: Find Passenger Rail Lines

```python
# Find lines with Amtrak & Commuter passenger service
where_clause = "PASSNGR = 'B'"
passenger_lines = get_rail_lines(where_clause)

print(f"Found {len(passenger_lines)} passenger rail line segments")
```

#### Example 4: Find STRACNET Designated Lines

```python
# Find STRACNET designated strategic rail lines
where_clause = "STRACNET = 'S'"
stracnet_lines = get_rail_lines(where_clause)

print(f"Found {len(stracnet_lines)} STRACNET designated segments")
stracnet_miles = stracnet_lines['MILES'].sum()
print(f"Total STRACNET miles: {stracnet_miles:.1f}")
```

#### Example 5: Find Rail Lines by Multiple States

```python
# Find rail lines in Pacific Northwest states
where_clause = "STATEAB = 'WA' OR STATEAB = 'OR' OR STATEAB = 'ID'"
pnw_rail = get_rail_lines(where_clause)

print(f"Found {len(pnw_rail)} rail line segments in Pacific Northwest")
```

#### Example 6: Find Lines by Country

```python
# Find rail lines in Canada
where_clause = "COUNTRY = 'CA'"
canada_rail = get_rail_lines(where_clause)

print(f"Found {len(canada_rail)} rail line segments in Canada")
canada_km = canada_rail['KM'].sum()
print(f"Total track kilometers: {canada_km:.1f}")
```

#### Example 7: Find Multi-Track Lines

```python
# Find lines with 2 or more tracks (double/triple track mainlines)
where_clause = "TRACKS >= 2"
multi_track = get_rail_lines(where_clause)

print(f"Found {len(multi_track)} multi-track line segments")
```

#### Example 8: Find Main Network Lines

```python
# Find main sub network lines (not industrial leads or yard tracks)
where_clause = "NET = 'M'"
main_lines = get_rail_lines(where_clause)

print(f"Found {len(main_lines)} main network line segments")
main_miles = main_lines['MILES'].sum()
print(f"Total main line miles: {main_miles:.1f}")
```

#### Example 9: Find Lines with Track Rights

```python
# Find lines where other railroads have track rights
where_clause = "TRKRGHTS1 IS NOT NULL AND TRKRGHTS1 <> ''"
rights_lines = get_rail_lines(where_clause)

print(f"Found {len(rights_lines)} segments with track rights")
```

#### Example 10: Find Railroad Yards

```python
# Find segments that are part of named yards
where_clause = "YARDNAME IS NOT NULL AND YARDNAME <> ''"
yard_segments = get_rail_lines(where_clause)

print(f"Found {len(yard_segments)} yard segments")
if 'YARDNAME' in yard_segments.columns:
    print(f"Unique yards: {yard_segments['YARDNAME'].nunique()}")
```

## Notes

### Common Railroad Owner Codes (AAR Codes)

**Class I Railroads:**
- `UP` - Union Pacific
- `BNSF` - BNSF Railway
- `CSX` - CSX Transportation
- `NS` - Norfolk Southern
- `KCS` - Kansas City Southern (now part of UP/CP)
- `CN` - Canadian National Railway
- `CP` - Canadian Pacific Kansas City

**Regional/Short Line Codes:**
- `GCR` - Genesee & Wyoming (various short lines)
- `IAIS` - Iowa Interstate Railroad
- `WC` - Wisconsin Central
- `SOO` - Soo Line
- `IM` - Illinois Midland
- And hundreds more regional/short line codes

### Passenger Service Codes (PASSNGR)

- `B` - Amtrak & Commuter
- `C` - Commuter only
- `T` - Tourist, museum, or science passenger service
- `E` - Electric passenger service (historic/streetcar)
- Other codes exist for various passenger service types

### Network Type Codes (NET)

- `M` - Main sub network
- `I` - Major Industrial Lead
- `O` - Other track (minor industrial leads)
- `Y` - Yard track
- `S` - Spur/Industrial track
- Other codes exist for specific track classifications

### STRACNET Codes

- `S` - STRACNET designated line (strategic rail network)
- `C` - Connector designated line

### Time Zone Codes

- `E` - Eastern
- `C` - Central
- `M` - Mountain
- `P` - Pacific
- `A` - Atlantic (Canada)
- `N` - Newfoundland (Canada)
- `G` - GMT+10 (Alaska)
- `U` - GMT+9.5 (Alaska)

### FRA District Codes

- `1` through `9` - FRA Districts within United States
- `99` - Out of the United States (Canada, Mexico)

### WHERE Clause Tips

- Use 2-letter state abbreviations: `"STATEAB = 'CA'"` not `"STATEAB = 'California'"`
- Use AAR codes for owners: `"RROWNER1 = 'UP'"` not `"RROWNER1 = 'Union Pacific'"`
- Use country codes: `"COUNTRY = 'US'"` for United States
- Combine conditions with OR: `"STATEAB = 'CA' OR STATEAB = 'NV' OR STATEAB = 'AZ'"`
- Use IS NOT NULL for checking existence: `"YARDNAME IS NOT NULL"`
- Use numeric comparisons: `"TRACKS >= 2"`, `"MILES > 10"`
- Enclose string values in single quotes
- Use `1=1` to match all features (no filtering)

### Complete Example: Analyze Rail Network by State

```python
import requests
import pandas as pd
import geopandas as gpd

def get_rail_lines(where_clause):
    url = "https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_North_American_Rail_Network_Lines/FeatureServer/0"

    all_features = []
    offset = 0
    batch_size = 2000

    while True:
        params = {
            "where": where_clause,
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson",
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
        return gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")

# Query for all rail lines in Texas
where_clause = "STATEAB = 'TX'"
tx_rail = get_rail_lines(where_clause)

print(f"Rail Network Analysis: Texas\n")
print(f"Total segments: {len(tx_rail)}")

# Calculate total miles
total_miles = tx_rail['MILES'].sum()
print(f"Total track miles: {total_miles:.1f}")

# Track count distribution
if 'TRACKS' in tx_rail.columns:
    track_dist = tx_rail['TRACKS'].value_counts().sort_index()
    print(f"\nTrack count distribution:")
    for tracks, count in track_dist.items():
        if pd.notna(tracks):
            miles = tx_rail[tx_rail['TRACKS'] == tracks]['MILES'].sum()
            print(f"  {int(tracks)} track(s): {count} segments, {miles:.1f} miles")

# Network type distribution
if 'NET' in tx_rail.columns:
    net_dist = tx_rail['NET'].value_counts()
    print(f"\nNetwork type distribution:")
    for net_type, count in net_dist.items():
        miles = tx_rail[tx_rail['NET'] == net_type]['MILES'].sum()
        print(f"  {net_type}: {count} segments, {miles:.1f} miles")

# Top owners
if 'RROWNER1' in tx_rail.columns:
    owner_miles = tx_rail.groupby('RROWNER1')['MILES'].sum().sort_values(ascending=False)
    print(f"\nTop 10 railroad owners by miles:")
    for owner, miles in owner_miles.head(10).items():
        if pd.notna(owner):
            print(f"  {owner}: {miles:.1f} miles")

# Passenger service
if 'PASSNGR' in tx_rail.columns:
    passenger = tx_rail[tx_rail['PASSNGR'].notna()]
    print(f"\nPassenger service segments: {len(passenger)}")
    if len(passenger) > 0:
        passenger_miles = passenger['MILES'].sum()
        print(f"  Passenger track miles: {passenger_miles:.1f}")

# STRACNET
if 'STRACNET' in tx_rail.columns:
    stracnet = tx_rail[tx_rail['STRACNET'] == 'S']
    print(f"\nSTRACNET segments: {len(stracnet)}")
    stracnet_miles = stracnet['MILES'].sum()
    print(f"  STRACNET miles: {stracnet_miles:.1f}")

# Time zone distribution
if 'TIMEZONE' in tx_rail.columns:
    tz_dist = tx_rail['TIMEZONE'].value_counts()
    print(f"\nTime zone distribution:")
    tz_names = {'E': 'Eastern', 'C': 'Central', 'M': 'Mountain', 'P': 'Pacific'}
    for tz_code, count in tz_dist.items():
        if tz_code in tz_names:
            miles = tx_rail[tx_rail['TIMEZONE'] == tz_code]['MILES'].sum()
            print(f"  {tz_names[tz_code]}: {count} segments, {miles:.1f} miles")
```
