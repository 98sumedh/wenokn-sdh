---
name: census-tracts
description: Use this skill for the requests related to USA census tracts; it provides a way to get tracts as a GeoDataframe in GeoPandas
---

# Census-Tracts Skill

## Description

This skill retrieves US Census tract geometries and attributes from the Census Bureau's TIGER/Web ArcGIS Feature Service.
https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/0/query

## Key Fields Returned
- **GEOID**: Unique Census geographic identifier (11 digits: 2-digit state + 3-digit county + 6-digit tract)
- **STATE**: Two-digit FIPS state code
- **COUNTY**: Three-digit FIPS county code
- **TRACT**: Six-digit Census tract code
- **NAME**: Full tract name
- **BASENAME**: Tract base name
- **AREALAND**: Land area (square meters)
- **AREAWATER**: Water area (square meters)
- **CENTLAT/CENTLON**: Centroid coordinates
- **geometry**: Tract boundary polygon

## Use Cases
1. Find census tract at a specific location (lat/lon)
2. Find census tract by GEOID
3. Find all tracts intersecting a region or linear feature (river, road, etc.)
4. Get all census tracts in a state (fast method using TIGER/Line shapefiles)

## Usage Examples

**CRITICAL NOTES**: If you need to all census tracts in state, use Example 1 below.

### Example 1: Get All Census Tracts in a State (Fast Method)

For retrieving all tracts in a state, downloading TIGER/Line shapefiles is **much faster** than using the API (typically 50-100x faster):

```python
import geopandas as gpd
import requests
from io import BytesIO
from zipfile import ZipFile
import tempfile
import os

def get_all_tracts_in_state(state_fips, year=2023):
    """
    Download all census tracts for a state from TIGER/Line shapefiles.
    This is the recommended method for bulk state-level downloads.
    
    Args:
        state_fips: Two-digit FIPS state code (e.g., '21' for Kentucky)
        year: Census year (default 2023, available: 2010-2023)
    
    Returns:
        GeoDataFrame with all tracts in the state
    
    Common State FIPS Codes:
        - Kentucky: '21'
        - Ohio: '39'
        - California: '06'
        - Texas: '48'
        - New York: '36'
        - Florida: '12'
        - Illinois: '17'
    """
    # TIGER/Line shapefile URL pattern
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_fips}_tract.zip"
    
    print(f"Downloading tracts for state {state_fips} from TIGER{year}...")
    
    # Download the zip file
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    
    # Extract and read the shapefile
    with ZipFile(BytesIO(response.content)) as zip_file:
        # Find the .shp file in the zip
        shp_file = [name for name in zip_file.namelist() if name.endswith('.shp')][0]
        
        # Extract all files to a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_file.extractall(tmpdir)
            shp_path = os.path.join(tmpdir, shp_file)
            gdf = gpd.read_file(shp_path)
    
    print(f"Loaded {len(gdf)} census tracts for state {state_fips}")
    return gdf

# Example usage: Get all tracts in Kentucky
kentucky_tracts = get_all_tracts_in_state('21')
print(f"Found {len(kentucky_tracts)} census tracts in Kentucky")
print(kentucky_tracts[['GEOID', 'NAME', 'COUNTYFP', 'ALAND', 'AWATER']].head())

# You can save to various formats
kentucky_tracts.to_file("kentucky_tracts.geojson", driver="GeoJSON")
kentucky_tracts.to_file("kentucky_tracts.shp")
kentucky_tracts.to_parquet("kentucky_tracts.parquet")

# Filter to specific counties if needed
jefferson_tracts = kentucky_tracts[kentucky_tracts['COUNTYFP'] == '111']  # Jefferson County
print(f"Jefferson County has {len(jefferson_tracts)} tracts")
```

**Performance Comparison:**
- **API method** (county-by-county): ~60-120 seconds for Kentucky (120+ API calls)
- **TIGER/Line method**: ~3-5 seconds for Kentucky (single download)

**When to use each method:**
- **Use TIGER/Line (Example 4)** when you need all tracts in a state
- **Use API (Examples 1-3)** when you need tracts for specific locations or geometries


### Example 2: Find Census Tract by Point Location

