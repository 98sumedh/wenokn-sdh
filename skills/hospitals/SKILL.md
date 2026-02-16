---
name: hospitals
description: Retrieve hospital locations in the USA. Query by name, city, state, type, or beds. Returns point geometries with facility details and contact information.
---

# Hospitals Skill

## Description

This skill retrieves locations and attributes of hospitals in the United States by accessing the ArcGIS Feature Service at the following URL:

```
https://services2.arcgis.com/RQcpPaCpMAXzUI5g/ArcGIS/rest/services/US_Hospitals/FeatureServer/0
```

**Service Details:**
- Maximum record count: 2000
- Native spatial reference: Web Mercator (EPSG:3857)
- Output spatial reference: WGS84 (EPSG:4326) - automatically transformed

The service returns the following columns:

- **FID**: System-assigned unique identifier for each hospital feature
- **ID**: Unique hospital identifier
- **NAME**: Name of the hospital facility
- **ADDRESS**: Street address
- **CITY**: City where the hospital is located
- **STATE**: Two-letter state abbreviation (e.g., "CA", "NY")
- **ZIP**: 5-digit ZIP code
- **ZIP4**: 4-digit ZIP code extension
- **TELEPHONE**: Hospital phone number
- **TYPE**: Type of hospital facility (e.g., "GENERAL ACUTE CARE", "CRITICAL ACCESS")
- **STATUS**: Operational status (e.g., "OPEN", "CLOSED")
- **POPULATION**: Population served by the hospital
- **COUNTY**: County name
- **COUNTYFIPS**: County FIPS code
- **COUNTRY**: Country code (typically "USA")
- **LATITUDE**: Latitude coordinate
- **LONGITUDE**: Longitude coordinate
- **NAICS_CODE**: North American Industry Classification System code
- **NAICS_DESC**: NAICS description
- **SOURCE**: Data source
- **SOURCEDATE**: Date when source data was collected
- **VAL_METHOD**: Validation method
- **VAL_DATE**: Validation date
- **WEBSITE**: Hospital website URL
- **STATE_ID**: State-assigned identifier
- **ALT_NAME**: Alternative name for the hospital
- **ST_FIPS**: State FIPS code
- **OWNER**: Hospital ownership type (e.g., "PRIVATE", "GOVERNMENT")
- **TTL_STAFF**: Total staff count
- **BEDS**: Number of beds
- **TRAUMA**: Trauma center designation (e.g., "LEVEL I", "LEVEL II")
- **HELIPAD**: Indicates if hospital has helipad ("Y" or "N")

## When to Use

Use this skill to:

- Find hospitals by name or location
- Find all hospitals in a specific city, county, or state
- Query hospitals by type (general acute care, critical access, etc.)
- Find hospitals by capacity (number of beds)
- Find trauma centers or hospitals with helipads
- Analyze hospital distribution and accessibility
- Find hospitals within a geographic area

## How to Use

### Step 1: Import Required Libraries

```python
import geopandas as gpd
import requests
```

### Step 2: Define the Query Function

Use the `get_features` function to query the feature service. The **bbox parameter** is crucial for spatial filtering.

**IMPORTANT**: This service has a maximum record count of 2000. For queries that may return more than 2000 results, you'll need to implement pagination using the `resultOffset` parameter.

```python
def get_features(service_url, where, bbox=None, max_records=2000):
    """
    Query the ArcGIS Feature Service for hospitals.
    
    Note: Service uses EPSG:3857 natively, but we request output in EPSG:4326.
    
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
        GeoDataFrame containing the queried hospital features in EPSG:4326
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
        "outSR": "4326",  # Request output in WGS84 (service native is EPSG:3857)
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

#### Example 1: Find Hospitals in a Specific City

```python
url = "https://services2.arcgis.com/RQcpPaCpMAXzUI5g/ArcGIS/rest/services/US_Hospitals/FeatureServer/0"

# Query for hospitals in Boston
where = "CITY = 'BOSTON' AND STATE = 'MA'"
boston_hospitals = get_features(url, where)

print(f"Found {len(boston_hospitals)} hospitals in Boston")
print(boston_hospitals[['NAME', 'ADDRESS', 'BEDS']].head())
```

#### Example 2: Find All Hospitals in a State

```python
# Colorado bounding box
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# Query for all hospitals in Colorado
where = "STATE = 'CO'"
co_hospitals = get_features(url, where, bbox=colorado_bbox)

