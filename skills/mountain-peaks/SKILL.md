---
name: mountain-peaks
description: Retrieve named mountain peaks and summits in the USA with elevations. Query by location, name, or minimum elevation. Returns point geometries with heights in meters.
---

# Mountain Peaks Skill

## Description

This skill retrieves locations, names, and elevations of mountain peaks and summits in the United States by accessing the ArcGIS Feature Service at the following URL:

```
https://services7.arcgis.com/hlgtGWqkM6RRz3r9/ArcGIS/rest/services/USA_Mountain_Peaks/FeatureServer/0
```

**Service Details:**
- Maximum record count: 2000
- Spatial reference: NAD83 UTM Zone 12N (EPSG:26912)
- Output spatial reference: WGS84 (EPSG:4326) - transformed automatically
- Data source: USGS Geographic Names Information System (GNIS)

The service returns the following columns:

- **OBJECTID**: System-assigned unique identifier
- **NAME**: Name of the mountain peak or summit
- **STCTYFIPS**: State and county FIPS code (5 digits)
- **ELEV_METER**: Elevation in meters above sea level

## When to Use

Use this skill to:

- Find all named peaks in a specific geographic area (state, county, park, etc.)
- Find peaks above a certain elevation
- Find peaks by name
- Get elevation data for mountain summits
- Identify the highest peaks in a region
- Answer queries like "What are the tallest mountains in [area]?"

## How to Use

### Step 1: Import Required Libraries

```python
import geopandas as gpd
import requests
```

### Step 2: Define the Query Function

**⚠️ IMPORTANT**: This service has a 2000 record limit. This function **automatically handles pagination** to retrieve ALL results.

```python
def get_features(service_url, where, bbox=None):
    """
    Query the ArcGIS Feature Service for mountain peaks.
    
    AUTOMATICALLY HANDLES PAGINATION - will retrieve all results even if >2000.
    
    Note: Service uses EPSG:26912 natively, but we request output in EPSG:4326.
    
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
        GeoDataFrame containing ALL queried mountain peak features in EPSG:4326
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
            "outSR": "4326",  # Request output in WGS84 (service native is EPSG:26912)
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

#### Example 1: Find All Peaks in a Region (e.g., Colorado Rockies)

```python
url = "https://services7.arcgis.com/hlgtGWqkM6RRz3r9/ArcGIS/rest/services/USA_Mountain_Peaks/FeatureServer/0"

# Colorado bounding box
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# Get all peaks in Colorado
where = "1=1"  # Get all peaks
co_peaks = get_features(url, where, bbox=colorado_bbox)

print(f"Found {len(co_peaks)} mountain peaks in Colorado")
print(co_peaks[['NAME', 'ELEV_METER']].head())
```

#### Example 2: Find High Elevation Peaks (14,000+ feet / 4267+ meters)

```python
# Colorado 14ers (peaks over 14,000 feet)
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# 14,000 feet = 4267 meters
where = "ELEV_METER >= 4267"
co_14ers = get_features(url, where, bbox=colorado_bbox)

print(f"Found {len(co_14ers)} Colorado 14ers")
print("\nColorado's highest peaks:")
print(co_14ers.nlargest(10, 'ELEV_METER')[['NAME', 'ELEV_METER']])
```

#### Example 3: Find Peaks by Name

```python
# Find all peaks with "Denali" in the name
where = "NAME LIKE '%Denali%'"
denali_peaks = get_features(url, where)

print(f"Found {len(denali_peaks)} peaks with 'Denali' in the name")
for idx, row in denali_peaks.iterrows():
    elev_ft = row['ELEV_METER'] * 3.28084
    print(f"  {row['NAME']}: {row['ELEV_METER']}m ({elev_ft:.0f}ft)")
```

#### Example 4: Find Peaks in a Specific Park Boundary

```python
# This example requires the national-parks SKILL to get park boundary
# Step 1: Get park boundary (using national-parks skill)
# park = get_park_by_name("Wrangell-St. Elias National Park and Preserve")

# Step 2: Get peaks in Alaska near the park
alaska_bbox = [-146.0, 59.0, -138.0, 63.0]  # Wrangell-St. Elias area
where = "1=1"
alaska_peaks = get_features(url, where, bbox=alaska_bbox)

