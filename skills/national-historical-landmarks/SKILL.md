---
name: national-historical-landmarks
description: Use this skill for requests to retrieve National Register of Historic Places (NRHP) locations in the USA as a GeoDataFrame in GeoPandas. This skill can retrieve historical landmarks by name, location, state, resource type, or NHL status.
---

# National Historical Landmarks Skill

## Description

This skill retrieves geometries and attributes of National Register of Historic Places (NRHP) locations by accessing the ArcGIS Feature Service at the following URL:

```
https://mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/0
```

The service has a maximum record count of 2000 and returns the following columns:

- **OBJECTID**: System-assigned unique identifier for each location feature in the service
- **NRIS_Refnum**: National Register Information System reference number (11-character unique identifier)
- **RESNAME**: Resource name - official name of the historic property (up to 250 characters)
- **ResType**: Resource type - type of historic resource (Building, District, Object, Site, Structure)
- **Address**: Street address of the historic property
- **City**: City where the property is located
- **County**: County where the property is located
- **State**: State where the property is located (full state name, not abbreviation)
- **Vicinity**: Additional location information or vicinity description
- **MultiName**: Multiple Resource Name - if property is part of a multiple property submission
- **NumCBldg**: Number of contributing buildings
- **NumCObj**: Number of contributing objects
- **NumCSite**: Number of contributing sites
- **NumCStru**: Number of contributing structures
- **Is_NHL**: Indicates if the property is a National Historic Landmark (Y/N)
- **BND_TYPE**: Boundary type (Entrance point, Center point, Facade point, Boundary polygon, etc.)
- **BND_OTHER**: Additional boundary type comments
- **IS_EXTANT**: Indicates if the property still exists (True, False, Unknown, etc.)
- **EXTANT_OTH**: Additional comments about extant status
- **CertDate**: Certification date (date listed on National Register)
- **CREATEDATE**: Date the record was created in the database
- **EDIT_DATE**: Date of last edit to the record
- **MAP_METHOD**: Method used for mapping (Differential GPS, Autonomous GPS, Digitized, etc.)
- **MAP_MTH_OT**: Additional mapping method comments
- **SOURCE**: Source of the geographic data
- **SRC_DATE**: Date of the source data
- **SRC_SCALE**: Scale of the source data
- **SRC_ACCU**: Source horizontal accuracy
- **SRC_COORD**: Source coordinate system
- **ORIGINATOR**: Originating institution that created the data
- **CONSTRANT**: Use constraints for the data
- **CR_ID**: Cultural Resource GUID
- **GEOM_ID**: Location GUID
- **PROPERTY_ID**: Property identifier
- **STATUS**: Status of the listing
- **NARA_URL**: URL to National Archives records
- **Shape**: Geometry of the location (point, polygon, etc.)

## When to Use

Use this skill to:

- Find a historic landmark by name
- Find historic properties in a specific city, county, or state
- Query National Historic Landmarks (NHL) specifically
- Find properties by resource type (buildings, districts, objects, sites, structures)
- Identify extant vs. demolished historic properties
- Find properties within a geographic area
- Query properties by certification date or other attributes

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
    Query the ArcGIS Feature Service for historical landmarks.
    
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
        GeoDataFrame containing the queried historical landmark features
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

#### Example 1: Find a Historic Landmark by Name

```python
url = "https://mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/0"

# Query for "Independence Hall"
where = "LOWER(RESNAME) LIKE '%independence hall%'"
landmarks_gdf = get_features(url, where)
```

#### Example 2: Find All National Historic Landmarks (NHL)

This example demonstrates how to find only properties designated as National Historic Landmarks.

```python
# Query for National Historic Landmarks
where = "Is_NHL = 'Y'"
nhl_landmarks = get_features(url, where)
```

#### Example 3: Find Historic Properties in a Specific State

The `State` column contains full state names in UPPERCASE (not abbreviations).

```python
# Query for landmarks in Pennsylvania
where = "State = 'PENNSYLVANIA'"
pa_landmarks = get_features(url, where)
```

#### Example 4: Find Properties by Resource Type

```python
# Find all historic districts
where = "ResType = 'District'"
districts = get_features(url, where)

# Find all buildings
where = "ResType = 'Building'"
buildings = get_features(url, where)
```

#### Example 5: Find Properties in a Specific City

```python
# Find all historic properties in Boston
where = "City = 'Boston'"
boston_landmarks = get_features(url, where)
```

#### Example 6: Find Extant Properties (Still Standing)

