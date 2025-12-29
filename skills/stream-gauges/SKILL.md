---
name: stream-gauges
description: Query stream gauge or gages geometries in the USA from the GeoConnex knowledge graph. Returns stream gauge locations and metadata as a GeoDataFrame.
---

# Stream Gauges Skill

## Description

Retrieves stream gauge or gages geometries from the GeoConnex knowledge graph on FRINK using SPARQL queries. Returns results as a GeoPandas GeoDataFrame.

## When to Use

- Find stream gauge or gages by name
- Find stream gauge or gages within counties or states
- Find stream gauge or gages near rivers or other geographic features
- Spatial analysis involving stream gauge or gages

## Important Notes

- **Always use spatial filtering in SPARQL** using `geof:sfContains()` for county/state queries - this is much faster than filtering in Python
- **County names must include state** - use "Ross County, Ohio" not just "Ross County" unless the county name is unqiue
- **stream gauge or gages are point geometries** - they may not intersect river lines exactly due to GIS precision
- **Large queries take time** - state-level queries may take up to 1 minute

## Examples

### Example 1: Find Stream Gauges in a County

**User Request:** "Find stream gauge in Ross County" or "Find stream gauge in Ross County, Ohio"

**Complete Code:**

```python
import sparql_dataframe
import geopandas as gpd
from shapely import wkt

# SPARQL query with spatial filtering
query = '''
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?gageId ?gageName ?gageGeometry
WHERE {{
    VALUES ?inputCounty { "Ross County, Ohio" }
    
    # Counties (AdministrativeRegion_2) - FILTERED BY NAME FIRST
    ?county rdf:type <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2> ;
            rdfs:label ?countyName ;
            geo:hasGeometry/geo:asWKT ?countyGeometry .
    FILTER(STRSTARTS(STR(?county), "http://stko-kwg.geog.ucsb.edu/lod/resource/"))
    FILTER(STRSTARTS(LCASE(STR(?countyName)), LCASE(?inputCounty)))
    
    # Gages - ONLY AFTER COUNTIES ARE FILTERED
    ?gage rdf:type hyf:HY_HydroLocation;
           rdf:type hyf:HY_HydrometricFeature;
           schema:provider <https://waterdata.usgs.gov>;
           schema:name ?gageName;
           schema:description ?gageDescription;
           geo:hasGeometry/geo:asWKT ?gageGeometry.  
    FILTER(STRSTARTS(STR(?gage), "https://geoconnex.us/ref/gages/"))
    BIND(STRAFTER(STR(?gage), "https://geoconnex.us/ref/gages/") AS ?gageId)
    
    # Spatial containment - LAST, on reduced dataset
    FILTER(geof:sfContains(?countyGeometry, ?gageGeometry))
}}
'''

# Execute query
endpoint_url = "https://frink.apps.renci.org/federation/sparql"
df = sparql_dataframe.get(endpoint_url, query)

# Convert to GeoDataFrame
wkt_col = None
for col in df.columns:
    col_lower = col.lower()
    if 'geometry' in col_lower or 'geom' in col_lower or 'wkt' in col_lower:
        sample = df[col].dropna().astype(str)
        if len(sample) > 0:
            valid_wkt = sample.str.match(r'^(POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|GEOMETRYCOLLECTION)\s*\(')
            if valid_wkt.sum() / len(sample) > 0.5:
                wkt_col = col
                break

if wkt_col is None:
    raise ValueError("No WKT geometry column found")

df = df.dropna(subset=[wkt_col]).copy()
df['geometry'] = df[wkt_col].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# Display results
print(f"Found {len(gdf)} gauges in Ross County, Ohio")
for _, row in gdf.iterrows():
    print(f"- {row['gagesName']}")
```

**Key Points:**
- Uses `AdministrativeRegion_2` for counties
- Spatial filtering with `geof:sfContains(?countyGeometry, ?gageGeometry)`
- County name must include state: "Ross County, Ohio"

---

### Example 2: Find Stream Gages in a State

**User Request:** "Find all stream gages in Ohio" or "Find gages in Ohio state"

