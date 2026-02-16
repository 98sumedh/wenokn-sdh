---
name: critical-habitat
description: Retrieve Critical Habitat designations for endangered and threatened species in the USA. Returns polygon geometries with species names and listing status.
---

# Critical Habitat Skill

## ⚠️ CRITICAL: Handling Multi-State Polygons

**IMPORTANT**: Critical habitat polygons often span multiple states. When a user asks for habitat "in Wyoming" or "in California", you MUST use the special filtering functions below to avoid showing polygons across the entire USA.

**DO NOT** just query by bbox - this will return entire multipolygons that span the whole country.

**ALWAYS** use one of these two approaches:
- **Option 1**: `get_critical_habitat_intersecting_state()` - Returns only polygons that touch the state
- **Option 2**: `get_critical_habitat_in_state()` - Returns polygons clipped to state boundary

## Description

This skill retrieves geometries and attributes of U.S. Fish and Wildlife Service Critical Habitat designations by accessing the ArcGIS Feature Service at the following URL:

```
https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/USFWS_Critical_Habitat/FeatureServer/0
```

**Service Details:**
- Maximum record count: 1000
- Native spatial reference: Web Mercator (EPSG:3857)
- Output spatial reference: WGS84 (EPSG:4326) - automatically transformed by the service

The service returns the following columns:

- **OBJECTID**: System-assigned unique identifier for each critical habitat feature
- **singlmulti**: Indicates if designation is for single or multiple species
- **comname**: Common name of the species (e.g., "Gray Wolf", "Northern Spotted Owl")
- **sciname**: Scientific name of the species (e.g., "Canis lupus", "Strix occidentalis caurina")
- **spcode**: Four-character species code
- **vipcode**: Three-character VIP (Vertebrate-Invertebrate-Plant) code
- **entity_id**: Unique identifier for the critical habitat entity
- **unit**: Critical habitat unit designation
- **subunit**: Critical habitat subunit designation (if applicable)
- **unitname**: Name of the critical habitat unit
- **subunitname**: Name of the critical habitat subunit (if applicable)
- **status**: Current status of the critical habitat designation (e.g., "Final", "Proposed", "Vacated")
- **leadoffice**: Lead U.S. Fish and Wildlife Service office code
- **coopoffice**: Cooperating office code(s)
- **coopofmore**: Additional cooperating offices
- **fedreg**: Federal Register citation
- **pubdate**: Publication date in Federal Register
- **effectdate**: Effective date of the critical habitat designation
- **vacatedate**: Date the designation was vacated (if applicable)
- **accuracy**: Accuracy of the spatial data
- **source_id**: Source data identifier
- **objectid_1**: Additional object identifier
- **listing_status**: ESA listing status of the species (e.g., "Endangered", "Threatened")
- **GlobalID**: Globally unique identifier
- **Shape__Area**: System-calculated area of the critical habitat geometry
- **Shape__Length**: System-calculated perimeter length of the critical habitat geometry

## When to Use

Use this skill to:

- Find critical habitat for a specific endangered or threatened species
- Find all critical habitat designations in a geographic area
- Query critical habitat by listing status (endangered vs. threatened)
- Find critical habitat by designation status (final, proposed, vacated)
- Analyze overlap between critical habitat and other spatial features
- Find critical habitat by effective date or publication date
- Identify species with critical habitat in a specific region

## How to Use

### Step 1: Import Required Libraries

```python
import geopandas as gpd
import requests
```

### Step 2: Define the Query Function

Use the `get_features` function to query the feature service. The **bbox parameter** is crucial for spatial filtering - it defines a bounding box to limit results to a specific geographic area.

**IMPORTANT**: This service has a maximum record count of 1000. For queries that may return more than 1000 results, you'll need to implement pagination using the `resultOffset` parameter.

