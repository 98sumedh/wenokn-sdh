---
name: lakes
description: Retrieve lakes, ponds, and water bodies in the USA using USGS National Hydrography Dataset via HyRiver. Query by name, location, buffer distance, or region boundary.
---

# Lakes Skill

## Description

This skill retrieves locations and attributes of lakes, ponds, and other water bodies in the United States by querying the USGS National Hydrography Dataset (NHD) through the HyRiver/PyNHD library.

**Data Source:**
- USGS National Hydrography Dataset (NHD) High Resolution
- Accessed via HyRiver Python package (`pynhd`)
- Coverage: Nationwide (all US states and territories)
- Resolution: High-resolution (1:24,000 scale)

**Water Body Types Available:**
- Lakes
- Ponds
- Reservoirs
- Playas (dry lake beds)
- Swamps/Marshes

The service returns the following key attributes:

- **gnis_name**: Geographic Names Information System name (official name)
- **ftype**: Feature type (e.g., "LakePond", "Reservoir", "Playa", "SwampMarsh")
- **fcode**: Feature code (numeric classification)
- **areasqkm**: Surface area in square kilometers
- **elevation**: Elevation in meters above sea level
- **reachcode**: Unique reach identifier for hydrologic connectivity
- **permanent_identifier**: Permanent feature identifier
- **geometry**: Polygon geometry of the water body

## When to Use

Use this skill to:

- Find a specific lake by name
- Find all lakes within a buffer distance of a location
- Find all lakes in a county, state, or custom region
- Find lakes within a national park or other boundary
- Find large lakes (by area threshold)
- Analyze water body distribution
- Get lakes for hydrologic analysis

## How to Use

### Step 1: Install and Import Required Libraries

```python
# Install HyRiver if not already installed
# pip install pynhd geopandas shapely

from pynhd import NHD
from shapely.geometry import Point, box
import geopandas as gpd
```

### Step 2: Define Query Functions

