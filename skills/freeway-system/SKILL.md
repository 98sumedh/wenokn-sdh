---
name: freeway-system
description: Retrieve USA freeway and highway segments including interstates, US highways, and state/county roads. Query by route number, highway class, or location. Returns line geometries with segment lengths in miles and kilometers.
---

# USA Freeway System Skill

## Description

This skill retrieves highway and freeway segment data for the United States by accessing the ArcGIS Feature Service at the following URL:

```
https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Freeway_System/FeatureServer/2
```

**Service Details:**
- Maximum record count: 1000
- Spatial reference: WGS84 (EPSG:4326) - no transformation needed
- Geometry type: Polyline (road segments)
- Coverage: Contiguous United States

The service returns the following key fields:

**Route Identification:**
- **ROUTE_NUM**: Full route number string (e.g., "I- 25", "US-36") — may contain spaces after the dash
- **CLASS**: Single-character highway class code (see CLASS codes below)
- **NUMBER**: Numeric portion of the route only (e.g., "25", "70", "36") — preferred for route number searches
- **SUFFIX**: Route suffix for directional or business variants (e.g., "E", "W", "N", "S", "B")

**Distance:**
- **DIST_MILES**: Segment length in miles
- **DIST_KM**: Segment length in kilometers

## CRITICAL: CLASS Field Codes

**CLASS is a single-character code, not a text label.** Use the following codes in WHERE clauses:

| CLASS | Highway Type |
|-------|-------------|
| **I** | Interstate Highway (e.g., I-25, I-70, I-80) |
| **O** | Interstate — alternate/business loop |
| **U** | US Highway (e.g., US-36, US-40, US-285) |
| **S** | State Highway (e.g., CO-93, CA-1, TX-71) |
| **C** | State/County Highway |
| **N** | State/County Highway — alternate |

## CRITICAL: ROUTE_NUM Format

**ROUTE_NUM may contain spaces after the dash** (e.g., `"I- 25"` not `"I-25"`). Always use the NUMBER field for numeric route searches, or use LIKE with % wildcards on ROUTE_NUM.

```python
# CORRECT — use NUMBER field for numeric searches
where = "NUMBER = '70' AND CLASS = 'I'"

# CORRECT — LIKE handles spacing variations in ROUTE_NUM
where = "ROUTE_NUM LIKE '%70%' AND CLASS = 'I'"

# INCORRECT — exact match on ROUTE_NUM will fail due to spacing
where = "ROUTE_NUM = 'I-70'"
```

## IMPORTANT: Segments, Not Whole Routes

Each record represents a single road **segment**, not a complete route. A highway like I-25 consists of hundreds of individual segment records. Always use `DIST_MILES.sum()` to calculate total route length.

## When to Use

Use this skill to:

- Find all highway segments in a state or region
- Find a specific route by number (e.g., I-70, US-36)
- Calculate total highway miles in an area
- Find interstates, US highways, or state roads by class
- Analyze highway network coverage
- Find road segments near a specific location

## How to Use

### Step 1: Import Required Libraries

```python
import requests
import pandas as pd
import geopandas as gpd
```

### Step 2: Define the Query Function

**CRITICAL**: This function automatically handles pagination to retrieve ALL results, even when more than 1000 records match your query.

