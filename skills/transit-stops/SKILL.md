---
name: transit-stops
description: Retrieve public transit stops nationwide. Query by location, stop type, or accessibility. Automatically handles pagination for large result sets.
---

# Transit Stops Skill

## Description

This skill retrieves geometries and attributes of public transportation stops by accessing the ArcGIS Feature Service at the following URL:

```
https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/NTAD_National_Transit_Map_Stops/FeatureServer/0
```

The service returns the following columns:

- **OBJECTID**: System-assigned unique identifier for each transit stop feature in the service
- **ntd_id**: National Transit Database ID - identifies the transit agency
- **feed_id**: GTFS feed identifier for the transit agency
- **stop_id**: Unique identifier for the stop within the transit system
- **stop_name**: Name of the transit stop (e.g., "Main St & 1st Ave", "Union Station")
- **stop_desc**: Description of the stop location or additional details
- **stop_lat**: Latitude coordinate of the stop
- **stop_lon**: Longitude coordinate of the stop
- **zone_id**: Fare zone identifier (if applicable)
- **stop_url**: URL with more information about the stop
- **stop_code**: Short code or identifier displayed to riders
- **location_type**: Type of location (0=stop/platform, 1=station, 2=entrance/exit, 3=generic node, 4=boarding area)
- **parent_station**: ID of parent station if this stop is part of a larger station complex
- **stop_timezone**: Timezone of the stop (if different from agency default)
- **wheelchair_boarding**: Wheelchair accessibility (0=no info, 1=accessible, 2=not accessible)
- **level_id**: Identifier for the level/floor of the stop (for multi-level stations)
- **platform_code**: Platform identifier (e.g., "Track 1", "Gate B")
- **stop_type**: Numeric code for stop type
- **stop_type_text**: Human-readable description of stop type (e.g., "Bus Stop", "Rail Station", "Ferry Terminal")
- **download_date**: Date when the data was downloaded/updated (format: YYYY-MM-DD)

## When to Use

Use this skill to:

- Find transit stops by name or location
- Find all stops for a specific transit agency (by ntd_id)
- Find wheelchair-accessible stops
- Find stops within a geographic area (city, county, region)
- Query stops by type (bus stops, rail stations, ferry terminals, etc.)
- Analyze transit coverage and accessibility
- Find stops near a specific location

## How to Use

### Step 1: Import Required Libraries

```python
import geopandas as gpd
import requests
```

### Step 2: Define the Query Function

**⚠️ IMPORTANT**: Transit stops are numerous - urban areas often have 5,000+ stops. This function **automatically handles pagination** to retrieve ALL results, even when more than 2000 records match your query.

Use the `get_features` function to query the feature service:

```python
def get_features(service_url, where, bbox=None):
    """
    Query the ArcGIS Feature Service for transit stops.
    
    AUTOMATICALLY HANDLES PAGINATION - will retrieve all results even if >2000.
    
    Parameters:
    -----------
    service_url : str
        The URL of the ArcGIS Feature Service
    where : str
        SQL-like WHERE clause to filter features
    bbox : list or tuple, optional
        Bounding box as [minx, miny, maxx, maxy] in WGS84 (EPSG:4326)
        Default is the continental USA bounds
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing ALL queried transit stop features
    """
    all_features = []
    offset = 0
    batch_size = 2000
    
    # Default to continental USA bounds if no bbox provided
    if bbox is None:
        bbox = [-125.0, 24.396308, -66.93457, 49.384358]
    
    minx, miny, maxx, maxy = bbox
    
    while True:
        params = {
            "where": where,
            "geometry": f"{minx},{miny},{maxx},{maxy}",
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson",
            "outSR": "4326",
            "resultOffset": offset,
            "resultRecordCount": batch_size
        }
        
        response = requests.get(service_url + "/query", params=params)
        data = response.json()
        
        if not data.get('features'):
            break
            
        all_features.extend(data['features'])
        
        # If we got fewer features than requested, we've reached the end
        if len(data['features']) < batch_size:
            break
            
        offset += batch_size
    
    if all_features:
        return gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
```

### Step 3: Query Examples

#### Example 1: Find Transit Stops in Denver, Colorado

```python
url = "https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/NTAD_National_Transit_Map_Stops/FeatureServer/0"

# Denver area bounding box (approximate)
denver_bbox = [-105.11, 39.61, -104.87, 39.91]

# Query for all transit stops in Denver
where = "1=1"  # Get all stops within the bbox
denver_stops = get_features(url, where, bbox=denver_bbox)

print(f"Found {len(denver_stops)} transit stops in Denver")
print(denver_stops[['stop_name', 'stop_type_text']].head())
```

#### Example 2: Find Wheelchair-Accessible Stops

