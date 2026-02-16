---
name: state-parks
description: Use this skill for requests to retrieve state parks and state forests in the USA as a GeoDataFrame in GeoPandas. This skill can retrieve state parks by name, location, or geographic area.
---

# State Parks Skill

## Description

This skill retrieves geometries and attributes of state parks and state forests by accessing the ArcGIS Feature Service at the following URL:

```
https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Parks/FeatureServer/0
```

The service returns the following columns:

- **FID**: System-assigned unique identifier for each park feature in the service
- **NAME**: Feature name - official name of the park or forest
- **FCC**: Feature code - classification code for the feature
- **SQMI**: Area in square miles - total area of the park
- **FEATTYPE**: Feature type - type of park facility (values: "County park", "Local park", "National park or forest", "Regional park", "State park or forest")
- **Shape__Area**: System-calculated area of the park geometry in the feature service's coordinate system
- **Shape__Length**: System-calculated perimeter length of the park geometry in the feature service's coordinate system

## When to Use

Use this skill to:

- Find a state park by name
- Find all state parks in a specific state or region
- Find state parks within a geographic area (bounding box)
- Query state parks by size (area in square miles)
- Get boundaries of state parks for spatial analysis

## How to Use

### Step 1: Import Required Libraries

```python
import geopandas as gpd
import requests
```

### Step 2: Define the Query Function

Use the `get_features` function to query the feature service. The **bbox parameter** is crucial for spatial filtering - it defines a bounding box to limit results to a specific geographic area.

**IMPORTANT**: This service has a maximum record count of 2000. For queries that may return more than 2000 results, you'll need to implement pagination using the `resultOffset` parameter.

```python
def get_features(service_url, where, bbox=None, max_records=2000):
    """
    Query the ArcGIS Feature Service for state parks.
    
    Parameters:
    -----------
    service_url : str
        The URL of the ArcGIS Feature Service
    where : str
        SQL-like WHERE clause to filter features
    bbox : list or tuple, optional
        Bounding box as [minx, miny, maxx, maxy] in WGS84 (EPSG:4326)
        Default is the continental USA bounds
    max_records : int, optional
        Maximum number of records to return (default: 2000, which is the service limit)
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing the queried state park features
    """
    
    # Default to continental USA bounds if no bbox provided
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
        "outSR": "4326",  # Ensure output is in WGS84
        "resultOffset": 0,
        "resultRecordCount": min(max_records, 2000)  # Service max is 2000
    }
    
    response = requests.get(service_url + "/query", params=params)
    data = response.json()
    
    if data.get('features'):
        return gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
```

### Step 3: Query Examples

#### Example 1: Find All State Parks in Colorado

```python
url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Parks/FeatureServer/0"

# Colorado bounding box (approximate)
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# Query for state parks and forests
where = "FEATTYPE = 'State park or forest'"
co_state_parks = get_features(url, where, bbox=colorado_bbox)

print(f"Found {len(co_state_parks)} state parks in Colorado")
print(co_state_parks[['NAME', 'SQMI']].head())
```

#### Example 2: Find a Specific State Park by Name

```python
# Query for "Rocky Mountain Arsenal National Wildlife Refuge" or similar
where = "FEATTYPE = 'State park or forest' AND LOWER(NAME) LIKE '%cherry creek%'"
park = get_features(url, where)

if len(park) > 0:
    print(f"Found: {park.iloc[0]['NAME']}")
    print(f"Area: {park.iloc[0]['SQMI']} square miles")
```

#### Example 3: Find All State Parks in California

```python
# California bounding box (approximate)
california_bbox = [-124.48, 32.53, -114.13, 42.01]

# Query for state parks in California
where = "FEATTYPE = 'State park or forest'"
ca_state_parks = get_features(url, where, bbox=california_bbox)

print(f"Found {len(ca_state_parks)} state parks in California")
```

#### Example 4: Find Large State Parks (over 10 square miles)

```python
# Query for large state parks
where = "FEATTYPE = 'State park or forest' AND SQMI > 10"
large_parks = get_features(url, where)

print(f"Found {len(large_parks)} state parks larger than 10 square miles")
print(large_parks[['NAME', 'SQMI']].sort_values('SQMI', ascending=False).head(10))
```

#### Example 5: Find State Parks in Multiple Western States

```python
# Western states bounding box (approximate: CO, UT, WY, MT, ID)
western_bbox = [-117.0, 36.0, -102.0, 49.0]

# Query for state parks in the western region
where = "FEATTYPE = 'State park or forest'"
western_parks = get_features(url, where, bbox=western_bbox)

print(f"Found {len(western_parks)} state parks in western states")
```

#### Example 6: Find State Parks by Partial Name Match

```python
# Find all state parks with "Lake" in the name
where = "FEATTYPE = 'State park or forest' AND NAME LIKE '%Lake%'"
lake_parks = get_features(url, where)

print(f"Found {len(lake_parks)} state parks with 'Lake' in the name")
```