```python
def get_features(service_url, where, bbox=None, max_records=1000):
    """
    Query the ArcGIS Feature Service for critical habitat.
    
    Note: The service uses Web Mercator (EPSG:3857) as its native spatial reference,
    but we request output in WGS84 (EPSG:4326) for easier geographic analysis.
    
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
        Maximum number of records to return (default: 1000, which is the service limit)
    
    Returns:
    --------
    geopandas.GeoDataFrame
        GeoDataFrame containing the queried critical habitat features in EPSG:4326
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
        "resultRecordCount": min(max_records, 1000)  # Service max is 1000
    }
    
    response = requests.get(service_url + "/query", params=params)
    data = response.json()
    
    if data.get('features'):
        return gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")
```

### Step 3: Query Examples

#### Example 1: Find Critical Habitat for a Specific Species by Common Name

```python
url = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/USFWS_Critical_Habitat/FeatureServer/0"

# Query for Northern Spotted Owl critical habitat
where = "LOWER(comname) LIKE '%spotted owl%'"
spotted_owl_habitat = get_features(url, where)

print(f"Found {len(spotted_owl_habitat)} critical habitat areas for Spotted Owl")
print(spotted_owl_habitat[['comname', 'unitname', 'status']].head())
```

#### Example 2: Find Critical Habitat by Scientific Name

```python
# Query for Gray Wolf (Canis lupus) critical habitat
where = "LOWER(sciname) LIKE '%canis lupus%'"
wolf_habitat = get_features(url, where)

print(f"Found {len(wolf_habitat)} critical habitat areas for Gray Wolf")
```

#### Example 3: Find All Critical Habitat in California

```python
# California bounding box (approximate)
california_bbox = [-124.48, 32.53, -114.13, 42.01]

# Query for all critical habitat in California
where = "1=1"  # Get all features within bbox
ca_critical_habitat = get_features(url, where, bbox=california_bbox)

print(f"Found {len(ca_critical_habitat)} critical habitat areas in California")

# See which species have critical habitat in California
unique_species = ca_critical_habitat['comname'].unique()
print(f"\nSpecies with critical habitat in California: {len(unique_species)}")
for species in sorted(unique_species)[:10]:
    print(f"  - {species}")
```

#### Example 4: Find Endangered Species Critical Habitat

```python
# Query for endangered species only
where = "listing_status = 'Endangered'"
endangered_habitat = get_features(url, where)

print(f"Found {len(endangered_habitat)} critical habitat areas for endangered species")
```

#### Example 5: Find Threatened Species Critical Habitat

```python
# Query for threatened species only
where = "listing_status = 'Threatened'"
threatened_habitat = get_features(url, where)

print(f"Found {len(threatened_habitat)} critical habitat areas for threatened species")
```

#### Example 6: Find Final vs. Proposed Critical Habitat

```python
# Pacific Northwest bounding box
pnw_bbox = [-125.0, 42.0, -116.0, 49.0]

# Query for final critical habitat designations
where = "status = 'Final'"
final_habitat = get_features(url, where, bbox=pnw_bbox)

print(f"Found {len(final_habitat)} final critical habitat areas in Pacific Northwest")

# Query for proposed critical habitat designations
where = "status = 'Proposed'"
proposed_habitat = get_features(url, where, bbox=pnw_bbox)

print(f"Found {len(proposed_habitat)} proposed critical habitat areas in Pacific Northwest")
```

#### Example 7: Find Critical Habitat by Effective Date

```python
# Find recently designated critical habitat (after 2020)
where = "effectdate >= '2020-01-01'"
recent_habitat = get_features(url, where)

print(f"Found {len(recent_habitat)} critical habitat areas designated since 2020")
```

#### Example 8: Find Multiple Species in a Region

```python
# Find critical habitat for salmon species in Pacific Northwest
pnw_bbox = [-125.0, 42.0, -116.0, 49.0]
where = "LOWER(comname) LIKE '%salmon%'"
salmon_habitat = get_features(url, where, bbox=pnw_bbox)

print(f"Found {len(salmon_habitat)} salmon critical habitat areas")
```

## Notes

The service has a maximum record count of 1000. If your query returns more results, you'll need to use pagination with the `resultOffset` parameter or refine your query with more specific WHERE clauses or a smaller bbox.

### Understanding the bbox Parameter

