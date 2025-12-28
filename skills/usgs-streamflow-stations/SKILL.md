---
name: usgs-streamflow-stations
description: Query and retrieve USGS streamflow gauging station data, navigate station networks, find stations by location or specific rivers, and access station metadata using PyNHD's NLDI interface.
---

# USGS Streamflow Stations Skill

## Description

This skill enables querying and analyzing USGS streamflow gauging stations (also called stream gauges) using the PyNHD library. USGS operates thousands of streamflow stations across the United States that measure river discharge (flow rate) and water levels. These stations are part of the National Water Information System (NWIS) and are integrated into the NHDPlus river network database.

Use this skill to find gauging stations by location, navigate upstream/downstream networks, retrieve station metadata, identify connected stations, and filter stations by specific rivers. This is essential for hydrologic analysis, watershed studies, flood forecasting, water resource management, and environmental monitoring.

## When to Use

- When the user asks to find USGS gauging stations near a location or within a region
- When you need to identify streamflow monitoring points on a **specific named river** (e.g., "Ohio River", "Scioto River")
- When the task involves finding stations upstream or downstream from a point of interest
- When the user wants to know what stations exist in a watershed or basin
- When you need to get metadata about a specific USGS station (location, river name, drainage area)
- When analyzing river networks and need to identify gauge-to-gauge relationships
- When the user asks about monitoring stations on rivers or streams
- When determining which stations measure flow for a particular water body

## How to Use

### Step 1: Import Required Libraries

Always start by importing PyNHD and related libraries:

```python
from pynhd import NLDI, WaterData
import geopandas as gpd
import pandas as pd  # CRITICAL: Always import pandas for data manipulation
```

### Step 2: Identify the Query Type and River Name Requirement

**CRITICAL DECISION POINT**: Determine if the user wants stations on a **specific named river** or all stations in a network area.

**Query Types:**

1. **Specific River Query** - User mentions a river name (e.g., "Scioto River", "Ohio River")
   - **MUST filter by river name** to avoid returning hundreds of irrelevant stations
   - Requires additional step to get flowline attributes and filter

2. **General Network Query** - User wants all stations in an area/network
   - No river name filtering needed
   - Returns all stations found in the search area

3. **By Station ID** - User provides a specific USGS station number
   - Direct query, no filtering needed

4. **By Watershed** - User wants all stations in a watershed/basin
   - Use spatial query within basin boundary

### Step 3: Execute Query Based on Type

#### For Specific River Queries (MOST COMMON - e.g., "stations on Scioto River")

**IMPORTANT**: When user asks for stations on a specific river, you MUST:
1. Navigate the network to get flowlines
2. Filter flowlines by river name using WaterData
3. Then find stations on those specific flowlines

```python
from pynhd import NLDI, WaterData
import geopandas as gpd
import pandas as pd

nldi = NLDI()
wd = WaterData("nhdflowline_network")

# Starting point coordinates
point = (-82.9988, 39.9612)
river_name = "Scioto River"  # The specific river user asked about

# Step 1: Find nearest river segment
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Step 2: Get all flowlines in the network (cast a wide net)
upstream_flowlines = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="upstreamTributaries",
    source="flowlines",
    distance=500  # km
)

downstream_flowlines = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="downstreamMain",
    source="flowlines",
    distance=500  # km
)

# Step 3: Get flowline attributes to check river names
all_comids = list(upstream_flowlines.nhdplus_comid) + list(downstream_flowlines.nhdplus_comid)
all_comids = list(set(all_comids))  # Remove duplicates
flowlines_with_attrs = wd.byid("comid", all_comids)

# Step 4: Filter to ONLY the specified river
river_flowlines = flowlines_with_attrs[
    flowlines_with_attrs.gnis_name == river_name
]

if len(river_flowlines) == 0:
    print(f"Warning: No flowlines found with name '{river_name}'")
    # Check what river we're actually on
    start_flowline = wd.byid("comid", [nearest_comid])
    actual_river = start_flowline.gnis_name.values[0]
    print(f"Starting point is on '{actual_river}'")
else:
    print(f"Found {len(river_flowlines)} {river_name} flowline segments")
    
    # Step 5: Now find stations on ONLY those river segments
    river_comids = river_flowlines.comid.tolist()
    
    # Search for stations near each river segment
    all_stations = []
    for comid in river_comids:
        try:
            # Search small radius around each river segment
            stations = nldi.navigate_byid(
                fsource="comid",
                fid=comid,
                navigation="upstreamTributaries",
                source="nwissite",
                distance=0.1  # Very small distance to get stations ON this segment
            )
            all_stations.append(stations)
        except:
            continue
    
    if all_stations:
        stations_gdf = gpd.GeoDataFrame(
            pd.concat(all_stations).drop_duplicates(subset='identifier')
        )
        print(f"Found {len(stations_gdf)} stations on {river_name}")
    else:
        print(f"No stations found on {river_name}")
```