## Notes

The service has a maximum record count of 2000. If your query returns more results, you'll need to use pagination or refine your query with a more specific WHERE clause or smaller bbox.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for efficient spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query, reducing response time and data volume
- **Default**: If not provided, defaults to continental USA bounds
- **Use case**: Always provide a bbox when querying for features in a specific state or region

**Why bbox matters**: Without a bbox, the service may return all state parks matching the WHERE clause across the entire USA, which is inefficient. The bbox acts as a spatial pre-filter, dramatically improving query performance.

**Common State Bounding Boxes**:
```python
# Colorado
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# California
california_bbox = [-124.48, 32.53, -114.13, 42.01]

# Texas
texas_bbox = [-106.65, 25.84, -93.51, 36.50]

# Florida
florida_bbox = [-87.63, 24.52, -80.03, 31.00]

# New York
newyork_bbox = [-79.76, 40.50, -71.86, 45.01]

# Washington
washington_bbox = [-124.85, 45.54, -116.92, 49.00]
```

### Using the FEATTYPE Field

The FEATTYPE field has only 5 distinct values:

- **"County park"** - County-level parks
- **"Local park"** - Local/municipal parks
- **"National park or forest"** - National Park Service and National Forest Service properties
- **"Regional park"** - Regional parks
- **"State park or forest"** - State parks and state forests

**For this skill, always use**: `FEATTYPE = 'State park or forest'`

This ensures you're only retrieving state-level parks and forests, excluding county, local, regional, and national parks.

### Using the NAME Field

Query by park name:

- **Format**: Park names are stored as text (e.g., "Cherry Creek State Park", "Anza-Borrego Desert State Park")
- **Case-insensitive search**: Use `LOWER(NAME)` for case-insensitive matching
  - Example: `"LOWER(NAME) LIKE '%cherry creek%'"`
- **Exact match**: Use `NAME = 'exact name'`
  - Example: `"NAME = 'Cherry Creek State Park'"`
- **Partial match**: Use `LIKE` with `%` wildcards
  - Example: `"NAME LIKE '%Lake%'"` finds all parks with "Lake" in the name

### Using the SQMI Field

Filter by park size:

- **Format**: Area in square miles (numeric/double)
- **Query patterns**:
  - Large parks: `"SQMI > 10"` (parks larger than 10 square miles)
  - Small parks: `"SQMI < 1"` (parks smaller than 1 square mile)
  - Medium parks: `"SQMI BETWEEN 1 AND 10"`
  - Sort by size: Use `.sort_values('SQMI', ascending=False)` in pandas

### WHERE Clause Tips

- **Always filter by FEATTYPE first**: `"FEATTYPE = 'State park or forest'"`
- Use `LOWER(field)` for case-insensitive string matching on text fields
  - Example: `"LOWER(NAME) LIKE '%yosemite%'"`
- Use `LIKE` with `%` wildcards for partial matches
  - Example: `"NAME LIKE '%State Park%'"`
- Combine conditions with `AND` / `OR`
  - Example: `"FEATTYPE = 'State park or forest' AND SQMI > 5"`
- Always enclose string values in single quotes
  - Example: `"FEATTYPE = 'State park or forest'"` not `"FEATTYPE = State park or forest"`
- Use numeric comparisons for area queries
  - Example: `"SQMI > 10"` or `"SQMI BETWEEN 1 AND 5"`
- Remember the 2000 record limit - use bbox to limit geographic extent

### Handling the 2000 Record Limit

If you expect more than 2000 results (e.g., querying all state parks in the USA without a bbox), implement pagination:

```python
def get_all_features(service_url, where, bbox=None):
    """
    Get all features, handling pagination for >2000 results.
    """
    all_features = []
    offset = 0
    batch_size = 2000
    
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
        
        if len(data['features']) < batch_size:
            break
            
        offset += batch_size
    
    if all_features:
        return gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
```

### Complete Example: Find and Map State Parks in Colorado

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
        "resultRecordCount": min(max_records, 2000)
    }
    
    response = requests.get(service_url + "/query", params=params)
    data = response.json()
    
    if data.get('features'):
        return gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")

# Query for Colorado state parks
url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Parks/FeatureServer/0"
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]
where = "FEATTYPE = 'State park or forest'"

co_parks = get_features(url, where, bbox=colorado_bbox)

# Display results
print(f"Found {len(co_parks)} state parks in Colorado")
print("\nTop 10 largest state parks:")
print(co_parks[['NAME', 'SQMI']].sort_values('SQMI', ascending=False).head(10))

# Plot the parks
fig, ax = plt.subplots(figsize=(12, 8))
co_parks.plot(ax=ax, alpha=0.5, edgecolor='black')
ax.set_title('Colorado State Parks and Forests')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()
```
