---
name: recreational-areas
description: Retrieve all public recreational areas in a region including state, county, local, regional, and national parks. Query by location or optionally filter by park type.
---

# Recreational Areas Skill

## Description

This skill retrieves all types of public recreational areas (parks and forests) in a specified region by accessing the ArcGIS Feature Service at the following URL:

```
https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Parks/FeatureServer/0
```

**Service Details:**
- Maximum record count: 2000
- Native spatial reference: Web Mercator (EPSG:3857)
- Output spatial reference: WGS84 (EPSG:4326) - automatically transformed

**Recreational Area Types Available:**
This service contains **5 types of recreational facilities**:
1. **"State park or forest"** - State-managed parks and forests
2. **"County park"** - County-level parks
3. **"Local park"** - Municipal/city parks
4. **"Regional park"** - Multi-jurisdiction regional parks
5. **"National park or forest"** - National Park Service and National Forest Service properties

The service returns the following columns:

- **FID**: System-assigned unique identifier
- **NAME**: Name of the recreational area
- **FCC**: Feature code
- **SQMI**: Area in square miles
- **FEATTYPE**: Type of park facility (one of the 5 types above)
- **Shape__Area**: System-calculated area of the geometry
- **Shape__Length**: System-calculated perimeter length of the geometry

## When to Use

Use this skill to:

- **Find ALL recreational areas in a city, county, or region** (combines all park types)
- Get a comprehensive inventory of public recreation facilities
- Analyze total recreational land available in an area
- Compare distribution of different park types (state vs county vs local)
- Find recreation opportunities near a location
- Optionally filter by specific park type when needed

## How to Use

### Step 1: Import Required Libraries

```python
import geopandas as gpd
import requests
```

### Step 2: Define the Query Function

**⚠️ IMPORTANT**: This function **automatically handles pagination** to retrieve ALL results, even when more than 2000 records match your query.

```python
def get_features(service_url, where, bbox=None):
    """
    Query the ArcGIS Feature Service for recreational areas.
    
    AUTOMATICALLY HANDLES PAGINATION - will retrieve all results even if >2000.
    
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
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing ALL queried recreational area features in EPSG:4326
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
            "outSR": "4326",  # Request output in WGS84 (service native is EPSG:3857)
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

#### Example 1: Get ALL Recreational Areas in a City (Most Common Use Case)

```python
url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Parks/FeatureServer/0"

# Denver area bounding box
denver_bbox = [-105.11, 39.61, -104.87, 39.91]

# Get ALL park types - use "1=1" to match everything
where = "1=1"
denver_recreation = get_features(url, where, bbox=denver_bbox)

print(f"Found {len(denver_recreation)} recreational areas in Denver")

# Show breakdown by type
print("\nRecreational areas by type:")
type_counts = denver_recreation['FEATTYPE'].value_counts()
for park_type, count in type_counts.items():
    print(f"  {park_type}: {count}")

# Calculate total recreational land
total_sqmi = denver_recreation['SQMI'].sum()
print(f"\nTotal recreational area: {total_sqmi:.2f} square miles")
```

#### Example 2: Get ALL Recreational Areas in a County

```python
# Boulder County, Colorado area (approximate)
boulder_county_bbox = [-105.72, 39.90, -105.17, 40.30]

# Get all recreational areas
where = "1=1"
boulder_recreation = get_features(url, where, bbox=boulder_county_bbox)

print(f"Found {len(boulder_recreation)} recreational areas in Boulder County")
print(boulder_recreation[['NAME', 'FEATTYPE', 'SQMI']].head(10))
```

#### Example 3: Get ALL Recreational Areas in a State

```python
# Rhode Island (small state)
rhode_island_bbox = [-71.91, 41.09, -71.08, 42.02]

# Get all recreational areas
where = "1=1"
ri_recreation = get_features(url, where, bbox=rhode_island_bbox)

print(f"Found {len(ri_recreation)} recreational areas in Rhode Island")

# Breakdown by type
print("\nBreakdown by park type:")
for park_type in ri_recreation['FEATTYPE'].unique():
    count = len(ri_recreation[ri_recreation['FEATTYPE'] == park_type])
    total_area = ri_recreation[ri_recreation['FEATTYPE'] == park_type]['SQMI'].sum()
    print(f"  {park_type}: {count} facilities, {total_area:.2f} sq mi")
```

#### Example 4: Filter by Specific Park Type - State Parks Only

```python
# Colorado bounding box
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# Get only state parks and forests
where = "FEATTYPE = 'State park or forest'"
co_state_parks = get_features(url, where, bbox=colorado_bbox)

print(f"Found {len(co_state_parks)} state parks/forests in Colorado")
```

#### Example 5: Filter by Specific Park Type - County Parks Only

```python
# San Diego County area
san_diego_bbox = [-117.60, 32.53, -116.07, 33.51]

# Get only county parks
where = "FEATTYPE = 'County park'"
sd_county_parks = get_features(url, where, bbox=san_diego_bbox)

print(f"Found {len(sd_county_parks)} county parks in San Diego area")
```

#### Example 6: Filter by Multiple Park Types

```python
# Seattle area
seattle_bbox = [-122.44, 47.48, -122.24, 47.73]

# Get state and county parks (exclude local/regional)
where = "FEATTYPE IN ('State park or forest', 'County park')"
seattle_major_parks = get_features(url, where, bbox=seattle_bbox)

print(f"Found {len(seattle_major_parks)} state and county parks in Seattle area")
```

#### Example 7: Find Large Recreational Areas (>1 square mile)

```python
# California
california_bbox = [-124.48, 32.53, -114.13, 42.01]