```python
# San Francisco area bounding box
sf_bbox = [-122.52, 37.71, -122.35, 37.81]

# Query for wheelchair-accessible stops
where = "wheelchair_boarding = '1'"
accessible_stops = get_features(url, where, bbox=sf_bbox)

print(f"Found {len(accessible_stops)} wheelchair-accessible stops in San Francisco")
```

#### Example 3: Find Stops by Name

```python
# Find stops with "Union Station" in the name
where = "LOWER(stop_name) LIKE '%union station%'"
union_stations = get_features(url, where)

print(f"Found {len(union_stations)} stops with 'Union Station' in the name")
for idx, row in union_stations.iterrows():
    print(f"  - {row['stop_name']} ({row['stop_type_text']})")
```

#### Example 4: Find Stops by Type

```python
# Chicago area bounding box
chicago_bbox = [-87.94, 41.64, -87.52, 42.02]

# Find rail stations in Chicago
where = "stop_type_text LIKE '%Rail%'"
rail_stations = get_features(url, where, bbox=chicago_bbox)

print(f"Found {len(rail_stations)} rail stations in Chicago")
```

#### Example 5: Find Bus Stops in a City

```python
# Seattle area bounding box
seattle_bbox = [-122.44, 47.48, -122.24, 47.73]

# Find bus stops
where = "stop_type_text LIKE '%Bus%'"
bus_stops = get_features(url, where, bbox=seattle_bbox)

print(f"Found {len(bus_stops)} bus stops in Seattle")
```

#### Example 6: Find Stops for a Specific Transit Agency

```python
# Query stops for a specific NTD ID (transit agency)
# Note: You'll need to know the specific ntd_id for your agency of interest
where = "ntd_id = '90154'"  # Example NTD ID
agency_stops = get_features(url, where)

print(f"Found {len(agency_stops)} stops for this transit agency")
```

#### Example 7: Find Stations (vs. individual stops)

```python
# Portland area bounding box
portland_bbox = [-122.76, 45.42, -122.54, 45.64]

# Find stations (location_type = 1)
where = "location_type = '1'"
stations = get_features(url, where, bbox=portland_bbox)

print(f"Found {len(stations)} stations in Portland")
```

## Notes

This service may contain millions of transit stops across the USA. Always use a bbox or specific WHERE clause to limit your query scope and avoid timeout errors.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for efficient spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query, reducing response time and data volume
- **Default**: If not provided, defaults to continental USA bounds
- **Use case**: ALWAYS provide a bbox when querying transit stops to limit results to a specific city or region

**Why bbox matters**: Transit stops are numerous - major cities may have thousands of stops. Without a bbox, queries may timeout or return too many results. The bbox acts as a spatial pre-filter, dramatically improving query performance.

**Common City Bounding Boxes**:
```python
# New York City
nyc_bbox = [-74.26, 40.49, -73.70, 40.92]

# Los Angeles
la_bbox = [-118.67, 33.70, -118.16, 34.34]

# Chicago
chicago_bbox = [-87.94, 41.64, -87.52, 42.02]

# San Francisco
sf_bbox = [-122.52, 37.71, -122.35, 37.81]

# Seattle
seattle_bbox = [-122.44, 47.48, -122.24, 47.73]

# Boston
boston_bbox = [-71.19, 42.23, -70.99, 42.40]

# Denver
denver_bbox = [-105.11, 39.61, -104.87, 39.91]

# Portland, OR
portland_bbox = [-122.76, 45.42, -122.54, 45.64]
```

### Using the stop_type_text Field

The `stop_type_text` field provides human-readable descriptions of stop types. Common values include:

- **Bus stops**: Contains "Bus"
- **Rail stations**: Contains "Rail" (Light Rail, Heavy Rail, Commuter Rail)
- **Ferry terminals**: Contains "Ferry"
- **Subway stations**: Contains "Subway" or "Metro"
- **Tram stops**: Contains "Tram" or "Streetcar"

**Query patterns**:
```python
# Find bus stops
where = "stop_type_text LIKE '%Bus%'"

# Find rail stations
where = "stop_type_text LIKE '%Rail%'"

# Find ferry terminals
where = "stop_type_text LIKE '%Ferry%'"
```

### Using the wheelchair_boarding Field

The `wheelchair_boarding` field indicates accessibility:

- **'0'**: No accessibility information available
- **'1'**: Wheelchair accessible
- **'2'**: Not wheelchair accessible

**Query patterns**:
```python
# Find accessible stops
where = "wheelchair_boarding = '1'"

# Find stops without accessibility info
where = "wheelchair_boarding = '0'"

# Find inaccessible stops
where = "wheelchair_boarding = '2'"
```

### Using the location_type Field

The `location_type` field distinguishes between different types of locations:

- **'0'**: Stop or platform (typical bus stop or train platform)
- **'1'**: Station (parent station containing multiple stops/platforms)
- **'2'**: Entrance or exit to a station
- **'3'**: Generic node (used for pathways)
- **'4'**: Boarding area (specific location on a platform)