The **bbox (bounding box) parameter** is essential for efficient spatial queries:

- **Format**: `[minx, miny, maxx, maxy]` in WGS84 coordinates (longitude, latitude)
- **Purpose**: Limits the geographic extent of the query, reducing response time and data volume
- **Default**: If not provided, defaults to continental USA bounds
- **Use case**: Always provide a bbox when querying for features in a specific region

**Why bbox matters**: Critical habitat designations exist across the USA. Without a bbox, the service may return all features matching the WHERE clause across the entire country, which is inefficient and may exceed the 1000 record limit. The bbox acts as a spatial pre-filter, dramatically improving query performance.

**Common Regional Bounding Boxes**:
```python
# California
california_bbox = [-124.48, 32.53, -114.13, 42.01]

# Pacific Northwest (OR, WA)
pnw_bbox = [-125.0, 42.0, -116.0, 49.0]

# Southwest (AZ, NM)
southwest_bbox = [-115.0, 31.0, -103.0, 37.0]

# Southeast (FL, GA, SC)
southeast_bbox = [-88.0, 24.0, -75.0, 35.0]

# Rocky Mountain Region (CO, WY, MT)
rockies_bbox = [-116.0, 37.0, -102.0, 49.0]

# Great Lakes Region
greatlakes_bbox = [-93.0, 41.0, -74.0, 49.0]
```

### Using the comname Field

The `comname` field contains the common name of the species:

- **Format**: Common species names (e.g., "Northern Spotted Owl", "Delta Smelt", "Florida Panther")
- **Case-insensitive search**: Use `LOWER(comname)` for case-insensitive matching
  - Example: `"LOWER(comname) LIKE '%wolf%'"`
- **Exact match**: Use `comname = 'exact name'`
  - Example: `"comname = 'Gray Wolf'"`
- **Partial match**: Use `LIKE` with `%` wildcards
  - Example: `"comname LIKE '%Owl%'"` finds all owl species

### Using the sciname Field

The `sciname` field contains the scientific name of the species:

- **Format**: Latin binomial nomenclature (e.g., "Canis lupus", "Strix occidentalis caurina")
- **Case-insensitive search**: Use `LOWER(sciname)` for case-insensitive matching
  - Example: `"LOWER(sciname) LIKE '%canis%'"`
- **Genus-level search**: Search by genus
  - Example: `"sciname LIKE 'Oncorhynchus%'"` finds all Pacific salmon species

### Using the listing_status Field

Filter by Endangered Species Act listing status:

- **Common values**:
  - `"Endangered"` - Species in danger of extinction
  - `"Threatened"` - Species likely to become endangered
- **Query patterns**:
  - Example: `"listing_status = 'Endangered'"` for endangered species only
  - Example: `"listing_status = 'Threatened'"` for threatened species only

### Using the status Field

Filter by critical habitat designation status:

- **Common values**:
  - `"Final"` - Final critical habitat designation
  - `"Proposed"` - Proposed critical habitat (under review)
  - `"Vacated"` - Previously designated but vacated/removed
- **Query patterns**:
  - Example: `"status = 'Final'"` for final designations
  - Example: `"status = 'Proposed'"` for proposed designations
  - Example: `"status <> 'Vacated'"` to exclude vacated designations

### Using Date Fields

Query by designation dates:

- **effectdate**: When the critical habitat became effective
- **pubdate**: When it was published in the Federal Register
- **vacatedate**: When it was vacated (if applicable)

**Query patterns**:
```python
# Recent designations (after 2020)
where = "effectdate >= '2020-01-01'"

# Designations from a specific year
where = "effectdate >= '2015-01-01' AND effectdate < '2016-01-01'"

# Active designations (not vacated)
where = "vacatedate IS NULL"
```

### WHERE Clause Tips

- Use `LOWER(field)` for case-insensitive string matching on text fields
  - Example: `"LOWER(comname) LIKE '%salmon%'"`
- **For the listing_status column**: Use exact values
  - Example: `"listing_status = 'Endangered'"` for endangered species
  - Example: `"listing_status = 'Threatened'"` for threatened species