```python
def get_lakes_by_name(name, state=None):
    """
    Find lakes by name using GNIS name search.
    
    Parameters:
    -----------
    name : str
        Lake name or partial name to search for
    state : str, optional
        State abbreviation to narrow search (e.g., "CO", "CA")
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing matching lakes
    
    Example:
    --------
    # Find Lake Tahoe
    tahoe = get_lakes_by_name("Tahoe")
    
    # Find all lakes with "Blue" in the name in Colorado
    blue_lakes = get_lakes_by_name("Blue", state="CO")
    """
    # Create NHD waterbody layer
    nhd = NHD("waterbody_hr")
    
    # For name search, we need to query a broad area first, then filter
    # If state provided, use state bounds; otherwise use continental US
    if state:
        # Get state bounding box (you may need to define these or import from another source)
        state_bounds = get_state_bbox(state)
        geom = box(*state_bounds)
    else:
        # Continental US bounds
        geom = box(-125.0, 24.0, -66.0, 50.0)
    
    # Query water bodies
    water_bodies = nhd.bygeom(geom)
    
    if len(water_bodies) == 0:
        return gpd.GeoDataFrame()
    
    # Filter by name (case-insensitive partial match)
    if 'gnis_name' in water_bodies.columns:
        mask = water_bodies['gnis_name'].str.contains(name, case=False, na=False)
        lakes = water_bodies[mask]
    else:
        lakes = gpd.GeoDataFrame()
    
    return lakes

def get_lakes_by_buffer(point, radius_miles):
    """
    Find all lakes within a buffer distance of a point.
    
    Parameters:
    -----------
    point : tuple or shapely.geometry.Point
        Center point as (longitude, latitude) or Point object
    radius_miles : float
        Buffer radius in miles
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing lakes within the buffer
    
    Example:
    --------
    # Find all lakes within 20 miles of Boulder, CO
    boulder = (-105.2705, 40.0150)
    lakes = get_lakes_by_buffer(boulder, radius_miles=20)
    """
    # Create NHD waterbody layer
    nhd = NHD("waterbody_hr")
    
    # Convert tuple to Point if needed
    if isinstance(point, tuple):
        point = Point(point[0], point[1])
    
    # Create buffer (convert miles to degrees - approximate)
    # 1 degree ≈ 69 miles at mid-latitudes
    radius_degrees = radius_miles / 69.0
    buffer_geom = point.buffer(radius_degrees)
    
    # Query water bodies
    lakes = nhd.bygeom(buffer_geom)
    
    return lakes

def get_lakes_in_region(region_gdf):
    """
    Find all lakes within a region defined by a GeoDataFrame.
    
    Parameters:
    -----------
    region_gdf : geopandas.GeoDataFrame
        GeoDataFrame defining the region boundary (e.g., county, park, state)
        Must contain geometry column with polygon(s)
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing lakes within the region
    
    Example:
    --------
    # Find all lakes in Rocky Mountain National Park
    # (assuming you have park_boundary as a GeoDataFrame)
    lakes = get_lakes_in_region(park_boundary)
    
    # Find all lakes in Boulder County
    lakes = get_lakes_in_region(boulder_county_gdf)
    """
    # Create NHD waterbody layer
    nhd = NHD("waterbody_hr")
    
    # Get the geometry (union if multiple polygons)
    region_geom = region_gdf.unary_union
    
    # Query water bodies
    lakes = nhd.bygeom(region_geom)
    
    # Optionally clip to exact boundary
    if len(lakes) > 0:
        lakes = gpd.clip(lakes, region_gdf)
    
    return lakes

def get_lakes_by_bbox(bbox, min_area_sqkm=None):
    """
    Find all lakes within a bounding box.
    
    Parameters:
    -----------
    bbox : tuple or list
        Bounding box as (minx, miny, maxx, maxy) in WGS84 (longitude, latitude)
    min_area_sqkm : float, optional
        Minimum area in square kilometers to filter results
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing lakes within the bounding box
    
    Example:
    --------
    # Find all lakes in Colorado
    colorado_bbox = (-109.06, 36.99, -102.04, 41.00)
    lakes = get_lakes_by_bbox(colorado_bbox)
    
    # Find large lakes (>1 sq km) in California
    california_bbox = (-124.48, 32.53, -114.13, 42.01)
    large_lakes = get_lakes_by_bbox(california_bbox, min_area_sqkm=1.0)
    """
    # Create NHD waterbody layer
    nhd = NHD("waterbody_hr")
    
    # Create box geometry
    bbox_geom = box(*bbox)
    
    # Query water bodies
    lakes = nhd.bygeom(bbox_geom)
    
    # Filter by minimum area if specified
    if min_area_sqkm and len(lakes) > 0 and 'areasqkm' in lakes.columns:
        lakes = lakes[lakes['areasqkm'] >= min_area_sqkm]
    
    return lakes

# Helper function for state bounding boxes
def get_state_bbox(state_abbr):
    """
    Get bounding box for a state.
    
    Returns approximate bounding boxes for US states.
    """
    state_bboxes = {
        'CO': (-109.06, 36.99, -102.04, 41.00),
        'CA': (-124.48, 32.53, -114.13, 42.01),
        'WY': (-111.06, 40.99, -104.05, 45.01),
        'MT': (-116.05, 44.35, -104.04, 49.00),
        'UT': (-114.05, 36.99, -109.04, 42.00),
        'NV': (-120.01, 35.00, -114.04, 42.00),
        'AZ': (-114.82, 31.33, -109.05, 37.00),
        'NM': (-109.05, 31.33, -103.00, 37.00),
        'WA': (-124.85, 45.54, -116.92, 49.05),
        'OR': (-124.56, 41.99, -116.46, 46.29),
        'ID': (-117.24, 41.99, -111.04, 49.00),
        'AK': (-180.0, 51.0, -129.0, 72.0),
        'HI': (-160.0, 18.9, -154.8, 22.3),
    }
    return state_bboxes.get(state_abbr.upper(), (-125.0, 24.0, -66.0, 50.0))
```

### Step 3: Query Examples

#### Example 1: Find a Lake by Name

```python
# Find Lake Tahoe
tahoe = get_lakes_by_name("Tahoe")

if len(tahoe) > 0:
    lake = tahoe.iloc[0]
    print(f"Lake: {lake['gnis_name']}")
    print(f"Area: {lake['areasqkm']:.2f} sq km")
    print(f"Elevation: {lake['elevation']:.0f} m")
else:
    print("Lake not found")

# Find all lakes with "Blue" in name in Colorado
blue_lakes = get_lakes_by_name("Blue", state="CO")
print(f"\nFound {len(blue_lakes)} lakes with 'Blue' in the name in Colorado")
for idx, row in blue_lakes.head(10).iterrows():
    print(f"  - {row['gnis_name']}: {row['areasqkm']:.2f} sq km")
```

#### Example 2: Find All Lakes Within Buffer Distance

