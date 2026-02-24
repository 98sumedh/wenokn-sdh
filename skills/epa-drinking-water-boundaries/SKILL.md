---
name: epa-drinking-water-boundaries
description: Use this skill for requests to retrieve EPA drinking water service area boundaries in the USA as a GeoDataFrame in GeoPandas. This skill can retrieve water systems by name, PWSID, state (via Primacy_Agency), population size, service area type, or spatial extent.
---

# EPA Drinking Water Service Areas Skill

## Description

This skill retrieves geometries and attributes of EPA Public Water System (PWS) service area boundaries by accessing the ArcGIS Feature Service at the following URL:

```
https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/Water_System_Boundaries/FeatureServer/0
```

The service returns the following columns:

- **OBJECTID**: System-assigned unique identifier for each feature in the service
- **Original_Data_Provider**: The original source organization that provided the boundary data
- **Data_Provider_Type**: Type of organization that provided the data
- **Data_Source**: Description of the data source
- **PWSID**: Public Water System ID — unique identifier for each water system (e.g., "CA3710004")
- **PWS_Name**: Name of the public water system
- **Primacy_Agency**: The state or territory agency with regulatory oversight (two-letter abbreviation, e.g., "CA", "TX")
- **Pop_Cat_5**: Population category grouping (5-tier classification)
- **Population_Served_Count**: Estimated number of people served by the water system
- **Service_Connections_Count**: Number of service connections in the system
- **Model_Method**: Method used to model or derive the service area boundary
- **Service_Area_Type**: Type of service area (e.g., "Retail", "Wholesale")
- **Symbology_Field**: Field used for map symbology
- **Modification_Method**: Method used if the boundary was modified
- **Feature_Type**: Type of feature geometry
- **Method_Details**: Additional details about the modeling or data method
- **Verification_Status**: Status of boundary verification
- **Detailed_Facility_Report**: URL or reference to EPA's detailed facility report for the system
- **Original_Data_Created_Date**: Date the original boundary data was created
- **Confirmed**: Whether the boundary has been confirmed
- **Shape__Area**: System-calculated area of the geometry in the feature service's coordinate system
- **Shape__Length**: System-calculated perimeter length of the geometry
- **Area_SqKM**: Area of the service boundary in square kilometers

## When to Use

Use this skill to:

- Find a drinking water utility's service area by name or PWSID
- Find which water system(s) serve a specific location or area
- Find all water systems in a specific state or region
- Analyze water system service areas spatially (e.g., overlap with other features)
- Query systems by population size, service area type, or verification status
- Assess drinking water coverage across geographies

## How to Use

### Step 1: Import Required Libraries

```python
import geopandas as gpd
import requests
```

### Step 2: Define the Query Function

Use the `get_features` function to query the feature service. The **bbox parameter** is crucial for spatial filtering — it defines a bounding box to limit results to a specific geographic area. Note that the service's native CRS is EPSG:3857 (Web Mercator), but this function requests output in WGS84 (EPSG:4326) for compatibility.

```python
def get_features(service_url, where, bbox=None):
    """
    Query the ArcGIS Feature Service for EPA water system boundaries.
    
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
        GeoDataFrame containing the queried water system boundary features
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
        "inSR": "4326",   # Input bbox is in WGS84
        "outSR": "4326",  # Return geometries in WGS84
        "resultOffset": 0,
        "resultRecordCount": 2000  # Max record count for this service
    }

    response = requests.get(service_url + "/query", params=params)
    data = response.json()

    if data.get('features'):
        return gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
```

### Step 3: Query Examples

#### Example 1: Find a Water System by Name

```python
url = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/Water_System_Boundaries/FeatureServer/0"

# Query for a water system by name (case-insensitive partial match)
where = "LOWER(PWS_Name) LIKE '%san diego%'"
systems_gdf = get_features(url, where)
```

#### Example 2: Find All Water Systems in a State

The `Primacy_Agency` column holds the two-letter state abbreviation for the regulatory agency.

```python
# Query for water systems in Texas
where = "Primacy_Agency = 'TX'"
tx_systems = get_features(url, where)
```

#### Example 3: Find a Water System by PWSID

```python
# Find a specific system by its unique PWSID
where = "PWSID = 'CA3710004'"
system = get_features(url, where)
```

#### Example 4: Find Large Water Systems by Population

