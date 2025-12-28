---
name: usgs-streamflow-stations
description: Query and retrieve USGS streamflow gauging station data, navigate station networks, find stations by location, and access station metadata using PyNHD's NLDI interface.
---

# USGS Streamflow Stations Skill

## Description

This skill enables querying and analyzing USGS streamflow gauging stations (also called stream gauges) using the PyNHD library. USGS operates thousands of streamflow stations across the United States that measure river discharge (flow rate) and water levels. These stations are part of the National Water Information System (NWIS) and are integrated into the NHDPlus river network database.

Use this skill to find gauging stations by location, navigate upstream/downstream networks, retrieve station metadata, identify connected stations, and access station attributes. This is essential for hydrologic analysis, watershed studies, flood forecasting, water resource management, and environmental monitoring.

## When to Use

- When the user asks to find USGS gauging stations near a location or within a region
- When you need to identify streamflow monitoring points on a specific river
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
import pandas as pd
```

### Step 2: Identify the Query Type

Determine what type of station query the user needs:

- **By Station ID**: User provides a specific USGS station number (e.g., "01031500")
- **By Location**: User provides coordinates or describes a location
- **By River**: User wants stations on a specific named river
- **By Watershed**: User wants all stations in a watershed/basin
- **By Network**: User wants stations upstream or downstream from a point

### Step 3: Execute the Appropriate Query

Use the corresponding PyNHD method based on the query type:

**For finding stations by location (coordinates):**
```python
from pynhd import NLDI
nldi = NLDI()

# Snap to nearest river and find nearby stations
point = (longitude, latitude)
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Find stations within a radius or along the network
stations = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="upstreamTributaries",  # or "downstreamMain"
    source="nwissite",
    distance=100  # km
)
```

**For finding stations upstream/downstream from a known station:**
```python
station_id = "01031500"

# Find upstream stations
upstream_stations = nldi.navigate_byid(
    fsource="nwissite",
    fid=f"USGS-{station_id}",
    navigation="upstreamTributaries",
    source="nwissite",
    distance=500  # km
)

# Find downstream stations
downstream_stations = nldi.navigate_byid(
    fsource="nwissite",
    fid=f"USGS-{station_id}",
    navigation="downstreamMain",
    source="nwissite",
    distance=500  # km
)
```

**For finding stations in a watershed:**
```python
# Get the watershed boundary first
basin = nldi.get_basins(station_id)

# Then use spatial query with GeoConnex
import pynhd
stations_in_basin = pynhd.geoconnex(
    item="gauges",
    query={"geometry": basin.geometry.iloc[0]}
)
```

### Step 4: Extract and Format Results

Parse the station information and present it clearly:

```python
# Extract station IDs
station_ids = stations.identifier.str.split("-").str[1].tolist()

# Get detailed metadata using GeoConnex
from pynhd import GeoConnex
gcx = GeoConnex("gauges")
detailed_info = gpd.GeoDataFrame(
    pd.concat(gcx.query({"provider_id": sid}) for sid in station_ids),
    crs=4326
)

# Present key information
print(f"Found {len(stations)} stations")
for idx, row in stations.iterrows():
    print(f"Station: {row.identifier}, Name: {row.name}")
```

## Best Practices

- Always use `"nwissite"` as the source when querying for USGS stations in `navigate_byid()`
- Station IDs should be formatted as `"USGS-{station_id}"` when used as `fid` parameter (e.g., `"USGS-01031500"`)
- Use appropriate navigation parameters:
  - `"upstreamMain"` - main channel only going upstream
  - `"upstreamTributaries"` - all tributaries going upstream
  - `"downstreamMain"` - main channel only going downstream
  - `"downstreamDiversions"` - all branches going downstream
- Set reasonable distance limits (in km) to avoid overwhelming results - typical values are 50-500 km
- For spatial queries within polygons, use `pynhd.geoconnex()` instead of `navigate_byid()`
- Cache NLDI instance to avoid repeated initialization: `nldi = NLDI()` once at the start
- Handle cases where no stations are found gracefully
- Extract station IDs from the `identifier` column and split by "-" to get the numeric ID

## Supporting Files

This skill directory can include supporting files referenced in the instructions:
- `station_query_helpers.py` - Helper functions for common station queries
- `station_metadata_template.json` - Template for station information format
- `navigation_patterns.md` - Common network navigation patterns

## Examples

### Example 1: Find All Upstream Stations

**User Request:** "What USGS stations are upstream of station 01031500?"

**Approach:**
1. Initialize NLDI interface
2. Use `navigate_byid()` with `fsource="nwissite"` and `navigation="upstreamTributaries"`
3. Set appropriate distance limit (e.g., 1000 km for entire upstream network)
4. Parse results to extract station IDs and names

```python
from pynhd import NLDI

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
    print(f"  - USGS {station_num}: {row.name if 'name' in row else 'N/A'}")