```python
# Find all lakes within 20 miles of Boulder, CO
boulder_coords = (-105.2705, 40.0150)
lakes_near_boulder = get_lakes_by_buffer(boulder_coords, radius_miles=20)

print(f"Found {len(lakes_near_boulder)} lakes within 20 miles of Boulder")

# Show largest lakes
if len(lakes_near_boulder) > 0:
    print("\nLargest lakes:")
    largest = lakes_near_boulder.nlargest(5, 'areasqkm')
    for idx, row in largest.iterrows():
        name = row.get('gnis_name', 'Unnamed')
        area = row.get('areasqkm', 0)
        print(f"  {name}: {area:.2f} sq km")
```

#### Example 3: Find All Lakes in a State

```python
# Find all lakes in Colorado
colorado_bbox = (-109.06, 36.99, -102.04, 41.00)
co_lakes = get_lakes_by_bbox(colorado_bbox)

print(f"Found {len(co_lakes)} water bodies in Colorado")

# Filter to only named lakes
if 'gnis_name' in co_lakes.columns:
    named_lakes = co_lakes[co_lakes['gnis_name'].notna()]
    print(f"  {len(named_lakes)} are named lakes")

# Get large lakes (>1 sq km)
large_lakes = co_lakes[co_lakes['areasqkm'] > 1.0]
print(f"  {len(large_lakes)} are larger than 1 sq km")
```

#### Example 4: Find Lakes in a National Park or Region

```python
# This example assumes you have a park boundary from the national-parks SKILL
# Example: Get Rocky Mountain National Park boundary
# park_boundary = get_park_by_name("Rocky Mountain")

# For demonstration, create a sample region (Rocky Mountain NP approximate area)
rmnp_bbox = (-105.95, 40.15, -105.50, 40.55)
rmnp_region = gpd.GeoDataFrame(
    geometry=[box(*rmnp_bbox)],
    crs="EPSG:4326"
)

# Find all lakes in the region
rmnp_lakes = get_lakes_in_region(rmnp_region)

print(f"Found {len(rmnp_lakes)} lakes in Rocky Mountain National Park")

# List named lakes
if len(rmnp_lakes) > 0:
    named = rmnp_lakes[rmnp_lakes['gnis_name'].notna()]
    print(f"\nNamed lakes in RMNP:")
    for idx, row in named.iterrows():
        print(f"  - {row['gnis_name']}: {row['areasqkm']:.3f} sq km")
```

#### Example 5: Find Large Lakes in a Region

```python
# Find lakes larger than 5 sq km in California
california_bbox = (-124.48, 32.53, -114.13, 42.01)
large_ca_lakes = get_lakes_by_bbox(california_bbox, min_area_sqkm=5.0)

print(f"Found {len(large_ca_lakes)} lakes larger than 5 sq km in California")

# Sort by size
if len(large_ca_lakes) > 0:
    print("\nTop 10 largest lakes in California:")
    top10 = large_ca_lakes.nlargest(10, 'areasqkm')
    for idx, row in top10.iterrows():
        name = row.get('gnis_name', 'Unnamed')
        area = row['areasqkm']
        elev = row.get('elevation', 'N/A')
        print(f"  {name}: {area:.2f} sq km, elevation: {elev} m")
```

#### Example 6: Find Lakes in a County

```python
# This example assumes you have county boundary data
# You can get this from Census TIGER/Line data

# For demonstration, approximate Boulder County, CO
boulder_county_bbox = (-105.72, 39.90, -105.17, 40.30)
boulder_county = gpd.GeoDataFrame(
    geometry=[box(*boulder_county_bbox)],
    crs="EPSG:4326"
)

# Find all lakes in Boulder County
boulder_lakes = get_lakes_in_region(boulder_county)

print(f"Found {len(boulder_lakes)} water bodies in Boulder County")

# Analyze by type
if len(boulder_lakes) > 0 and 'ftype' in boulder_lakes.columns:
    print("\nBreakdown by type:")
    type_counts = boulder_lakes['ftype'].value_counts()
    for ftype, count in type_counts.items():
        print(f"  {ftype}: {count}")
```

#### Example 7: Find Reservoirs vs Natural Lakes