#### For General Network Queries (No specific river mentioned)

```python
# Find nearest segment
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Find all stations in network
upstream_stations = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="upstreamTributaries",
    source="nwissite",
    distance=100  # km
)

downstream_stations = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="downstreamMain",
    source="nwissite",
    distance=100  # km
)

# Combine results
all_stations = gpd.GeoDataFrame(
    pd.concat([upstream_stations, downstream_stations]).drop_duplicates(subset='identifier')
)
```

#### For Station ID Queries

```python
station_id = "01031500"

# Get stations upstream
upstream_stations = nldi.navigate_byid(
    fsource="nwissite",
    fid=f"USGS-{station_id}",
    navigation="upstreamTributaries",
    source="nwissite",
    distance=500
)
```

#### For Watershed Queries

```python
# Get watershed boundary
basin = nldi.get_basins(station_id)

# Find all stations in watershed
import pynhd
stations_in_basin = pynhd.geoconnex(
    item="gauges",
    query={"geometry": basin.geometry.iloc[0]}
)
```

### Step 4: Extract and Format Results

Parse station information and present clearly:

```python
# Extract station IDs and names
print(f"Total stations found: {len(stations_gdf)}")
for idx, row in stations_gdf.iterrows():
    station_num = row.identifier.split('-')[1]
    station_name = row.name if 'name' in row and row.name else 'N/A'
    print(f"USGS {station_num}: {station_name}")
```

## Best Practices

- **ALWAYS import pandas**: `import pandas as pd` is required for `pd.concat()` operations
- **Filter by river name when specified**: If user mentions a specific river, you MUST filter flowlines by `gnis_name` field before finding stations
- **Use WaterData to get flowline attributes**: `wd = WaterData("nhdflowline_network")` then `wd.byid("comid", comid_list)` to get river names
- **comid_byloc syntax**: Use `nldi.comid_byloc(point)` without `crs` parameter for WGS84 coordinates, or `nldi.comid_byloc(point, loc_crs=crs_string)` for other CRS
- **Navigation parameters**:
  - `"upstreamMain"` - main channel only
  - `"upstreamTributaries"` - all tributaries (includes main channel)
  - `"downstreamMain"` - main channel only
  - `"downstreamDiversions"` - all branches
- **Set appropriate distance limits**: 50-500 km typical, but use smaller distances (0.1-1 km) when searching near specific river segments
- **Handle empty results gracefully**: Always check if dataframes have rows before processing
- **Station ID format**: Use `"USGS-{station_id}"` when station ID is the source (fid parameter)
- **Avoid overwhelming results**: For specific river queries, filter first then search, rather than searching entire network

## Supporting Files

This skill directory can include supporting files referenced in the instructions:
- `station_query_helpers.py` - Helper functions for river-specific station queries
- `river_name_lookup.json` - Common river name variations and standardization
- `navigation_patterns.md` - Common network navigation patterns

## Examples

### Example 1: Find Stations on a Specific River (MOST IMPORTANT)

**User Request:** "Find all USGS streamflow stations on the Scioto River"

**Approach:**
1. Start with a point on or near the Scioto River
2. Navigate to get all flowlines in the area
3. **CRITICAL**: Filter flowlines to only "Scioto River" using WaterData
4. Find stations on those specific flowline segments
5. Present results

```python
from pynhd import NLDI, WaterData
import geopandas as gpd
import pandas as pd

nldi = NLDI()
wd = WaterData("nhdflowline_network")

# Columbus, Ohio on Scioto River
point = (-82.9988, 39.9612)
river_name = "Scioto River"

print(f"Finding stations on {river_name}...")

# Find nearest segment
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Get flowlines in both directions
upstream_flow = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="upstreamTributaries",
    source="flowlines",
    distance=500
)

downstream_flow = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="downstreamMain",
    source="flowlines",
    distance=500
)

# Get all unique COMIDs
all_comids = list(set(
    list(upstream_flow.nhdplus_comid) + 
    list(downstream_flow.nhdplus_comid)
))

# Get flowline attributes
print(f"Fetching attributes for {len(all_comids)} flowline segments...")
flowlines_attrs = wd.byid("comid", all_comids)

# Filter to Scioto River ONLY
scioto_flowlines = flowlines_attrs[
    flowlines_attrs.gnis_name == river_name
]

print(f"Found {len(scioto_flowlines)} {river_name} segments")

# Now find stations on Scioto River segments
scioto_comids = scioto_flowlines.comid.tolist()
all_stations = []

for comid in scioto_comids:
    try:
        stations = nldi.navigate_byid(
            fsource="comid",
            fid=comid,
            navigation="upstreamTributaries",
            source="nwissite",
            distance=0.1  # Small distance
        )
        if len(stations) > 0:
            all_stations.append(stations)
    except:
        continue

if all_stations:
    stations_gdf = gpd.GeoDataFrame(
        pd.concat(all_stations).drop_duplicates(subset='identifier')
    )
    
    print(f"\nFound {len(stations_gdf)} stations on {river_name}:")
    for idx, row in stations_gdf.iterrows():
        station_id = row.identifier.split('-')[1]
        print(f"  USGS {station_id}")
else:
    print(f"No stations found on {river_name}")
```