```python
import geopandas as gpd
import requests

def get_tract_by_location(latitude, longitude):
    """Get census tract containing a point."""
    url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/0/query"
    
    params = {
        "f": "geojson",
        "geometry": f"{longitude},{latitude}",
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    gdf = gpd.read_file(response.text)
    if gdf.empty:
        raise ValueError("No census tract found at the given location")
    
    return gdf

# Example usage
tract = get_tract_by_location(39.9612, -82.9988)  # Columbus, OH
print(tract[['GEOID', 'NAME', 'STATE', 'COUNTY']])
```

### Example 3: Find Tracts Intersecting a Geometry

```python
import json
from shapely.geometry import LineString, Polygon

def get_tracts_by_geometry(geometry, buffer_distance=0):
    """
    Find census tracts intersecting a geometry.
    
    Args:
        geometry: Shapely geometry (Point, LineString, Polygon, etc.)
        buffer_distance: Optional buffer in degrees (useful for lines)
    
    Returns:
        GeoDataFrame with intersecting tracts
    """
    url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/0/query"
    
    # Apply buffer if specified
    if buffer_distance > 0:
        geometry = geometry.buffer(buffer_distance)
    
    # Convert to appropriate Esri geometry format
    if geometry.geom_type == 'Point':
        geometry_type = "esriGeometryPoint"
        geometry_json = {"x": geometry.x, "y": geometry.y}
    elif geometry.geom_type in ['LineString', 'MultiLineString']:
        geometry_type = "esriGeometryPolyline"
        if geometry.geom_type == 'LineString':
            paths = [list(geometry.coords)]
        else:
            paths = [list(line.coords) for line in geometry.geoms]
        geometry_json = {"paths": paths}
    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
        geometry_type = "esriGeometryPolygon"
        if geometry.geom_type == 'Polygon':
            rings = [list(geometry.exterior.coords)]
            rings.extend([list(interior.coords) for interior in geometry.interiors])
        else:
            rings = []
            for poly in geometry.geoms:
                rings.append(list(poly.exterior.coords))
                rings.extend([list(interior.coords) for interior in poly.interiors])
        geometry_json = {"rings": rings}
    else:
        raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")
    
    params = {
        "f": "geojson",
        "geometry": json.dumps(geometry_json),
        "geometryType": geometry_type,
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true"
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    
    gdf = gpd.read_file(response.text)
    return gdf

# Example: River or road (always use buffer for linear features)
river_line = LineString([(-82.5, 39.5), (-82.3, 39.6), (-82.1, 39.7)])
tracts = get_tracts_by_geometry(river_line, buffer_distance=0.0001)  # Buffer required!
print(f"Found {len(tracts)} tracts")
```

### Example 4: Process Long Features in Segments

For long linear features (rivers, highways), process in segments to avoid API limitations:

```python
def get_tracts_for_long_feature(geometry, max_points_per_segment=50):
    """Process long features by splitting into manageable segments."""
    import time
    import pandas as pd
    
    all_tracts = []
    
    if geometry.geom_type == 'LineString':
        coords = list(geometry.coords)
        
        for i in range(0, len(coords) - 1, max_points_per_segment):
            segment_coords = coords[i:i + max_points_per_segment + 1]
            if len(segment_coords) >= 2:
                segment = LineString(segment_coords)
                # Buffer is required for linear features!
                tracts = get_tracts_by_geometry(segment, buffer_distance=0.0001)
                if not tracts.empty:
                    all_tracts.append(tracts)
                time.sleep(0.5)  # Rate limiting
    
    if all_tracts:
        combined = gpd.GeoDataFrame(pd.concat(all_tracts, ignore_index=True))
        return combined.drop_duplicates(subset=['GEOID']).reset_index(drop=True)
    
    return gpd.GeoDataFrame()
```

## Important Notes

- **Coordinate System**: Always use WGS84 (EPSG:4326)
- **Buffers for Linear Features**: **Always use a buffer** (0.0001-0.001 degrees) for LineStrings/rivers/roads, as zero-width lines may miss tract boundaries
- **Rate Limiting**: Add delays between requests for large queries
- **Geometry Simplification**: Simplify complex geometries before querying
- **API Limitations**: Break large features into segments (<100 points per request)
- **Valid Bounds**: US contiguous states approximately (-125°W to -66°W, 24°N to 49°N)
- **TIGER/Line Years**: Available from 2010-2023; use the most recent year for current boundaries
- **Bulk Downloads**: For state-level data, TIGER/Line shapefiles are 50-100x faster than API queries