print(f"Found {len(co_hospitals)} hospitals in Colorado")
```

#### Example 3: Find Hospitals by Name

```python
# Find hospitals with "Memorial" in the name
where = "NAME LIKE '%MEMORIAL%'"
memorial_hospitals = get_features(url, where)

print(f"Found {len(memorial_hospitals)} Memorial hospitals")
```

#### Example 4: Find Large Hospitals (by Bed Count)

```python
# Find hospitals with 300 or more beds
where = "BEDS >= 300"
large_hospitals = get_features(url, where)

print(f"Found {len(large_hospitals)} hospitals with 300+ beds")
print(large_hospitals[['NAME', 'CITY', 'STATE', 'BEDS']].sort_values('BEDS', ascending=False).head(10))
```

#### Example 5: Find Trauma Centers

```python
# Find Level I trauma centers
where = "TRAUMA = 'LEVEL I'"
level1_trauma = get_features(url, where)

print(f"Found {len(level1_trauma)} Level I trauma centers")
```

#### Example 6: Find Hospitals with Helipads

```python
# California bounding box
california_bbox = [-124.48, 32.53, -114.13, 42.01]

# Find hospitals with helipads in California
where = "HELIPAD = 'Y' AND STATE = 'CA'"
ca_helipad_hospitals = get_features(url, where, bbox=california_bbox)

print(f"Found {len(ca_helipad_hospitals)} hospitals with helipads in California")
```

#### Example 7: Find Hospitals by Type

```python
# Find Critical Access Hospitals
where = "TYPE = 'CRITICAL ACCESS'"
critical_access = get_features(url, where)

print(f"Found {len(critical_access)} Critical Access Hospitals")
```

#### Example 8: Find Hospitals by Ownership

```python
# Find government-owned hospitals
where = "OWNER LIKE '%GOVERNMENT%'"
govt_hospitals = get_features(url, where)

print(f"Found {len(govt_hospitals)} government-owned hospitals")
```

## Notes

The service has a maximum record count of 2000. If your query returns more results, you'll need to use pagination or refine your query with a more specific WHERE clause or smaller bbox.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for efficient spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query, reducing response time and data volume
- **Default**: If not provided, defaults to continental USA bounds
- **Use case**: Always provide a bbox when querying for hospitals in a specific region

**Why bbox matters**: Without a bbox, the service may return all hospitals matching the WHERE clause across the entire USA, which could exceed the 2000 record limit. The bbox acts as a spatial pre-filter, dramatically improving query performance.

**Common City/Region Bounding Boxes**:
```python
# New York City
nyc_bbox = [-74.26, 40.49, -73.70, 40.92]

# Los Angeles
la_bbox = [-118.67, 33.70, -118.16, 34.34]

# Chicago
chicago_bbox = [-87.94, 41.64, -87.52, 42.02]

# Houston
houston_bbox = [-95.82, 29.52, -95.01, 30.11]

# Phoenix
phoenix_bbox = [-112.32, 33.29, -111.92, 33.69]

# San Francisco Bay Area
sf_bay_bbox = [-122.52, 37.20, -121.80, 37.90]