```python
def get_highways(where_clause, bbox=None):
    """
    Query the ArcGIS Feature Service for highway segments.

    AUTOMATICALLY HANDLES PAGINATION - retrieves all results even if >1000.

    Parameters:
    -----------
    where_clause : str
        SQL-like WHERE clause to filter features (e.g., "CLASS = 'I'")
    bbox : list, optional
        Bounding box as [minx, miny, maxx, maxy] in WGS84 (EPSG:4326)
        Default is continental USA bounds

    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing ALL queried highway segment features with geometry
    """
    url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Freeway_System/FeatureServer/2"

    if bbox is None:
        bbox = [-125.0, 24.396308, -66.93457, 49.384358]

    minx, miny, maxx, maxy = bbox

    all_features = []
    offset = 0
    batch_size = 1000

    while True:
        params = {
            "where": where_clause,
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


def get_highways_in_region(where_clause, region_gdf):
    """
    Query highway segments and clip results to an exact region boundary.

    USE THIS FUNCTION when the user asks for highways "in" a specific region
    (state, county, park, or any polygon boundary provided as a GeoDataFrame).

    IMPORTANT: A simple bbox query is NOT sufficient — highway segments cross
    state/region boundaries and bbox returns complete segments extending beyond
    the region. This function clips geometries precisely to the boundary.

    Parameters:
    -----------
    where_clause : str
        SQL-like WHERE clause to filter features (e.g., "CLASS = 'I'")
    region_gdf : geopandas.GeoDataFrame
        GeoDataFrame defining the region boundary (e.g., a state or county polygon)
        Must be in EPSG:4326 or will be reprojected automatically

    Returns:
    --------
    geopandas.GeoDataFrame
        Highway segments clipped precisely to the region boundary, in EPSG:4326

    Example:
    --------
    # Find I-80 within California boundary
    california_gdf = gpd.read_file("california.geojson")
    i80_in_ca = get_highways_in_region("NUMBER = '80' AND CLASS = 'I'", california_gdf)
    """
    # Ensure region is in EPSG:4326
    if region_gdf.crs is None:
        region_gdf = region_gdf.set_crs("EPSG:4326")
    elif region_gdf.crs.to_epsg() != 4326:
        region_gdf = region_gdf.to_crs("EPSG:4326")

    # Get bounding box of region to limit server-side query
    bounds = region_gdf.total_bounds  # [minx, miny, maxx, maxy]
    bbox = [bounds[0], bounds[1], bounds[2], bounds[3]]

    # Query using bbox (fast, server-side)
    highways = get_highways(where_clause, bbox=bbox)

    if len(highways) == 0:
        return highways

    # Clip precisely to region boundary (removes segments outside the region)
    highways_clipped = gpd.clip(highways, region_gdf)

    return highways_clipped
```

### Step 3: Query Examples

#### Example 1: Find I-80 Within California (Region Clipping)

```python
# WHEN USER ASKS FOR A HIGHWAY "IN" A STATE OR REGION:
# MUST use get_highways_in_region() — bbox alone returns segments
# crossing into Nevada, Oregon, etc.

# California boundary provided as a GeoDataFrame
# california_gdf = gpd.read_file("california.geojson")  # or from another skill

# Find I-80 clipped precisely to California
where_clause = "NUMBER = '80' AND CLASS = 'I'"
i80_california = get_highways_in_region(where_clause, california_gdf)

print(f"Found {len(i80_california)} I-80 segments within California")
print(f"Total I-80 length in California: {i80_california['DIST_MILES'].sum():.1f} miles")
```

#### Example 2: Find All Interstates in a State (with clipping)

```python
# Find all interstate segments clipped to California
where_clause = "CLASS IN ('I', 'O')"
ca_interstates = get_highways_in_region(where_clause, california_gdf)

print(f"Found {len(ca_interstates)} interstate segments in California")
print(f"Total interstate miles: {ca_interstates['DIST_MILES'].sum():.1f}")

# List unique routes
routes = sorted(ca_interstates['ROUTE_NUM'].dropna().unique())
print(f"Interstate routes: {routes}")
```

#### Example 3: Find All Highways in a State (with clipping)

```python
# Find all highway types clipped to California
where_clause = "1=1"
ca_highways = get_highways_in_region(where_clause, california_gdf)

print(f"Found {len(ca_highways)} highway segments in California")

class_labels = {
    'I': 'Interstate', 'O': 'Interstate (alt)',
    'U': 'US Highway',  'S': 'State Highway',
    'C': 'County Road',  'N': 'State/County (alt)'
}
print("\nBreakdown by highway type:")
for cls, count in ca_highways['CLASS'].value_counts().items():
    miles = ca_highways[ca_highways['CLASS'] == cls]['DIST_MILES'].sum()
    print(f"  {class_labels.get(cls, cls)}: {count} segments, {miles:.1f} miles")
```

#### Example 4: Find a Specific Route (without region boundary)