```python
# Find water bodies in a region and distinguish types
region_bbox = (-105.5, 39.5, -104.5, 40.5)
water_bodies = get_lakes_by_bbox(region_bbox)

if len(water_bodies) > 0 and 'ftype' in water_bodies.columns:
    # Separate natural lakes from reservoirs
    natural_lakes = water_bodies[water_bodies['ftype'] == 'LakePond']
    reservoirs = water_bodies[water_bodies['ftype'] == 'Reservoir']
    
    print(f"Natural lakes: {len(natural_lakes)}")
    print(f"Reservoirs: {len(reservoirs)}")
    
    print("\nLargest natural lakes:")
    if len(natural_lakes) > 0:
        for idx, row in natural_lakes.nlargest(5, 'areasqkm').iterrows():
            name = row.get('gnis_name', 'Unnamed')
            print(f"  {name}: {row['areasqkm']:.2f} sq km")
```

#### Example 8: Analyze Lake Distribution

```python
# Get all lakes in Wyoming
wyoming_bbox = (-111.06, 40.99, -104.05, 45.01)
wy_lakes = get_lakes_by_bbox(wyoming_bbox)

print(f"LAKE ANALYSIS FOR WYOMING")
print("="*50)
print(f"\nTotal water bodies: {len(wy_lakes)}")

if len(wy_lakes) > 0:
    # Size distribution
    print(f"\nSize distribution:")
    small = len(wy_lakes[wy_lakes['areasqkm'] < 0.1])
    medium = len(wy_lakes[(wy_lakes['areasqkm'] >= 0.1) & (wy_lakes['areasqkm'] < 1.0)])
    large = len(wy_lakes[wy_lakes['areasqkm'] >= 1.0])
    
    print(f"  Small (<0.1 sq km): {small}")
    print(f"  Medium (0.1-1 sq km): {medium}")
    print(f"  Large (>1 sq km): {large}")
    
    # Total surface water area
    total_area = wy_lakes['areasqkm'].sum()
    print(f"\nTotal lake surface area: {total_area:.2f} sq km")
    
    # Elevation range
    if 'elevation' in wy_lakes.columns:
        elevations = wy_lakes['elevation'].dropna()
        if len(elevations) > 0:
            print(f"\nElevation range:")
            print(f"  Lowest: {elevations.min():.0f} m")
            print(f"  Highest: {elevations.max():.0f} m")
            print(f"  Average: {elevations.mean():.0f} m")
```

## Notes

HyRiver/PyGeoHydro queries the USGS National Hydrography Dataset (NHD), which is the authoritative source for surface water data in the United States.

### Understanding Water Body Types (ftype)

The NHD classifies water bodies into several types:

- **LakePond**: Natural lakes and ponds
- **Reservoir**: Man-made impoundments
- **Playa**: Dry lake beds (intermittent water)
- **SwampMarsh**: Wetlands, swamps, marshes
- **Estuary**: Coastal estuaries

**Query pattern:**
```python
# Filter to specific type
natural_lakes = water_bodies[water_bodies['ftype'] == 'LakePond']
reservoirs = water_bodies[water_bodies['ftype'] == 'Reservoir']
```

### Working with Lake Names

**Important**: Not all water bodies have official names (gnis_name may be null).

```python
# Filter to named lakes only
named_lakes = lakes[lakes['gnis_name'].notna()]

# Count named vs unnamed
named_count = lakes['gnis_name'].notna().sum()
unnamed_count = lakes['gnis_name'].isna().sum()
print(f"Named: {named_count}, Unnamed: {unnamed_count}")
```

### Performance Tips

1. **Use smaller query areas** when possible - querying entire large states can be slow
2. **Filter by area threshold** to reduce result size for large queries
3. **Cache results** if querying the same area multiple times
4. **Use specific regions** (GeoDataFrame boundaries) rather than large bounding boxes when possible

### Area and Distance Conversions

```python
# Convert square kilometers to acres
acres = sqkm * 247.105

# Convert square kilometers to square miles
sq_miles = sqkm * 0.386102

# Miles to degrees (approximate at mid-latitudes)
degrees = miles / 69.0

# More accurate buffer (using pyproj for actual distance)
from pyproj import Geod
geod = Geod(ellps='WGS84')
```

### Integration with Other SKILL.md Files

This lakes skill works well with:

**national-parks SKILL:**
```python
# Get park boundary
park = get_park_by_name("Yellowstone")
# Find lakes in park
lakes = get_lakes_in_region(park)
```

**watersheds SKILL:**
```python
# Get watershed boundary
watershed = get_watershed_by_huc("14010001")
# Find lakes in watershed
lakes = get_lakes_in_region(watershed)
```