- **For the status column**: Use exact values
  - Example: `"status = 'Final'"` for final designations
  - Example: `"status = 'Proposed'"` for proposed designations
- Use `LIKE` with `%` wildcards for partial matches
  - Example: `"comname LIKE '%Owl%'"` finds all owl species
- Use date comparisons for temporal queries
  - Example: `"effectdate >= '2020-01-01'"`
- Combine multiple conditions with `AND` / `OR`
  - Example: `"listing_status = 'Endangered' AND status = 'Final'"`
- Use `IS NULL` or `IS NOT NULL` for null checks
  - Example: `"vacatedate IS NULL"` for active designations
- Always enclose string values in single quotes
- Use `1=1` to match all features when relying solely on spatial filtering (bbox)
- Remember the 1000 record limit - use bbox and specific WHERE clauses

### Handling the 1000 Record Limit

If you expect more than 1000 results, implement pagination:

```python
def get_all_features(service_url, where, bbox=None):
    """
    Get all features, handling pagination for >1000 results.
    
    Note: Service uses EPSG:3857 natively, but we request output in EPSG:4326.
    """
    all_features = []
    offset = 0
    batch_size = 1000
    
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

### Complete Example: Analyze Critical Habitat for Endangered Species in California

```python
import geopandas as gpd
import requests
import matplotlib.pyplot as plt

# Function definition (as above)
def get_features(service_url, where, bbox=None, max_records=1000):
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
        "resultRecordCount": min(max_records, 1000)
    }
    
    response = requests.get(service_url + "/query", params=params)
    data = response.json()
    
    if data.get('features'):
        return gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")

# Query for endangered species critical habitat in California
url = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/USFWS_Critical_Habitat/FeatureServer/0"
california_bbox = [-124.48, 32.53, -114.13, 42.01]
where = "listing_status = 'Endangered' AND status = 'Final'"

ca_endangered_habitat = get_features(url, where, bbox=california_bbox)

# Display results
print(f"Found {len(ca_endangered_habitat)} critical habitat areas for endangered species in California")

# Count species
unique_species = ca_endangered_habitat['comname'].unique()
print(f"\nNumber of endangered species with critical habitat: {len(unique_species)}")
print("\nSpecies list:")
for species in sorted(unique_species)[:15]:
    print(f"  - {species}")

# Calculate total area (convert to square kilometers)
ca_endangered_habitat_proj = ca_endangered_habitat.to_crs("EPSG:3310")  # California Albers
total_area_sqkm = ca_endangered_habitat_proj.geometry.area.sum() / 1_000_000
print(f"\nTotal critical habitat area: {total_area_sqkm:,.0f} square kilometers")

# Plot the critical habitat
fig, ax = plt.subplots(figsize=(12, 14))
ca_endangered_habitat.plot(ax=ax, alpha=0.5, edgecolor='red', facecolor='yellow')
ax.set_title('Critical Habitat for Endangered Species in California')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()
```

### Clipping Critical Habitat to State Boundaries

**IMPORTANT**: Critical habitat designations often span multiple states as multipolygons. When querying by bbox, you'll get the entire geometry for each species, not just the portion within your area of interest. You have two options:

**Option 1: Get entire polygons that intersect the state** (simpler, shows full habitat extent)
**Option 2: Clip to state boundary** (more precise, shows only the portion within the state)

#### Option 1: Get Only Polygons That Intersect a State

This approach explodes multipolygons and returns only the individual polygons that actually intersect the specified state:

```python
import geopandas as gpd
import requests