```python
# Find all segments of I-70 nationwide
where_clause = "NUMBER = '70' AND CLASS = 'I'"
i70 = get_highways(where_clause)

print(f"Found {len(i70)} segments of I-70")
print(f"Total length: {i70['DIST_MILES'].sum():.1f} miles")
```

#### Example 5: Find All Highways in a Bounding Box Region

```python
# Find all highway types in the Denver metro area (no clipping needed)
denver_bbox = [-105.4, 39.5, -104.5, 40.2]
where_clause = "1=1"
denver_highways = get_highways(where_clause, bbox=denver_bbox)

print(f"Found {len(denver_highways)} highway segments in Denver area")

class_labels = {
    'I': 'Interstate', 'O': 'Interstate (alt)',
    'U': 'US Highway',  'S': 'State Highway',
    'C': 'County Road',  'N': 'State/County (alt)'
}
print("\nBreakdown by highway type:")
for cls, count in denver_highways['CLASS'].value_counts().items():
    miles = denver_highways[denver_highways['CLASS'] == cls]['DIST_MILES'].sum()
    print(f"  {class_labels.get(cls, cls)}: {count} segments, {miles:.1f} miles")
```

#### Example 6: Find US Highways by Number

```python
# Find US-101 clipped to California
where_clause = "NUMBER = '101' AND CLASS = 'U'"
us101_ca = get_highways_in_region(where_clause, california_gdf)

print(f"Found {len(us101_ca)} segments of US-101 in California")
print(f"Total length: {us101_ca['DIST_MILES'].sum():.1f} miles")
```

#### Example 7: Find State Highways in a Region

```python
# Find state highways in New Mexico (using bbox)
nm_bbox = [-109.05, 31.33, -103.00, 37.00]
where_clause = "CLASS = 'S'"
nm_state_hwy = get_highways(where_clause, bbox=nm_bbox)

print(f"Found {len(nm_state_hwy)} state highway segments in New Mexico")
print(f"Total state highway miles: {nm_state_hwy['DIST_MILES'].sum():.1f}")
```

#### Example 8: Find Directional Route Splits

```python
# Find directional variants of I-80 in California (e.g., I-80E, I-80W)
where_clause = "NUMBER = '80' AND CLASS IN ('I', 'O') AND SUFFIX IS NOT NULL"
i80_splits = get_highways_in_region(where_clause, california_gdf)

if len(i80_splits) > 0:
    print(f"Found {len(i80_splits)} directional segments of I-80 in California")
    print(f"Suffixes: {i80_splits['SUFFIX'].unique()}")
else:
    print("No directional splits found for I-80 in California")
```

```python
# Find all interstate segments in Colorado
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]
where_clause = "CLASS IN ('I', 'O')"
co_interstates = get_highways(where_clause, bbox=colorado_bbox)

print(f"Found {len(co_interstates)} interstate segments in Colorado")
print(f"Total interstate miles: {co_interstates['DIST_MILES'].sum():.1f}")

# List unique routes
routes = sorted(co_interstates['ROUTE_NUM'].dropna().unique())
print(f"Interstate routes: {routes}")
```

#### Example 2: Find a Specific Route

```python
# Find all segments of I-70
where_clause = "NUMBER = '70' AND CLASS = 'I'"
i70 = get_highways(where_clause)

print(f"Found {len(i70)} segments of I-70")
print(f"Total length: {i70['DIST_MILES'].sum():.1f} miles")
```

#### Example 3: Find All Highways in a Region

```python
# Find all highway types in the Denver metro area
denver_bbox = [-105.4, 39.5, -104.5, 40.2]
where_clause = "1=1"
denver_highways = get_highways(where_clause, bbox=denver_bbox)

print(f"Found {len(denver_highways)} highway segments in Denver area")

# Breakdown by class
class_labels = {
    'I': 'Interstate', 'O': 'Interstate (alt)',
    'U': 'US Highway',  'S': 'State Highway',
    'C': 'County Road',  'N': 'State/County (alt)'
}
print("\nBreakdown by highway type:")
for cls, count in denver_highways['CLASS'].value_counts().items():
    miles = denver_highways[denver_highways['CLASS'] == cls]['DIST_MILES'].sum()
    print(f"  {class_labels.get(cls, cls)}: {count} segments, {miles:.1f} miles")
```