**Query patterns**:
```python
# Find stations only
where = "location_type = '1'"

# Find individual stops/platforms
where = "location_type = '0'"

# Find station entrances
where = "location_type = '2'"
```

### Using the stop_name Field

Query by stop name:

- **Format**: Stop names vary by transit system (e.g., "Main St & 1st Ave", "Union Station - Platform 3")
- **Case-insensitive search**: Use `LOWER(stop_name)` for case-insensitive matching
  - Example: `"LOWER(stop_name) LIKE '%main street%'"`
- **Exact match**: Use `stop_name = 'exact name'`
  - Example: `"stop_name = 'Union Station'"`
- **Partial match**: Use `LIKE` with `%` wildcards
  - Example: `"stop_name LIKE '%Station%'"` finds all stops with "Station" in the name

### WHERE Clause Tips

- **Always use a bbox**: Transit stops are numerous - always limit geographic extent
- Use `LOWER(field)` for case-insensitive string matching on text fields
  - Example: `"LOWER(stop_name) LIKE '%market%'"`
- **For stop_type_text**: Use `LIKE` with `%` wildcards
  - Example: `"stop_type_text LIKE '%Bus%'"` for bus stops
  - Example: `"stop_type_text LIKE '%Rail%'"` for rail stations
- **For wheelchair_boarding**: Use exact values '0', '1', or '2'
  - Example: `"wheelchair_boarding = '1'"` for accessible stops
- **For location_type**: Use exact values '0', '1', '2', '3', or '4'
  - Example: `"location_type = '1'"` for stations
- Use `LIKE` with `%` wildcards for partial matches
  - Example: `"stop_name LIKE '%Union%'"` finds stops with "Union" in the name
- Combine multiple conditions with `AND` / `OR`
  - Example: `"stop_type_text LIKE '%Rail%' AND wheelchair_boarding = '1'"`
- Always enclose string values in single quotes
- Use `1=1` to match all features when relying solely on spatial filtering (bbox)

### Complete Example: Find and Map Accessible Transit Stops in Boston

```python
import geopandas as gpd
import requests
import matplotlib.pyplot as plt

# Function definition (as above)
def get_features(service_url, where, bbox=None, max_records=2000):
    if bbox is None:
        bbox = [-125.0, 24.396308, -66.93457, 49.384358]
    
    minx, miny, maxx, maxy = bbox
    
    params = {
        "where": where,
        "geometry": f"{minx},{miny},{maxx},{maxy}",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "4326",
        "resultOffset": 0,
        "resultRecordCount": max_records
    }
    
    response = requests.get(service_url + "/query", params=params)
    data = response.json()
    
    if data.get('features'):
        return gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")

# Query for wheelchair-accessible transit stops in Boston
url = "https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/NTAD_National_Transit_Map_Stops/FeatureServer/0"
boston_bbox = [-71.19, 42.23, -70.99, 42.40]
where = "wheelchair_boarding = '1'"

accessible_stops = get_features(url, where, bbox=boston_bbox)

# Display results
print(f"Found {len(accessible_stops)} wheelchair-accessible stops in Boston")

# Count by stop type
if 'stop_type_text' in accessible_stops.columns:
    print("\nAccessible stops by type:")
    print(accessible_stops['stop_type_text'].value_counts())

# Plot the stops
fig, ax = plt.subplots(figsize=(12, 10))
accessible_stops.plot(ax=ax, color='green', markersize=5, alpha=0.6)
ax.set_title('Wheelchair-Accessible Transit Stops in Boston')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()
```

### Finding Transit Stops Near a Point

To find transit stops within a certain distance of a point (e.g., within 0.5 miles):

```python
# Center point (e.g., downtown location)
center_lat = 42.3601
center_lon = -71.0589

# Create small bbox around the point (approx 0.01 degrees ~ 0.7 miles)
buffer = 0.01
point_bbox = [center_lon - buffer, center_lat - buffer, 
              center_lon + buffer, center_lat + buffer]

# Find all stops near this point
where = "1=1"
nearby_stops = get_features(url, where, bbox=point_bbox)

print(f"Found {len(nearby_stops)} transit stops near the location")

# Calculate actual distances using GeoPandas
from shapely.geometry import Point
center_point = gpd.GeoDataFrame(
    geometry=[Point(center_lon, center_lat)], 
    crs="EPSG:4326"
).to_crs("EPSG:3857")  # Convert to meters

nearby_stops_proj = nearby_stops.to_crs("EPSG:3857")
nearby_stops['distance_meters'] = nearby_stops_proj.geometry.distance(
    center_point.geometry.iloc[0]
)

# Filter to within 800 meters (about 0.5 miles)
within_distance = nearby_stops[nearby_stops['distance_meters'] <= 800]
print(f"{len(within_distance)} stops within 800 meters")
```