**mountain-peaks SKILL:**
```python
# Find peaks near a lake
lake = get_lakes_by_name("Grand Lake", state="CO")
lake_center = lake.geometry.iloc[0].centroid
nearby_peaks = get_peaks_by_buffer(lake_center, radius_miles=10)
```

### Complete Example: Comprehensive Lake Analysis

```python
from pynhd import NHD
from shapely.geometry import Point, box
import geopandas as gpd
import matplotlib.pyplot as plt

# Function definitions (as above - included in the skill)
# [Include all the function definitions here]

# Analyze lakes in Rocky Mountain region
region_bbox = (-109.0, 39.0, -105.0, 41.5)
lakes = get_lakes_by_bbox(region_bbox)

print(f"ROCKY MOUNTAIN REGION LAKE ANALYSIS")
print("="*60)
print(f"\nTotal water bodies: {len(lakes)}")

# Filter to lakes only (exclude reservoirs)
if 'ftype' in lakes.columns:
    natural_lakes = lakes[lakes['ftype'] == 'LakePond']
    print(f"Natural lakes: {len(natural_lakes)}")
    
    reservoirs = lakes[lakes['ftype'] == 'Reservoir']
    print(f"Reservoirs: {len(reservoirs)}")

# Named vs unnamed
if 'gnis_name' in lakes.columns:
    named = lakes[lakes['gnis_name'].notna()]
    print(f"Named lakes: {len(named)}")

# Size analysis
print(f"\nSize distribution:")
if 'areasqkm' in lakes.columns:
    size_categories = {
        'Very small (<0.01 sq km)': len(lakes[lakes['areasqkm'] < 0.01]),
        'Small (0.01-0.1 sq km)': len(lakes[(lakes['areasqkm'] >= 0.01) & (lakes['areasqkm'] < 0.1)]),
        'Medium (0.1-1 sq km)': len(lakes[(lakes['areasqkm'] >= 0.1) & (lakes['areasqkm'] < 1.0)]),
        'Large (1-10 sq km)': len(lakes[(lakes['areasqkm'] >= 1.0) & (lakes['areasqkm'] < 10.0)]),
        'Very large (>10 sq km)': len(lakes[lakes['areasqkm'] >= 10.0])
    }
    
    for category, count in size_categories.items():
        print(f"  {category}: {count}")
    
    # Total surface area
    total_area_sqkm = lakes['areasqkm'].sum()
    total_area_sqmi = total_area_sqkm * 0.386102
    print(f"\nTotal lake surface area:")
    print(f"  {total_area_sqkm:.2f} sq km")
    print(f"  {total_area_sqmi:.2f} sq miles")

# Top 10 largest
print(f"\nTop 10 largest lakes:")
if len(lakes) > 0:
    top10 = lakes.nlargest(10, 'areasqkm')
    for idx, row in top10.iterrows():
        name = row.get('gnis_name', 'Unnamed')
        area_sqkm = row['areasqkm']
        area_sqmi = area_sqkm * 0.386102
        elev = row.get('elevation', 'N/A')
        print(f"  {name}: {area_sqkm:.2f} sq km ({area_sqmi:.2f} sq mi), elev: {elev} m")

# Elevation analysis
if 'elevation' in lakes.columns:
    elevations = lakes['elevation'].dropna()
    if len(elevations) > 0:
        print(f"\nElevation statistics:")
        print(f"  Lowest: {elevations.min():.0f} m ({elevations.min() * 3.28084:.0f} ft)")
        print(f"  Highest: {elevations.max():.0f} m ({elevations.max() * 3.28084:.0f} ft)")
        print(f"  Average: {elevations.mean():.0f} m ({elevations.mean() * 3.28084:.0f} ft)")

# Plot lakes
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Map colored by size
if len(lakes) > 0:
    lakes.plot(ax=ax1, column='areasqkm', cmap='Blues', 
               legend=True, alpha=0.7,
               legend_kwds={'label': 'Area (sq km)'})
    ax1.set_title('Lakes in Rocky Mountain Region by Size')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')

# Size distribution histogram
if 'areasqkm' in lakes.columns:
    # Log scale for better visualization
    ax2.hist(lakes['areasqkm'], bins=50, edgecolor='black', alpha=0.7)
    ax2.set_xlabel('Area (sq km)')
    ax2.set_ylabel('Number of Lakes')
    ax2.set_title('Lake Size Distribution')
    ax2.set_yscale('log')
    ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\n{'='*60}")
print("Analysis complete!")
```