```python
# Find properties that still exist
where = "IS_EXTANT = 'True'"
extant_properties = get_features(url, where)
```

#### Example 7: Combine Multiple Criteria

```python
# Find National Historic Landmarks in California that are still extant
where = "Is_NHL = 'Y' AND State = 'CALIFORNIA' AND IS_EXTANT = 'True'"
ca_nhl_extant = get_features(url, where)
```

## Notes

The service has a maximum record count of 2000. If your query returns more results, you'll need to use pagination with the `resultOffset` parameter or refine your query with more specific WHERE clauses or a smaller bbox.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for efficient spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query, reducing response time and data volume
- **Default**: If not provided, defaults to continental USA bounds
- **Use case**: Always provide a bbox when querying for features in a specific region

**Why bbox matters**: Without a bbox, the service may return all features matching the WHERE clause across the entire USA, which is inefficient. The bbox acts as a spatial pre-filter, dramatically improving query performance. This is especially important for this service given the 2000 record limit.

### Using the State Column

The `State` column is useful for querying landmarks by location:

- **Format**: Contains full state names in UPPERCASE (e.g., "PENNSYLVANIA", "CALIFORNIA", "NEW YORK")
- **Important**: Use full state names in UPPERCASE, not abbreviations
- **Query pattern**: Use `State = 'STATENAME'` for exact matches
  - Example: `"State = 'PENNSYLVANIA'"` for Pennsylvania
  - Example: `"State = 'CALIFORNIA'"` for California
- **Multiple states**: Use OR to find landmarks in multiple states
  - Example: `"State = 'PENNSYLVANIA' OR State = 'NEW JERSEY'"`
- **Partial match**: Use LIKE for partial matches
  - Example: `"State LIKE '%NEW%'"` finds NEW YORK, NEW JERSEY, NEW MEXICO, NEW HAMPSHIRE

### Using the ResType Column

Filter by different types of historic resources:

- **Resource types**:
  - `"Building"` - Individual historic buildings
  - `"District"` - Historic districts containing multiple properties
  - `"Object"` - Historic objects (monuments, sculptures, etc.)
  - `"Site"` - Historic sites (archaeological sites, battlefields, etc.)
  - `"Structure"` - Historic structures (bridges, dams, etc.)
- **Query pattern**: Use `ResType = 'type'` for exact matches
  - Example: `"ResType = 'Building'"` for buildings only
  - Example: `"ResType = 'District'"` for historic districts

### Using the Is_NHL Column

Filter for National Historic Landmarks:

- **Values**: 'Y' (yes) or 'N' (no)
- **Query pattern**: Use `Is_NHL = 'Y'` to find only NHL properties
  - Example: `"Is_NHL = 'Y'"` returns only National Historic Landmarks
  - Example: `"Is_NHL = 'N'"` returns properties on the National Register but not designated as NHL

### WHERE Clause Tips

- Use `LOWER(field)` for case-insensitive string matching on text fields
- **For the State column**: Use full state names in UPPERCASE
  - Example: `"State = 'PENNSYLVANIA'"` not `"State = 'PA'"` or `"State = 'Pennsylvania'"`
- **For the Is_NHL column**: Use 'Y' or 'N'
  - Example: `"Is_NHL = 'Y'"` for National Historic Landmarks
- **For the ResType column**: Use exact type names
  - Example: `"ResType = 'Building'"` for buildings
- **For the IS_EXTANT column**: Use 'True', 'False', or 'Unknown'
  - Example: `"IS_EXTANT = 'True'"` for properties that still exist
- Use `LIKE` with `%` wildcards for partial matches
  - Example: `"RESNAME LIKE '%Hall%'"` finds resources with "Hall" in the name
- Use `1=1` to match all features when relying solely on spatial filtering (bbox)
- Combine multiple conditions with `AND` / `OR`
- Always enclose string values in single quotes
- Remember the 2000 record limit - use specific WHERE clauses or bbox to limit results

### Handling the 2000 Record Limit

If you expect more than 2000 results, implement pagination:

```python
def get_all_features(service_url, where, bbox=None):
    """
    Get all features, handling pagination for >2000 results.
    """
    all_features = []
    offset = 0
    batch_size = 2000
    
    while True:
        params = {
            "where": where,
            "geometry": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}" if bbox else None,
            "geometryType": "esriGeometryEnvelope" if bbox else None,
            "spatialRel": "esriSpatialRelIntersects" if bbox else None,
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
