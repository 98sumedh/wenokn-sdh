import sparql_dataframe
import geopandas as gpd
from shapely import wkt
import pandas as pd
from pynhd import GeoConnex

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
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    return gdf

def get_river_geometry(river_name):
    """Get the geometry of a river by name via SPARQL."""
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
ORDER BY DESC(STRLEN(STR(?riverGeometry)))
LIMIT 1
'''
    df = execute_sparql_query(query)
    if len(df) == 0:
        raise ValueError(f"River '{river_name}' not found")
    gdf = df_to_gdf(df)
    print(f"Found river: {gdf.iloc[0]['riverName']}")
    return gdf

def find_dams_on_river(river_gdf, dams_gdf, buffer_meters=200):
    """Find dams that intersect with the buffered river."""
    print(f"\n=== Step 4: Finding dams within {buffer_meters}m of river ===")
    
    # Project to EPSG:3857 (Web Mercator) to use meters for buffering
    river_projected = river_gdf.to_crs("EPSG:3857")
    dams_projected = dams_gdf.to_crs("EPSG:3857")
    
    # Apply buffer to river
    river_buffered = river_projected.copy()
    river_buffered['geometry'] = river_projected.geometry.buffer(buffer_meters)
    
    # Create a single union shape of the buffered river segments
    river_union = river_buffered.geometry.unary_union
    
    # Filter dams that intersect the buffered area
    dams_on_river = dams_projected[dams_projected.intersects(river_union)]
    
    # Return to WGS84 coordinates
    return dams_on_river.to_crs("EPSG:4326")

def get_dams_on_river(river_name, buffer_size=200):
    """
    Main workflow to find dams on a specific river using GeoConnex.
    """
    print(f"Finding all dams on {river_name} using a {buffer_size}m buffer")
    print("=" * 70)
    
    # Step 1: Get river geometry
    river_gdf = get_river_geometry(river_name)
    
    # Step 2: Get the bounding box of the river geometry
    bbox = tuple(river_gdf.total_bounds)
    print(f"River bounding box identified: {bbox}")
    
    # Step 3: Get all dams in that bounding box using GeoConnex
    print("\n=== Step 3: Fetching dams from GeoConnex ===")
    gcx = GeoConnex("dams")
    try:
        # Querying the dams collection by bounding box
        dams_gdf = gcx.bybox(bbox, 4326)
    except Exception as e:
        print(f"Error fetching dams from GeoConnex: {e}")
        return None
    
    if dams_gdf is None or dams_gdf.empty:
        print(f"No dams found in the bounding box area.")
        return None
    
    print(f"Retrieved {len(dams_gdf)} candidate dams within the bounding box.")
    
    # Step 4: Filter dams to those within the precision buffer
    dams_on_river = find_dams_on_river(river_gdf, dams_gdf, buffer_size)        
    return dams_on_river

if __name__ == "__main__":
    # Execute for Scioto River
    results = get_dams_on_river("Muskingum River", buffer_size=200)