# Step 3: Filter to peaks inside park boundary
# peaks_in_park = alaska_peaks[alaska_peaks.within(park.geometry.iloc[0])]

print(f"Found {len(alaska_peaks)} peaks in Wrangell-St. Elias area")
print("\nHighest peaks:")
print(alaska_peaks.nlargest(10, 'ELEV_METER')[['NAME', 'ELEV_METER']])
```

#### Example 5: Find Tallest Peaks in Each State

```python
# Note: This requires state boundary data to determine which peaks are in which state
# For demonstration, using bbox for individual states

# Find highest peak in Washington
washington_bbox = [-124.85, 45.54, -116.92, 49.05]
where = "1=1"
wa_peaks = get_features(url, where, bbox=washington_bbox)

if len(wa_peaks) > 0:
    highest = wa_peaks.loc[wa_peaks['ELEV_METER'].idxmax()]
    print(f"Highest peak in Washington:")
    print(f"  {highest['NAME']}: {highest['ELEV_METER']}m ({highest['ELEV_METER']*3.28084:.0f}ft)")
```

#### Example 6: Find Peaks Above a Specific Elevation in a Region

```python
# Find all peaks above 3000m in California
california_bbox = [-124.48, 32.53, -114.13, 42.01]
where = "ELEV_METER >= 3000"
ca_high_peaks = get_features(url, where, bbox=california_bbox)

print(f"Found {len(ca_high_peaks)} peaks above 3000m in California")
print(ca_high_peaks.nlargest(15, 'ELEV_METER')[['NAME', 'ELEV_METER']])
```

#### Example 7: Find Peaks with Specific Names

```python
# Find Mount Whitney
where = "NAME = 'Mount Whitney'"
whitney = get_features(url, where)

if len(whitney) > 0:
    elev_m = whitney.iloc[0]['ELEV_METER']
    elev_ft = elev_m * 3.28084
    print(f"Mount Whitney: {elev_m}m ({elev_ft:.0f}ft)")
```

#### Example 8: Find Prominent Peaks in Alaska

```python
# Alaska bounding box
alaska_bbox = [-180.0, 51.0, -129.0, 72.0]

# High peaks in Alaska (>5000m)
where = "ELEV_METER >= 5000"
ak_high_peaks = get_features(url, where, bbox=alaska_bbox)

print(f"Found {len(ak_high_peaks)} peaks above 5000m in Alaska")
print("\nAlaska's highest peaks:")
print(ak_high_peaks.nlargest(10, 'ELEV_METER')[['NAME', 'ELEV_METER']])
```

## Notes

The service contains mountain peaks and summits from the USGS Geographic Names Information System. Elevation data is provided in meters above sea level.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query
- **Use case**: Always provide a bbox when querying for peaks in a specific region

**Common State/Region Bounding Boxes**:
```python
# Colorado
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# California
california_bbox = [-124.48, 32.53, -114.13, 42.01]

# Alaska
alaska_bbox = [-180.0, 51.0, -129.0, 72.0]

# Washington
washington_bbox = [-124.85, 45.54, -116.92, 49.05]

# Wyoming (for Grand Tetons, Yellowstone)
wyoming_bbox = [-111.06, 40.99, -104.05, 45.01]

# Wrangell-St. Elias area (Alaska)
wrangell_bbox = [-146.0, 59.0, -138.0, 63.0]
```

### Using the ELEV_METER Field

Filter by elevation (all elevations are in **meters above sea level**):

**Common elevation thresholds**:
```python
# Colorado 14ers (14,000 feet = 4267 meters)
where = "ELEV_METER >= 4267"

# Very high peaks (>5000m / 16,404ft)
where = "ELEV_METER >= 5000"

# Moderate peaks (>3000m / 9,843ft)
where = "ELEV_METER >= 3000"

# Range query
where = "ELEV_METER BETWEEN 3000 AND 4000"
```

**Convert between meters and feet**:
```python
# Meters to feet
elevation_ft = elevation_m * 3.28084