# Colorado
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# California
california_bbox = [-124.48, 32.53, -114.13, 42.01]
```

### Using the STATE Field

The `STATE` field contains two-letter state abbreviations:

- **Format**: Uppercase two-letter codes (e.g., "CA", "NY", "TX")
- **Query pattern**: Use exact match with state abbreviation
  - Example: `"STATE = 'CA'"` for California
  - Example: `"STATE = 'NY'"` for New York
- **Multiple states**: Use OR to find hospitals in multiple states
  - Example: `"STATE = 'CA' OR STATE = 'OR' OR STATE = 'WA'"` for West Coast
- **Important**: Use uppercase abbreviations, not full state names

### Using the TYPE Field

Filter by hospital type:

- **Common values**:
  - `"GENERAL ACUTE CARE"` - General hospitals with acute care
  - `"CRITICAL ACCESS"` - Critical Access Hospitals (rural facilities)
  - `"CHILDREN"` - Pediatric hospitals
  - `"PSYCHIATRIC"` - Mental health facilities
- **Query patterns**:
  - Example: `"TYPE = 'GENERAL ACUTE CARE'"`
  - Example: `"TYPE LIKE '%CHILDREN%'"` for partial matches

### Using the STATUS Field

Filter by operational status:

- **Common values**:
  - `"OPEN"` - Currently operational
  - `"CLOSED"` - No longer operating
- **Query pattern**:
  - Example: `"STATUS = 'OPEN'"` for active hospitals only

### Using the BEDS Field

Filter by hospital capacity:

- **Format**: Numeric (double precision)
- **Query patterns**:
  - Large hospitals: `"BEDS >= 300"`
  - Medium hospitals: `"BEDS BETWEEN 100 AND 300"`
  - Small hospitals: `"BEDS < 100"`
  - Sort by size: Use `.sort_values('BEDS', ascending=False)` in pandas

### Using the TRAUMA Field

Filter by trauma center designation:

- **Common values**:
  - `"LEVEL I"` - Highest level trauma center
  - `"LEVEL II"` - Second-tier trauma center
  - `"LEVEL III"` - Third-tier trauma center
  - `"LEVEL IV"` - Basic trauma services
- **Query patterns**:
  - Example: `"TRAUMA = 'LEVEL I'"` for top-tier trauma centers
  - Example: `"TRAUMA IS NOT NULL"` for any trauma-designated hospital

### Using the HELIPAD Field

Filter by helipad availability:

- **Values**: "Y" (yes) or "N" (no)
- **Query pattern**:
  - Example: `"HELIPAD = 'Y'"` for hospitals with helipads

### WHERE Clause Tips

- Use uppercase for STATE field: `"STATE = 'CA'"` not `"STATE = 'ca'"`
- Use LIKE for partial name matches: `"NAME LIKE '%MEMORIAL%'"`
- Combine multiple conditions with AND / OR:
  - Example: `"STATE = 'CA' AND BEDS >= 200 AND TRAUMA = 'LEVEL I'"`
- Use numeric comparisons for BEDS and POPULATION:
  - Example: `"BEDS >= 100"`
- Filter active hospitals: `"STATUS = 'OPEN'"`
- Always enclose string values in single quotes
- Use `1=1` to match all features when relying solely on spatial filtering (bbox)
- Remember the 2000 record limit - use bbox and specific WHERE clauses

### Handling the 2000 Record Limit

If you expect more than 2000 results, implement pagination:

```python
def get_all_features(service_url, where, bbox=None):
    """
    Get all features, handling pagination for >2000 results.
    
    Note: Service uses EPSG:3857 natively, but we request output in EPSG:4326.
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

### Complete Example: Analyze Hospital Distribution in a State

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

# Query for hospitals in Colorado
url = "https://services2.arcgis.com/RQcpPaCpMAXzUI5g/ArcGIS/rest/services/US_Hospitals/FeatureServer/0"
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]
where = "STATE = 'CO' AND STATUS = 'OPEN'"

co_hospitals = get_features(url, where, bbox=colorado_bbox)

# Display results
print(f"Found {len(co_hospitals)} active hospitals in Colorado\n")

# Hospital types
print("Hospitals by type:")
print(co_hospitals['TYPE'].value_counts())

# Trauma centers
trauma_centers = co_hospitals[co_hospitals['TRAUMA'].notna()]
print(f"\nTrauma centers: {len(trauma_centers)}")
if len(trauma_centers) > 0:
    print(trauma_centers['TRAUMA'].value_counts())

# Hospitals with helipads
helipad_count = len(co_hospitals[co_hospitals['HELIPAD'] == 'Y'])
print(f"\nHospitals with helipads: {helipad_count}")

# Bed capacity statistics
print(f"\nBed capacity statistics:")
print(f"  Total beds: {co_hospitals['BEDS'].sum():.0f}")
print(f"  Average beds per hospital: {co_hospitals['BEDS'].mean():.0f}")
print(f"  Largest hospital: {co_hospitals['BEDS'].max():.0f} beds")

# Top 5 largest hospitals
print("\nTop 5 largest hospitals:")
top5 = co_hospitals.nlargest(5, 'BEDS')[['NAME', 'CITY', 'BEDS']]
for idx, row in top5.iterrows():
    print(f"  {row['NAME']} ({row['CITY']}): {row['BEDS']:.0f} beds")

# Plot hospitals
fig, ax = plt.subplots(figsize=(12, 10))

# Different colors for different hospital types
if 'TYPE' in co_hospitals.columns:
    co_hospitals.plot(ax=ax, column='TYPE', legend=True, markersize=30, 
                      alpha=0.7, categorical=True, cmap='tab10')
else:
    co_hospitals.plot(ax=ax, markersize=30, alpha=0.7, color='red')

ax.set_title('Hospitals in Colorado')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()
```