def get_critical_habitat_intersecting_state(state_name, listing_status=None):
    """
    Get only the individual polygons from critical habitat that intersect a state.
    Explodes multipolygons and filters to polygons within/touching the state.
    
    Parameters:
    -----------
    state_name : str
        State name (e.g., 'Wyoming', 'California')
    listing_status : str, optional
        Filter by 'Endangered' or 'Threatened' (default: both)
    
    Returns:
    --------
    geopandas.GeoDataFrame
        Critical habitat polygons that intersect the state (not clipped, but filtered)
    """
    # Get state boundary for bbox and filtering
    print(f"Fetching {state_name} boundary...")
    states_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/0"
    
    params = {
        "where": f"UPPER(NAME) = UPPER('{state_name}')",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "4326"
    }
    
    response = requests.get(states_url + "/query", params=params)
    data = response.json()
    
    if not data.get('features'):
        raise ValueError(f"State '{state_name}' not found")
    
    state_boundary = gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    state_geom = state_boundary.geometry.iloc[0]
    bounds = state_boundary.total_bounds  # [minx, miny, maxx, maxy]
    state_bbox = bounds.tolist()
    
    # Build WHERE clause
    where_parts = ["status = 'Final'"]  # Only final designations
    if listing_status:
        where_parts.append(f"listing_status = '{listing_status}'")
    where = " AND ".join(where_parts)
    
    # Query critical habitat
    print(f"Querying critical habitat intersecting {state_name}...")
    url = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/USFWS_Critical_Habitat/FeatureServer/0"
    habitat = get_features(url, where, bbox=state_bbox)
    
    if len(habitat) == 0:
        print(f"No critical habitat found intersecting {state_name}")
        return gpd.GeoDataFrame(columns=habitat.columns, crs="EPSG:4326")
    
    print(f"Found {len(habitat)} critical habitat designations")
    print(f"Exploding multipolygons and filtering to {state_name}...")
    
    # Explode multipolygons into individual polygons
    habitat_exploded = habitat.explode(index_parts=True).reset_index(drop=True)
    
    # Use spatial join to find only polygons that actually intersect the state
    # This is more reliable than simple intersects() for filtering
    habitat_in_state = gpd.sjoin(habitat_exploded, state_boundary, predicate='intersects', how='inner')
    
    # Drop the extra columns from the spatial join
    habitat_in_state = habitat_in_state.drop(columns=['index_right'], errors='ignore')
    
    # Remove duplicates if any (shouldn't be any with inner join)
    habitat_in_state = habitat_in_state.drop_duplicates(subset=['OBJECTID'], keep='first')
    
    print(f"Found {len(habitat_in_state)} individual polygons intersecting {state_name}")
    
    return habitat_in_state

# Example usage: Get only the polygons that intersect Wyoming
wyoming_habitat = get_critical_habitat_intersecting_state('Wyoming', listing_status='Endangered')

print(f"\nEndangered species with critical habitat in Wyoming:")
for species in sorted(wyoming_habitat['comname'].unique()):
    count = len(wyoming_habitat[wyoming_habitat['comname'] == species])
    print(f"  - {species} ({count} polygon(s))")

print(f"\nNote: These are individual polygons that intersect Wyoming (not clipped to state boundary)")

# Plot - shows only polygons that intersect Wyoming
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(14, 10))
wyoming_habitat.plot(ax=ax, column='comname', legend=True, alpha=0.6, cmap='tab20', edgecolor='black')

# Optionally overlay state boundary
state_boundary = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
wyoming_state = state_boundary[state_boundary['name'] == 'United States of America']
# Or fetch Wyoming boundary as shown above

ax.set_title('Critical Habitat Polygons Intersecting Wyoming')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()
```

#### Option 2: Clip Critical Habitat to State Boundary

For precise analysis of habitat *within* a state, use clipping:

```python
import geopandas as gpd
import requests

def get_state_boundary(state_name):
    """
    Get state boundary from Census Bureau TIGER/Line service.
    
    Parameters:
    -----------
    state_name : str
        State name (e.g., 'Wyoming', 'California')
    
    Returns:
    --------
    geopandas.GeoDataFrame
        State boundary polygon
    """
    # Census Bureau States service
    states_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/0"
    
    params = {
        "where": f"UPPER(NAME) = UPPER('{state_name}')",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "4326"
    }
    
    response = requests.get(states_url + "/query", params=params)
    data = response.json()
    
    if data.get('features'):
        return gpd.GeoDataFrame.from_features(data['features'], crs="EPSG:4326")
    else:
        raise ValueError(f"State '{state_name}' not found")