# Feet to meters
elevation_m = elevation_ft / 3.28084
```

### Using the NAME Field

Filter by peak name:

**Exact match**:
```python
where = "NAME = 'Mount Rainier'"
where = "NAME = 'Denali'"
```

**Partial match**:
```python
# Find all peaks with "Whitney" in the name
where = "NAME LIKE '%Whitney%'"

# Find all peaks starting with "Mount"
where = "NAME LIKE 'Mount%'"

# Case-insensitive search (if supported)
where = "UPPER(NAME) LIKE UPPER('%rainier%')"
```

### WHERE Clause Tips

- **Get all peaks in a region**: Use `"1=1"` with bbox
- **Filter by elevation**: Use numeric comparisons
  - Example: `"ELEV_METER >= 4000"`
  - Example: `"ELEV_METER BETWEEN 3000 AND 5000"`
- **Find by name**: Use `LIKE` with `%` wildcards
  - Example: `"NAME LIKE '%Rainier%'"`
- **Combine conditions**: Use AND/OR
  - Example: `"ELEV_METER >= 4000 AND NAME LIKE '%Peak'"`
- Always enclose string values in single quotes
- Elevation is in **meters**, not feet

### Complete Example: Find and Analyze Peaks in a National Park

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

# Find and analyze peaks in Colorado
url = "https://services7.arcgis.com/hlgtGWqkM6RRz3r9/ArcGIS/rest/services/USA_Mountain_Peaks/FeatureServer/0"
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]

# Get all peaks
where = "1=1"
co_peaks = get_features(url, where, bbox=colorado_bbox)

print(f"MOUNTAIN PEAKS IN COLORADO")
print("="*60)
print(f"\nTotal peaks: {len(co_peaks)}")

# Elevation statistics
print(f"\nElevation statistics (meters):")
print(f"  Highest: {co_peaks['ELEV_METER'].max()}m ({co_peaks['ELEV_METER'].max()*3.28084:.0f}ft)")
print(f"  Lowest: {co_peaks['ELEV_METER'].min()}m ({co_peaks['ELEV_METER'].min()*3.28084:.0f}ft)")
print(f"  Average: {co_peaks['ELEV_METER'].mean():.0f}m ({co_peaks['ELEV_METER'].mean()*3.28084:.0f}ft)")

# 14ers (peaks over 14,000 feet / 4267 meters)
fourteeners = co_peaks[co_peaks['ELEV_METER'] >= 4267]
print(f"\nColorado 14ers (>14,000ft): {len(fourteeners)}")

# Top 10 highest peaks
print(f"\nTop 10 highest peaks:")
top10 = co_peaks.nlargest(10, 'ELEV_METER')[['NAME', 'ELEV_METER']]
for idx, row in top10.iterrows():
    elev_ft = row['ELEV_METER'] * 3.28084
    print(f"  {row['NAME']}: {row['ELEV_METER']}m ({elev_ft:.0f}ft)")

# Elevation distribution
bins = [0, 2000, 3000, 4000, 4267, 5000]
labels = ['<2000m', '2000-3000m', '3000-4000m', '4000-4267m (near 14ers)', '4267m+ (14ers+)']
co_peaks['elev_category'] = pd.cut(co_peaks['ELEV_METER'], bins=bins, labels=labels)

print(f"\nElevation distribution:")
print(co_peaks['elev_category'].value_counts().sort_index())

# Plot peaks by elevation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Map colored by elevation
co_peaks.plot(ax=ax1, column='ELEV_METER', cmap='terrain', 
              markersize=20, alpha=0.6, legend=True,
              legend_kwds={'label': 'Elevation (meters)'})
ax1.set_title('Colorado Mountain Peaks by Elevation')
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')

# Histogram
ax2.hist(co_peaks['ELEV_METER'], bins=50, edgecolor='black', alpha=0.7)
ax2.axvline(4267, color='red', linestyle='--', linewidth=2, label='14,000ft threshold')
ax2.set_xlabel('Elevation (meters)')
ax2.set_ylabel('Number of Peaks')
ax2.set_title('Distribution of Peak Elevations in Colorado')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\n{'='*60}")
print(f"Analysis complete!")
```