**Complete Code:**

```python
import sparql_dataframe
import geopandas as gpd
from shapely import wkt

# SPARQL query with spatial filtering
query = '''
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?gageId ?gageName ?gageGeometry
WHERE {{
    # User-provided states - FILTER EARLY
    VALUES ?inputState { "Ohio" }

    # States (AdministrativeRegion_1) - FILTERED BY NAME FIRST
    ?state rdf:type <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> ;
           rdfs:label ?stateName ;
           geo:hasGeometry/geo:asWKT ?stateGeometry .
    FILTER(STRSTARTS(STR(?state), "http://stko-kwg.geog.ucsb.edu/lod/resource/"))
    FILTER(STRSTARTS(LCASE(STR(?stateName)), LCASE(?inputState)))

    # Gages - ONLY AFTER STATES ARE FILTERED
    ?gage rdf:type hyf:HY_HydroLocation;
           rdf:type hyf:HY_HydrometricFeature;
           schema:provider <https://waterdata.usgs.gov>;
           schema:name ?gageName;
           schema:description ?gageDescription;
           geo:hasGeometry/geo:asWKT ?gageGeometry.  
    FILTER(STRSTARTS(STR(?gage), "https://geoconnex.us/ref/gages/"))
    BIND(STRAFTER(STR(?gage), "https://geoconnex.us/ref/gages/") AS ?gageId)

    # Spatial containment - LAST, on reduced dataset
    FILTER(geof:sfContains(?stateGeometry, ?gageGeometry))
}}
'''

# Execute query
endpoint_url = "https://frink.apps.renci.org/federation/sparql"
df = sparql_dataframe.get(endpoint_url, query)

# Convert to GeoDataFrame
wkt_col = None
for col in df.columns:
    col_lower = col.lower()
    if 'geometry' in col_lower or 'geom' in col_lower or 'wkt' in col_lower:
        sample = df[col].dropna().astype(str)
        if len(sample) > 0:
            valid_wkt = sample.str.match(r'^(POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|GEOMETRYCOLLECTION)\s*\(')
            if valid_wkt.sum() / len(sample) > 0.5:
                wkt_col = col
                break

if wkt_col is None:
    raise ValueError("No WKT geometry column found")

df = df.dropna(subset=[wkt_col]).copy()
df['geometry'] = df[wkt_col].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# Display results
print(f"Found {len(gdf)} gages in Ohio")
print(f"First 10 gages:")
for _, row in gdf.head(10).iterrows():
    print(f"- {row['damName']}")
```

**Key Points:**
- Uses `AdministrativeRegion_1` for states
- Spatial filtering with `geof:sfContains(?stateGeometry, ?damGeometry)`
- State name only: "Ohio" (no additional qualifier needed)
- May take up to 1 minute for large states

---

### Example 3: Find Streamflow Gauges on the Scioto River