# Get large recreational areas
where = "SQMI > 1"
large_parks = get_features(url, where, bbox=california_bbox)

print(f"Found {len(large_parks)} recreational areas larger than 1 square mile")
print("\nTop 10 largest:")
print(large_parks.nlargest(10, 'SQMI')[['NAME', 'FEATTYPE', 'SQMI']])
```

#### Example 8: Find Recreational Areas by Name

```python
# Find all parks with "Yellowstone" in the name
where = "NAME LIKE '%Yellowstone%'"
yellowstone_areas = get_features(url, where)

print(f"Found {len(yellowstone_areas)} areas with 'Yellowstone' in the name")
print(yellowstone_areas[['NAME', 'FEATTYPE', 'SQMI']])
```

## Notes

Fetching all recreational areas in a large region may take about one minute depending on the number of facilities.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query
- **Use case**: Always provide a bbox when querying for areas in a specific region

**Common City/State Bounding Boxes**:
```python
# Denver
denver_bbox = [-105.11, 39.61, -104.87, 39.91]

# San Francisco Bay Area
sf_bay_bbox = [-122.52, 37.20, -121.80, 37.90]

# Los Angeles
la_bbox = [-118.67, 33.70, -118.16, 34.34]

# Seattle
seattle_bbox = [-122.44, 47.48, -122.24, 47.73]

# Colorado
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# Rhode Island
rhode_island_bbox = [-71.91, 41.09, -71.08, 42.02]
```

### Using the FEATTYPE Field

The `FEATTYPE` field has exactly **5 distinct values**:

- **"State park or forest"** - State-managed facilities
- **"County park"** - County-level parks
- **"Local park"** - City/municipal parks
- **"Regional park"** - Regional facilities
- **"National park or forest"** - Federal lands (NPS & USFS)

**Query patterns**:

**Get ALL types** (most common):
```python
where = "1=1"  # Matches everything
```

**Get specific type**:
```python
where = "FEATTYPE = 'State park or forest'"
where = "FEATTYPE = 'County park'"
where = "FEATTYPE = 'Local park'"
```

**Get multiple types**:
```python
where = "FEATTYPE IN ('State park or forest', 'County park')"
```

**Exclude certain types**:
```python
# Get everything except local parks
where = "FEATTYPE <> 'Local park'"
```

### WHERE Clause Tips

- **For ALL recreational areas**: Use `"1=1"` (matches everything)
- **For specific park type**: Use exact match with `FEATTYPE = 'type'`
- **For multiple types**: Use `FEATTYPE IN ('type1', 'type2')`
- Use `LIKE` with `%` wildcards for name searches:
  - Example: `"NAME LIKE '%Lake%'"` finds all parks with "Lake" in the name
- Filter by size: `"SQMI > 1"` for large areas
- Combine conditions with AND/OR:
  - Example: `"FEATTYPE = 'State park or forest' AND SQMI > 5"`
- Always enclose string values in single quotes
- Remember: `"1=1"` is the key for getting ALL recreational areas in a region

### Complete Example: Comprehensive Recreation Analysis for a Region

```python
import geopandas as gpd
import requests
import matplotlib.pyplot as plt

# Function definition (as above)
def get_features(service_url, where, bbox=None):
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

# Query for ALL recreational areas in Colorado
url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Parks/FeatureServer/0"
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# Get ALL types
where = "1=1"
co_recreation = get_features(url, where, bbox=colorado_bbox)

# Comprehensive Analysis
print(f"RECREATIONAL AREAS IN COLORADO")
print("="*60)
print(f"\nTotal recreational areas: {len(co_recreation)}")

# Breakdown by type
print(f"\nBreakdown by type:")
type_stats = co_recreation.groupby('FEATTYPE').agg({
    'NAME': 'count',
    'SQMI': 'sum'
}).rename(columns={'NAME': 'Count', 'SQMI': 'Total Area (sq mi)'})
print(type_stats)

# Total recreational land
total_sqmi = co_recreation['SQMI'].sum()
total_acres = total_sqmi * 640
print(f"\nTotal recreational land:")
print(f"  {total_sqmi:,.2f} square miles")
print(f"  {total_acres:,.0f} acres")

# Size distribution
print(f"\nSize distribution:")
print(f"  Small (<1 sq mi): {len(co_recreation[co_recreation['SQMI'] < 1])}")
print(f"  Medium (1-10 sq mi): {len(co_recreation[(co_recreation['SQMI'] >= 1) & (co_recreation['SQMI'] < 10)])}")
print(f"  Large (10+ sq mi): {len(co_recreation[co_recreation['SQMI'] >= 10])}")

# Largest recreational areas
print(f"\nTop 10 largest recreational areas:")
top10 = co_recreation.nlargest(10, 'SQMI')[['NAME', 'FEATTYPE', 'SQMI']]
for idx, row in top10.iterrows():
    print(f"  {row['NAME']} ({row['FEATTYPE']}): {row['SQMI']:.2f} sq mi")

# Plot recreational areas by type
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Map
co_recreation.plot(ax=ax1, column='FEATTYPE', legend=True, 
                   alpha=0.6, edgecolor='black', cmap='Set3',
                   legend_kwds={'loc': 'lower left', 'fontsize': 8})
ax1.set_title('Recreational Areas in Colorado by Type')
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')

# Bar chart of counts
type_counts = co_recreation['FEATTYPE'].value_counts()
ax2.bar(range(len(type_counts)), type_counts.values)
ax2.set_xticks(range(len(type_counts)))
ax2.set_xticklabels(type_counts.index, rotation=45, ha='right')
ax2.set_ylabel('Number of Areas')
ax2.set_title('Count by Recreational Area Type')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\n{'='*60}")
print(f"Analysis complete!")
```