def get_critical_habitat_in_state(state_name, listing_status=None):
    """
    Get critical habitat clipped to a specific state boundary.
    
    Parameters:
    -----------
    state_name : str
        State name (e.g., 'Wyoming', 'California')
    listing_status : str, optional
        Filter by 'Endangered' or 'Threatened' (default: both)
    
    Returns:
    --------
    geopandas.GeoDataFrame
        Critical habitat clipped to state boundary
    """
    # Get state boundary
    print(f"Fetching {state_name} boundary...")
    state_boundary = get_state_boundary(state_name)
    state_geom = state_boundary.geometry.iloc[0]
    
    # Get state bounding box
    bounds = state_boundary.total_bounds  # [minx, miny, maxx, maxy]
    state_bbox = bounds.tolist()
    
    # Build WHERE clause
    where_parts = ["status = 'Final'"]  # Only final designations
    if listing_status:
        where_parts.append(f"listing_status = '{listing_status}'")
    where = " AND ".join(where_parts)
    
    # Query critical habitat
    print(f"Querying critical habitat in {state_name}...")
    url = "https://services.arcgis.com/QVENGdaPbd4LUkLV/ArcGIS/rest/services/USFWS_Critical_Habitat/FeatureServer/0"
    habitat = get_features(url, where, bbox=state_bbox)
    
    if len(habitat) == 0:
        print(f"No critical habitat found in {state_name}")
        return gpd.GeoDataFrame(columns=habitat.columns, crs="EPSG:4326")
    
    print(f"Found {len(habitat)} habitat designations (before clipping)")
    print(f"Clipping to {state_name} boundary...")
    
    # Clip to state boundary - this gives us only the portion within the state
    habitat_clipped = gpd.clip(habitat, state_geom)
    
    # Remove any empty geometries that might result from clipping
    habitat_clipped = habitat_clipped[~habitat_clipped.geometry.is_empty]
    
    print(f"After clipping: {len(habitat_clipped)} habitat areas within {state_name}")
    
    return habitat_clipped

# Example usage: Get endangered species critical habitat in Wyoming
wyoming_habitat = get_critical_habitat_in_state('Wyoming', listing_status='Endangered')

print(f"\nEndangered species with critical habitat in Wyoming:")
for species in sorted(wyoming_habitat['comname'].unique()):
    print(f"  - {species}")

# Calculate area within Wyoming
wyoming_habitat_proj = wyoming_habitat.to_crs("EPSG:32613")  # UTM Zone 13N for Wyoming
total_area_sqkm = wyoming_habitat_proj.geometry.area.sum() / 1_000_000
print(f"\nTotal critical habitat area in Wyoming: {total_area_sqkm:,.0f} square kilometers")

# Plot
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(12, 10))
wyoming_habitat.plot(ax=ax, column='comname', legend=True, alpha=0.7, cmap='tab20')
ax.set_title('Endangered Species Critical Habitat in Wyoming (Clipped)')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()
```

**When to use each option:**

- **Option 1 (Filter to intersecting polygons)**: Use when you want to see complete individual polygons that touch or overlap Wyoming, without cutting them. For example, if Canada Lynx has 10 separate habitat polygons across the western US, you'll only get the 2-3 polygons that actually touch Wyoming - not all 10, and not clipped. Good for understanding which specific habitat units are relevant to the state.

- **Option 2 (Clipped to state)**: Use when you need accurate area calculations within a state, regulatory analysis for a specific state, or visualization focused only on the state's portion. This cuts each polygon at the state boundary, so you see only what's inside Wyoming.

**Why clipping is important for accurate analysis:**

1. **Accurate area calculations**: Without clipping, you'd be calculating the area of the entire multistate designation, not just the portion in your state of interest
2. **Correct visualization**: Maps will show only the habitat within the state boundary
3. **Proper analysis**: When analyzing habitat in a specific state, you want only the geometries that actually fall within that state

**Alternative: Using State Abbreviation Column (if available)**

Some datasets include a state field. However, the critical habitat service doesn't have a direct state column. The spatial clipping approach is the most accurate method for this service.