#### Example 4: Find US Highways by Number

```python
# Find US-101 on the West Coast
west_coast_bbox = [-124.5, 32.5, -117.0, 49.0]
where_clause = "NUMBER = '101' AND CLASS = 'U'"
us101 = get_highways(where_clause, bbox=west_coast_bbox)

print(f"Found {len(us101)} segments of US-101")
print(f"Total length: {us101['DIST_MILES'].sum():.1f} miles")
```

#### Example 5: Find State Highways in a Region

```python
# Find state highways in New Mexico
nm_bbox = [-109.05, 31.33, -103.00, 37.00]
where_clause = "CLASS = 'S'"
nm_state_hwy = get_highways(where_clause, bbox=nm_bbox)

print(f"Found {len(nm_state_hwy)} state highway segments in New Mexico")
print(f"Total state highway miles: {nm_state_hwy['DIST_MILES'].sum():.1f}")
```

#### Example 6: Find All Major Highways Near a Location

```python
# Find interstates and US highways within ~15 miles of Kansas City, MO
# (~15 miles ≈ 0.22 degrees)
kc_bbox = [-94.8, 38.9, -94.3, 39.4]
where_clause = "CLASS IN ('I', 'O', 'U')"
kc_major = get_highways(where_clause, bbox=kc_bbox)

print(f"Found {len(kc_major)} major highway segments near Kansas City")
routes = sorted(kc_major['ROUTE_NUM'].dropna().unique())
print(f"Routes: {routes}")
```

#### Example 7: Find Directional Route Splits

```python
# Find directional variants of I-80 (e.g., I-80E, I-80W)
where_clause = "NUMBER = '80' AND CLASS IN ('I', 'O') AND SUFFIX IS NOT NULL"
i80_splits = get_highways(where_clause)

if len(i80_splits) > 0:
    print(f"Found {len(i80_splits)} directional segments of I-80")
    print(f"Suffixes: {i80_splits['SUFFIX'].unique()}")
else:
    print("No directional splits found for I-80")
```

#### Example 8: Calculate Highway Miles by Class for a State

```python
# Analyze highway network composition in Texas
texas_bbox = [-106.65, 25.84, -93.51, 36.50]
where_clause = "1=1"
tx_highways = get_highways(where_clause, bbox=texas_bbox)

print(f"TEXAS HIGHWAY NETWORK")
print("=" * 40)
print(f"Total segments: {len(tx_highways)}")
print(f"Total highway miles: {tx_highways['DIST_MILES'].sum():.1f}\n")

class_labels = {
    'I': 'Interstate', 'O': 'Interstate (alt)',
    'U': 'US Highway',  'S': 'State Highway',
    'C': 'County Road',  'N': 'State/County (alt)'
}
print("By highway class:")
for cls in ['I', 'O', 'U', 'S', 'C', 'N']:
    subset = tx_highways[tx_highways['CLASS'] == cls]
    if len(subset) > 0:
        miles = subset['DIST_MILES'].sum()
        print(f"  {class_labels.get(cls, cls)}: {len(subset)} segments, {miles:.1f} miles")
```

## Notes

### When to Use Each Function

| Scenario | Function to Use |
|----------|----------------|
| "Find I-80 **in** California" | `get_highways_in_region()` — clips to boundary |
| "Find all interstates **in** Colorado" | `get_highways_in_region()` — clips to boundary |
| "Find I-70 nationwide" | `get_highways()` — no boundary needed |
| "Find highways near Denver" | `get_highways()` with bbox |
| "Find US-101 **in** Oregon" | `get_highways_in_region()` — clips to boundary |

**Rule of thumb:** If the user says "in [state/county/region]" and provides or implies a boundary polygon, use `get_highways_in_region()`. If the query is nationwide or uses a simple rectangular area, use `get_highways()` with bbox.

### Why Clipping Is Necessary

A bbox query for California will also return portions of I-80 in Nevada, portions of I-5 in Oregon, and other cross-border segments because the bounding box intersects those states. `get_highways_in_region()` uses `gpd.clip()` to cut segments precisely at the state boundary, returning only the geometry within California.

