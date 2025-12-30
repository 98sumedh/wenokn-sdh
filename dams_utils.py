"""
Pre-validated functions for querying dams.

DO NOT MODIFY THIS FILE - Functions are validated against specific SPARQL endpoints.

Find all dams on the Scioto River using a small buffer.

This script:
1. Gets the geometry of the Scioto River
2. Finds all states the river flows through
3. Gets all dams in those states
4. Applies a small buffer (50 meters) to the river
5. Finds dams that intersect the buffered river
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
LIMIT 60
'''
    
    df = execute_sparql_query(query)
    states = df['stateName'].tolist()
    print(f"Found {len(states)} states: {', '.join(states)}")
    
    return states

def get_dams_in_states(states):
    """Get all dams in the given states."""
    print(f"\n=== Step 3: Getting all dams in states: {', '.join(states)} ===")
    
    # Create VALUES clause for states
    state_values = ' '.join([f'"{state}"' for state in states])
    
    query = f'''
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?damName ?damGeometry ?stateName
WHERE {
    # User-provided states - FILTER EARLY
    VALUES ?inputState {{ {state_values} }}
    
    # Get state geometry
    ?state rdf:type <http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1>;
           rdfs:label ?stateName;
           geo:hasGeometry/geo:asWKT ?stateGeometry.
    FILTER(STRSTARTS(STR(?state), "http://stko-kwg.geog.ucsb.edu/lod/resource/"))
    FILTER(STRSTARTS(LCASE(STR(?stateName)), LCASE(?inputState)))
    
    # Get dams
    ?dam schema:provider "https://nid.usace.army.mil"^^<https://schema.org/url>;
         schema:name ?damName;
         geo:hasGeometry/geo:asWKT ?damGeometry.
    FILTER(STRSTARTS(STR(?dam), "https://geoconnex.us/ref/dams/"))
    
    # Spatial filter - dam must be contained in state
    FILTER(geof:sfContains(?stateGeometry, ?damGeometry))
}
'''
    
    df = execute_sparql_query(query)
    
    if len(df) == 0:
        print("No dams found in these states")
        return None
    
    gdf = df_to_gdf(df)
    print(f"Found {len(gdf)} total dams in {len(states)} state(s)")
    
    return gdf

def find_dams_on_river(river_gdf, dams_gdf, buffer_meters=50):
    """Find dams that intersect with the buffered river."""
    print(f"\n=== Step 4: Finding dams within {buffer_meters}m of river ===")
    
    # Project to a suitable CRS for buffering (Web Mercator for approximate meters)
    # For Ohio area, could use UTM Zone 17N (EPSG:32617), but Web Mercator works for approximate buffer
    river_projected = river_gdf.to_crs("EPSG:3857")
    dams_projected = dams_gdf.to_crs("EPSG:3857")
    
    # Apply buffer to river
    river_buffered = river_projected.copy()
    river_buffered['geometry'] = river_projected.geometry.buffer(buffer_meters)
    
    # Find dams that intersect the buffered river
    dams_on_river = dams_projected[dams_projected.intersects(river_buffered.unary_union)]
    
    # Convert back to original CRS
    dams_on_river = dams_on_river.to_crs("EPSG:4326")
    
    return dams_on_river

def get_dams_on_river(river_name, buffer_size=50):
    """
    Find all stream dams on a specific river using a buffer.
    
    Args:
        river_name (str): Name of the river (e.g., "Scioto River", "Ohio River")
        buffer_size (int): Buffer distance in meters (default: 50)
    
    Returns:
        GeoDataFrame: GeoDataFrame containing all dams within the buffer of the river,
                     or None if no dams are found
    
    Example:
        >>> dams = get_dams_on_river("Scioto River", buffer_size=50)
        >>> print(f"Found {len(dams)} dams")
    """
    print(f"Finding all dams on {river_name} using a {buffer_size}m buffer")
    print("=" * 70)
    
    # Step 1: Get river geometry
    river_gdf = get_river_geometry(river_name)
    
    # Step 2: Find states the river flows through
    states = get_states_for_river(river_name)
    
    if not states:
        print(f"No states found for {river_name}")
        return None
    
    # Step 3: Get all dams in those states
    dams_gdf = get_dams_in_states(states)
    
    if dams_gdf is None or len(dams_gdf) == 0:
        print(f"No dams found in states where {river_name} flows")
        return None
    
    # Step 4: Filter to dams within buffer of river
    dams_on_river = find_dams_on_river(river_gdf, dams_gdf, buffer_size)
    
    # Display results
    print("\n" + "=" * 70)
    print(f"RESULTS: Found {len(dams_on_river)} dams on {river_name}")
    print("=" * 70)
    
    if len(dams_on_river) > 0:
        print(f"\nDams on {river_name}:")
        for idx, row in dams_on_river.iterrows():
            print(f"  - {row['damName']}")
            print(f"    Location: {row.geometry.y:.6f}°N, {row.geometry.x:.6f}°W")
    else:
        print("\nNo dams found within the buffer zone of the river.")
        return None
    
    return dams_on_river