### Example 2: Find All Upstream Stations (No River Filter)

**User Request:** "What USGS stations are upstream of station 01031500?"

**Approach:**
1. Use station ID directly as starting point
2. Navigate upstream without river name filtering
3. Present all stations found

```python
from pynhd import NLDI
import pandas as pd

nldi = NLDI()
station_id = "01031500"

upstream_stations = nldi.navigate_byid(
    fsource="nwissite",
    fid=f"USGS-{station_id}",
    navigation="upstreamTributaries",
    source="nwissite",
    distance=1000
)

print(f"Found {len(upstream_stations)} upstream stations:")
for idx, row in upstream_stations.iterrows():
    station_num = row.identifier.split('-')[1]
    station_name = row.name if 'name' in row and row.name else 'N/A'
    print(f"  USGS {station_num}: {station_name}")
```

### Example 3: Find Nearest Station to Coordinates

**User Request:** "What's the nearest USGS gauging station to coordinates -87.888, 37.743?"

**Approach:**
1. Snap to nearest river
2. Search small radius
3. Return closest station

```python
from pynhd import NLDI
import pandas as pd

nldi = NLDI()
point = (-87.888, 37.743)

# Find nearest river
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Find nearby stations (small radius)
nearby = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="upstreamTributaries",
    source="nwissite",
    distance=20  # 20 km radius
)

if len(nearby) > 0:
    # Get closest one
    closest = nearby.iloc[0]
    station_id = closest.identifier.split('-')[1]
    print(f"Nearest station: USGS {station_id}")
else:
    print("No stations within 20 km")
```

### Example 4: Verify River Name at Starting Point

**User Request:** "What river am I starting from at these coordinates?"

**Approach:**
1. Snap to nearest river segment
2. Get flowline attributes
3. Report river name

```python
from pynhd import NLDI, WaterData

nldi = NLDI()
wd = WaterData("nhdflowline_network")

point = (-82.9988, 39.9612)

# Find nearest segment
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Get flowline info
flowline = wd.byid("comid", [nearest_comid])
river_name = flowline.gnis_name.values[0]

print(f"Starting point is on: {river_name}")
print(f"COMID: {nearest_comid}")
```

### Example 5: Find Stations in Watershed

**User Request:** "Show all USGS gauges in the watershed for station 01031500"

**Approach:**
1. Get watershed boundary
2. Spatial query for stations within boundary

```python
from pynhd import NLDI
import pynhd

nldi = NLDI()
station_id = "01031500"

# Get watershed
basin = nldi.get_basins(station_id)

# Find all stations in watershed
stations = pynhd.geoconnex(
    item="gauges",
    query={"geometry": basin.geometry.iloc[0]}
)

print(f"Found {len(stations)} stations in watershed")
```

## Common Pitfalls and Solutions

### Pitfall 1: Forgetting to Import Pandas
**Error**: `NameError: name 'pd' is not defined`
**Solution**: Always include `import pandas as pd` at the top

### Pitfall 2: Not Filtering by River Name
**Problem**: User asks for "stations on Ohio River" but gets 200+ stations from entire network
**Solution**: Always filter flowlines by `gnis_name` field before finding stations

### Pitfall 3: Using Wrong CRS Parameter
**Error**: `TypeError: comid_byloc() got an unexpected keyword argument 'crs'`
**Solution**: Use `loc_crs` parameter: `nldi.comid_byloc(point, loc_crs="EPSG:4326")` or omit for WGS84

### Pitfall 4: Empty Results Not Handled
**Error**: `IndexError: single positional indexer is out-of-bounds`
**Solution**: Always check `if len(dataframe) > 0:` before accessing rows

### Pitfall 5: Searching Too Large Area
**Problem**: Query takes forever or returns thousands of stations
**Solution**: Use smaller distance limits (20-100 km) or filter by river name first

## Notes

- USGS station IDs are typically 8-15 digit numbers
- The `identifier` field format is `"USGS-{station_id}"` - always split to extract numeric ID
- Not all river segments have stations - coverage varies by region
- Distance parameter is in kilometers
- For queries about specific rivers, ALWAYS filter by `gnis_name` field
- Some stations may be inactive - check data availability separately if needed
- GeoConnex provides richer metadata than basic NLDI responses
- When user mentions a river name, assume they want stations ON THAT SPECIFIC RIVER, not all stations in the area
- The `name` field in station results may be empty - this is normal
- Small tributaries often lack station coverage