```python
# Find systems serving more than 100,000 people
where = "Population_Served_Count > 100000"
large_systems = get_features(url, where)
```

#### Example 5: Find Water Systems by Service Area Type

```python
# Find retail water systems only
where = "Service_Area_Type = 'Retail'"
retail_systems = get_features(url, where)
```

#### Example 6: Spatial Query with Bounding Box

```python
# Find all water systems within a bounding box around Chicago
chicago_bbox = [-88.5, 41.5, -87.2, 42.2]  # [minx, miny, maxx, maxy]
where = "1=1"  # No attribute filter — rely solely on spatial extent
chicago_systems = get_features(url, where, bbox=chicago_bbox)
```

#### Example 7: Combine Attribute and Spatial Filters

```python
# Find confirmed retail water systems in California
where = "Primacy_Agency = 'CA' AND Service_Area_Type = 'Retail' AND Confirmed = 'Yes'"
ca_retail = get_features(url, where)
```

## Notes

- The service has a **maximum record count of 2000** per request. If your query may return more than 2000 results, either narrow your WHERE clause, use a tighter bbox, or implement pagination using `resultOffset`.
- Fetching all systems in a large state may take a minute or more depending on the number of matching records.
- The service's native spatial reference is **EPSG:3857** (Web Mercator). Always pass `inSR=4326` when supplying a WGS84 bbox and `outSR=4326` to receive geometries in WGS84.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for efficient spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query, reducing response time and data volume
- **Default**: If not provided, defaults to continental USA bounds
- **Use case**: Always provide a bbox when querying for features in a specific city or region

**Why bbox matters**: Without a bbox, the service may return all features matching the WHERE clause across the entire USA, which can exceed the 2000-record limit and be very slow. The bbox acts as a spatial pre-filter, dramatically improving query performance.

### Using the Primacy_Agency Column

The `Primacy_Agency` column is the most reliable way to filter by state:

- **Format**: Two-letter state abbreviations (e.g., "CA", "TX", "FL")
- **Query pattern**: `Primacy_Agency = 'XX'` where XX is the state abbreviation
  - Example: `"Primacy_Agency = 'CA'"` for California
  - Example: `"Primacy_Agency = 'TX'"` for Texas
- **Multiple states**: Use OR to query multiple states
  - Example: `"Primacy_Agency = 'CA' OR Primacy_Agency = 'NV'"`

### Using the PWSID Column

Each water system has a unique Public Water System ID (PWSID):

- **Format**: Two-letter state prefix followed by 7 digits (e.g., "CA3710004", "TX0610012")
- **Query pattern**: `PWSID = 'XXXXXXXXX'` for exact match
- **Useful for**: Joining with EPA SDWIS (Safe Drinking Water Information System) data

### Using the Population_Served_Count Column

Filter systems by the population they serve:

- **Query pattern**: Use comparison operators
  - Example: `"Population_Served_Count > 100000"` for large systems
  - Example: `"Population_Served_Count <= 500"` for very small systems
- **Pop_Cat_5** provides a pre-computed 5-tier category grouping if exact counts are not needed

### Pagination for Large Result Sets

If a query may return more than 2000 records, use pagination:

```python
def get_all_features(service_url, where, bbox=None):
    """Fetch all features using pagination to handle the 2000-record limit."""
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
            "inSR": "4326",
            "outSR": "4326",
            "resultOffset": offset,
            "resultRecordCount": batch_size
        }

        response = requests.get(service_url + "/query", params=params)
        data = response.json()
        features = data.get('features', [])

        if not features:
            break

        all_features.extend(features)

        if len(features) < batch_size:
            break  # Last page

        offset += batch_size

    if all_features:
        return gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
```

### WHERE Clause Tips

- Use `LOWER(field)` for case-insensitive string matching on text fields
- **For Primacy_Agency**: Use exact match `Primacy_Agency = 'XX'`
- **For PWSID**: Use exact match `PWSID = 'XXXXXXXXX'`
- Use `LIKE` with `%` wildcards for partial name matches
  - Example: `"PWS_Name LIKE '%Municipal%'"` finds systems with "Municipal" in the name
- Use `1=1` to match all features when relying solely on spatial filtering (bbox)
- Combine multiple conditions with `AND` / `OR`
- Always enclose string values in single quotes