```

### Example 2: Find Nearest Station to Coordinates

**User Request:** "What's the nearest USGS gauging station to coordinates -87.888, 37.743?"

**Approach:**
1. Snap coordinates to nearest river segment (COMID)
2. Search for stations in a small radius (e.g., 20 km)
3. If multiple found, identify the closest one
4. Return station information

```python
from pynhd import NLDI

nldi = NLDI()
point = (-87.888, 37.743)

# Find nearest river segment
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Find nearby stations (within 20 km)
nearby_stations = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="upstreamTributaries",
    source="nwissite",
    distance=20
)

if len(nearby_stations) > 0:
    closest = nearby_stations.iloc[0]
    station_id = closest.identifier.split('-')[1]
    print(f"Nearest station: USGS {station_id}")
    print(f"Location: {closest.geometry.coords[0]}")
else:
    print("No stations found within 20 km")
```

### Example 3: Find Stations in a Watershed

**User Request:** "Show me all USGS gauges in the watershed for station 01031500"

**Approach:**
1. Get the watershed boundary using `get_basins()`
2. Use GeoConnex spatial query to find all stations within the boundary
3. Filter and present results

```python
from pynhd import NLDI
import pynhd

nldi = NLDI()
station_id = "01031500"

# Get watershed boundary
basin = nldi.get_basins(station_id)

# Find all gauges within the watershed
stations_in_basin = pynhd.geoconnex(
    item="gauges",
    query={"geometry": basin.geometry.iloc[0]}
)

print(f"Found {len(stations_in_basin)} stations in watershed:")
for idx, row in stations_in_basin.iterrows():
    if 'provider_id' in row:
        print(f"  - USGS {row.provider_id}")
```

### Example 4: Find Downstream Stations on Same River

**User Request:** "What USGS stations are downstream on the Ohio River from coordinates -87.888, 37.743?"

**Approach:**
1. Snap to nearest river segment
2. Navigate downstream along main channel
3. Filter to only Ohio River segments
4. Find stations on those segments
5. Present results with river name verification

```python
from pynhd import NLDI, WaterData

nldi = NLDI()
wd = WaterData("nhdflowline_network")

point = (-87.888, 37.743)

# Find nearest segment
comid_result = nldi.comid_byloc(point)
nearest_comid = comid_result.comid.values[0]

# Get downstream flowlines
downstream_flow = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="downstreamMain",
    source="flowlines",
    distance=500
)

# Get attributes to filter by river name
comids = downstream_flow.nhdplus_comid.tolist()
flowlines_attrs = wd.byid("comid", comids)
ohio_river_comids = flowlines_attrs[
    flowlines_attrs.gnis_name == "Ohio River"
].comid.tolist()

# Now find stations on Ohio River segments
stations = nldi.navigate_byid(
    fsource="comid",
    fid=nearest_comid,
    navigation="downstreamMain",
    source="nwissite",
    distance=500
)

print(f"Found {len(stations)} stations downstream on Ohio River")
```

### Example 5: Get Station Metadata

**User Request:** "Tell me about USGS station 01031500"

**Approach:**
1. Get basic info from NLDI
2. Optionally get detailed metadata from GeoConnex
3. Get watershed boundary
4. Present comprehensive information

```python
from pynhd import NLDI, GeoConnex

nldi = NLDI()
gcx = GeoConnex("gauges")
station_id = "01031500"

# Get basin
basin = nldi.get_basins(station_id)

# Get detailed metadata
station_info = gcx.query({"provider_id": station_id})

if len(station_info) > 0:
    info = station_info.iloc[0]
    print(f"Station: USGS {station_id}")
    print(f"Name: {info.name if 'name' in info else 'N/A'}")
    print(f"Coordinates: {info.geometry.coords[0] if hasattr(info.geometry, 'coords') else 'N/A'}")
    print(f"Drainage area: {basin.geometry.area[0]:.2f} sq degrees")
else:
    print(f"Station {station_id} found, but detailed metadata unavailable")
```

## Notes

- USGS station IDs are typically 8-15 digit numbers (e.g., "01031500", "07374000")
- The `identifier` field in results is formatted as `"USGS-{station_id}"` - remember to split and extract the numeric portion
- Not all river segments have nearby gauging stations - large networks may only have a few monitoring points
- Distance parameter is in kilometers, not miles
- Some stations may be inactive or historical - check data availability separately if needed
- For real-time or historical streamflow data, use PyGeoHydro's NWIS class (separate from this skill)
- Station density varies by region - more stations in populated areas and major rivers
- GeoConnex provides richer metadata than NLDI's basic station information
- When no stations are found, consider increasing the distance parameter or checking if the area has any USGS monitoring
- The `name` field in NLDI responses may be empty - use GeoConnex for more complete metadata