```python
"""
Find all stream gauges on the Scioto River using a small buffer.

This script:
1. Gets the geometry of the Scioto River
2. Finds all states the river flows through
3. Gets all gauges in those states
4. Applies a small buffer (15 meters) to the river
5. Finds gauges that intersect the buffered river
"""

import sparql_dataframe
import geopandas as gpd
from shapely import wkt
import pandas as pd

# SPARQL endpoint
ENDPOINT_URL = "https://frink.apps.renci.org/federation/sparql"

def execute_sparql_query(query):
    """Execute a SPARQL query and return the result as a DataFrame."""
    print("Executing SPARQL query...")
    df = sparql_dataframe.get(ENDPOINT_URL, query)
    print(f"Query returned {len(df)} rows")
    return df

def df_to_gdf(df):
    """Convert a DataFrame with WKT geometry to a GeoDataFrame."""
    # Identify the WKT column automatically
    wkt_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'geometry' in col_lower or 'geom' in col_lower or 'wkt' in col_lower:
            sample = df[col].dropna().astype(str)
            if len(sample) > 0:
                valid_wkt = sample.str.match(r'^(POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|GEOMETRYCOLLECTION)\s*\(')
                if valid_wkt.sum() / len(sample) > 0.5:
                    wkt_col = col
                    break
    
    if wkt_col is None:
        raise ValueError("No WKT geometry column found")
    
    # Drop missing geometries
    df = df.dropna(subset=[wkt_col]).copy()
    
    # Convert WKT to shapely geometries
    df['geometry'] = df[wkt_col].apply(wkt.loads)
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    
    return gdf

def get_river_geometry(river_name):
    """Get the geometry of a river by name."""
    print(f"\n=== Step 1: Getting geometry for {river_name} ===")
    
    query = f'''
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

SELECT DISTINCT ?riverName ?riverGeometry 
WHERE {{
  ?river a hyf:HY_FlowPath ;
         a hyf:HY_WaterBody ;
         a schema:Place ;
         schema:name ?riverName ;
         geo:hasGeometry/geo:asWKT ?riverGeometry .
  FILTER(LCASE(?riverName) = LCASE("{river_name}")) .
}}
ORDER BY DESC(STRLEN(?riverGeometry))
LIMIT 1
'''
    
    df = execute_sparql_query(query)
    
    if len(df) == 0:
        raise ValueError(f"River '{river_name}' not found")
    
    gdf = df_to_gdf(df)
    print(f"Found river: {gdf.iloc[0]['riverName']}")
    
    return gdf

def get_states_for_river(river_name):
    """Find all states that a river flows through."""
    print(f"\n=== Step 2: Finding states that {river_name} flows through ===")
    
    query = f'''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>

SELECT DISTINCT ?stateName 
WHERE {{
  ?river a hyf:HY_FlowPath ;
         a hyf:HY_WaterBody ;
         a schema:Place ;
         schema:name ?riverName ;
         geo:hasGeometry/geo:asWKT ?riverGeometry .
  FILTER(LCASE(?riverName) = LCASE("{river_name}")) .
  
  ?state rdf:type kwg-ont:AdministrativeRegion_1 ;
          rdfs:label ?stateName ;
          geo:hasGeometry/geo:asWKT ?stateGeometry .
  FILTER(STRSTARTS(STR(?state), "http://stko-kwg.geog.ucsb.edu/lod/resource/"))
  FILTER(strlen(?stateName) > 2)

  FILTER(geof:sfIntersects(?riverGeometry, ?stateGeometry))
}}
LIMIT 200
'''
    
    df = execute_sparql_query(query)
    states = df['stateName'].tolist()
    print(f"Found {len(states)} states: {', '.join(states)}")
    
    return states

def get_gauges_in_states(states):
    """Get all gauges in the given states."""
    print(f"\n=== Step 3: Getting all gauges in states: {', '.join(states)} ===")
    
    # Create VALUES clause for states
    state_values = ' '.join([f'"{state}"' for state in states])
    
    query = f'''
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?gageId ?gageName ?gageGeometry
WHERE {{
    # User-provided states - FILTER EARLY
    VALUES ?inputState {{ {state_values} }}

    # States (AdministrativeRegion_1) - FILTERED BY NAME FIRST
    ?state rdf:type <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1> ;
           rdfs:label ?stateName ;
           geo:hasGeometry/geo:asWKT ?stateGeometry .
    FILTER(STRSTARTS(STR(?state), "http://stko-kwg.geog.ucsb.edu/lod/resource/"))
    FILTER(STRSTARTS(LCASE(STR(?stateName)), LCASE(?inputState)))

    # Gages - ONLY AFTER STATES ARE FILTERED
    ?gage rdf:type hyf:HY_HydroLocation;
           rdf:type hyf:HY_HydrometricFeature;
           schema:provider <https://waterdata.usgs.gov>;
           schema:name ?gageName;
           schema:description ?gageDescription;
           geo:hasGeometry/geo:asWKT ?gageGeometry.  
    FILTER(STRSTARTS(STR(?gage), "https://geoconnex.us/ref/gages/"))
    BIND(STRAFTER(STR(?gage), "https://geoconnex.us/ref/gages/") AS ?gageId)

    # Spatial containment - LAST, on reduced dataset
    FILTER(geof:sfContains(?stateGeometry, ?gageGeometry))
}}
'''
    
    df = execute_sparql_query(query)
    
    if len(df) == 0:
        print("No gauges found in these states")
        return None
    
    gdf = df_to_gdf(df)
    print(f"Found {len(gdf)} total gauges in {len(states)} state(s)")
    
    return gdf

def find_gauges_on_river(river_gdf, gauges_gdf, buffer_meters=15):
    """Find gauges that intersect with the buffered river."""
    print(f"\n=== Step 4: Finding gauges within {buffer_meters}m of river ===")
    
    # Project to a suitable CRS for buffering (Web Mercator for approximate meters)
    # For Ohio area, could use UTM Zone 17N (EPSG:32617), but Web Mercator works for approximate buffer
    river_projected = river_gdf.to_crs("EPSG:3857")
    gauges_projected = gauges_gdf.to_crs("EPSG:3857")
    
    # Apply buffer to river
    river_buffered = river_projected.copy()
    river_buffered['geometry'] = river_projected.geometry.buffer(buffer_meters)
    
    # Find gauges that intersect the buffered river
    gauges_on_river = gauges_projected[gauges_projected.intersects(river_buffered.unary_union)]
    
    # Convert back to original CRS
    gauges_on_river = gauges_on_river.to_crs("EPSG:4326")
    
    return gauges_on_river

def get_gages_on_river(river_name, buffer_size=20):
    """
    Find all stream gauges on a specific river using a buffer.
    
    Args:
        river_name (str): Name of the river (e.g., "Scioto River", "Ohio River")
        buffer_size (int): Buffer distance in meters (default: 20)
    
    Returns:
        GeoDataFrame: GeoDataFrame containing all gauges within the buffer of the river,
                     or None if no gauges are found
    
    Example:
        >>> gauges = get_gages_on_river("Scioto River", buffer_size=15)
        >>> print(f"Found {len(gauges)} gauges")
    """
    print(f"Finding all gauges on {river_name} using a {buffer_size}m buffer")
    print("=" * 70)
    
    # Step 1: Get river geometry
    river_gdf = get_river_geometry(river_name)
    
    # Step 2: Find states the river flows through
    states = get_states_for_river(river_name)
    
    if not states:
        print(f"No states found for {river_name}")
        return None
    
    # Step 3: Get all gauges in those states
    gauges_gdf = get_gauges_in_states(states)
    
    if gauges_gdf is None or len(gauges_gdf) == 0:
        print(f"No gauges found in states where {river_name} flows")
        return None
    
    # Step 4: Filter to gauges within buffer of river
    gauges_on_river = find_gauges_on_river(river_gdf, gauges_gdf, buffer_size)
    
    # Display results
    print("\n" + "=" * 70)
    print(f"RESULTS: Found {len(gauges_on_river)} gauges on {river_name}")
    print("=" * 70)
    
    if len(gauges_on_river) > 0:
        print(f"\nGauges on {river_name}:")
        for idx, row in gauges_on_river.iterrows():
            print(f"  - {row['gageName']} (ID: {row['gageId']})")
            print(f"    Location: {row.geometry.y:.6f}°N, {row.geometry.x:.6f}°W")
    else:
        print("\nNo gauges found within the buffer zone of the river.")
        return None
    
    return gauges_on_river

def main():
    """Main function - example usage of get_gages_on_river()."""
    # Example: Find gauges on Scioto River with 15m buffer
    gauges = get_gages_on_river("Scioto River", buffer_size=15)
    
    if gauges is not None and len(gauges) > 0:
        # Save to file
        output_file = "scioto_river_gauges.geojson"
        gauges.to_file(output_file, driver="GeoJSON")
        print(f"\nResults saved to: {output_file}")
    
    return gauges

if __name__ == "__main__":
    result = main()
```

### Notes:

- Qlever (used by FRINK) has very limited support for geospatial functions.
- It doesn't support geof:distance(?gageGeometry, ?riverGeometry, unit:KiloM).
- Use the spatial functions in the examples only. Other functions do not exist in Qlevel.