- `I` — Interstate Highway (main designation)
- `O` — Interstate alternate/business loop
- `U` — US Highway
- `S` — State Highway
- `C` — State/County Highway
- `N` — State/County Highway alternate

### SUFFIX Values

The SUFFIX field identifies directional or business route variants:
- `E`, `W`, `N`, `S` — Directional splits (e.g., I-80E, I-80W)
- `B` — Business route (e.g., I-25B)
- `A` — Alternate route

```python
# Exclude directional/business splits, main alignment only
where_clause = "NUMBER = '25' AND CLASS = 'I' AND (SUFFIX IS NULL OR SUFFIX = '')"
```

### WHERE Clause Tips

- Use single-character CLASS codes: `"CLASS = 'I'"` not `"CLASS = 'Interstate'"`
- Use NUMBER for route number searches: `"NUMBER = '70'"` not `"ROUTE_NUM = 'I-70'"`
- Use LIKE for ROUTE_NUM searches: `"ROUTE_NUM LIKE '%70%'"`
- Combine class variants: `"CLASS IN ('I', 'O')"` for all interstates
- Filter directional splits: `"SUFFIX IS NULL OR SUFFIX = ''"` for main alignment only
- Use `1=1` to match all features in a bbox
- Always sum DIST_MILES across segments: `gdf['DIST_MILES'].sum()`

### Common Bounding Boxes

```python
colorado_bbox    = [-109.06, 36.99, -102.04, 41.00]
california_bbox  = [-124.48, 32.53, -114.13, 42.01]
texas_bbox       = [-106.65, 25.84,  -93.51, 36.50]
new_york_bbox    = [ -79.76, 40.50,  -71.86, 45.01]
washington_bbox  = [-124.85, 45.54, -116.92, 49.05]
florida_bbox     = [ -87.63, 24.52,  -80.03, 31.00]
```

### Complete Example: Full Highway Network Analysis

```python
import requests
import pandas as pd
import geopandas as gpd

def get_highways(where_clause, bbox=None):
    url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Freeway_System/FeatureServer/2"

    if bbox is None:
        bbox = [-125.0, 24.396308, -66.93457, 49.384358]

    minx, miny, maxx, maxy = bbox
    all_features = []
    offset = 0
    batch_size = 1000

    while True:
        params = {
            "where": where_clause,
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


# Full network analysis for Colorado
colorado_bbox = [-109.06, 36.99, -102.04, 41.00]
highways = get_highways("1=1", bbox=colorado_bbox)

print(f"Colorado Highway Network Analysis\n{'='*40}")
print(f"Total segments : {len(highways)}")
print(f"Total miles    : {highways['DIST_MILES'].sum():.1f}")
print(f"Total km       : {highways['DIST_KM'].sum():.1f}\n")

class_labels = {
    'I': 'Interstate', 'O': 'Interstate (alt)',
    'U': 'US Highway',  'S': 'State Highway',
    'C': 'County Road',  'N': 'State/County (alt)'
}

print("By highway class:")
for cls in ['I', 'O', 'U', 'S', 'C', 'N']:
    subset = highways[highways['CLASS'] == cls]
    if len(subset) > 0:
        miles = subset['DIST_MILES'].sum()
        print(f"  {class_labels.get(cls, cls):25s}: {len(subset):4d} segments, {miles:7.1f} miles")

print("\nTop 10 longest individual segments:")
top10 = highways.nlargest(10, 'DIST_MILES')[['ROUTE_NUM', 'CLASS', 'DIST_MILES']]
for _, row in top10.iterrows():
    print(f"  {row['ROUTE_NUM']:10s} ({row['CLASS']}): {row['DIST_MILES']:.2f} miles")

print("\nInterstates present:")
interstates = highways[highways['CLASS'].isin(['I', 'O'])]
for route in sorted(interstates['ROUTE_NUM'].dropna().unique()):
    miles = interstates[interstates['ROUTE_NUM'] == route]['DIST_MILES'].sum()
    print(f"  {route}: {miles:.1f} miles")
```
