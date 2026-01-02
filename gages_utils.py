"""
Pre-validated functions for querying streamflow gages.

DO NOT MODIFY THIS FILE - Functions are validated against specific SPARQL endpoints.

Complete implementation to find stream gauges on any river.

This script combines:
1. GeoConnex SPARQL to get river geometry
2. USGS Water Services API to get active stream gauges
3. Spatial buffering to find gauges near the river

Usage:
    gauges = get_gages_on_river("Scioto River", buffer_size=500)
    gauges = get_gages_on_river("Ohio River", buffer_size=1000)
"""

import requests
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt
import sparql_dataframe

# SPARQL endpoint for GeoConnex
GEOCONNEX_ENDPOINT = "https://frink.apps.renci.org/federation/sparql"

def get_river_geometry_from_geoconnex(river_name):
    """
    Get river geometry from GeoConnex using SPARQL.
    
    Args:
        river_name (str): Name of the river (e.g., "Scioto River", "Ohio River")
    
    Returns:
        GeoDataFrame: River geometry as LineString/MultiLineString
    """
    print(f"Step 1: Getting geometry for {river_name} from GeoConnex...")
    
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
    
    try:
        df = sparql_dataframe.get(GEOCONNEX_ENDPOINT, query)
        
        if len(df) == 0:
            raise ValueError(f"River '{river_name}' not found in GeoConnex")
        
        # Find geometry column
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
        
        # Convert to GeoDataFrame
        df = df.dropna(subset=[wkt_col]).copy()
        df['geometry'] = df[wkt_col].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
        
        print(f"  ✓ Found river: {gdf.iloc[0]['riverName']}")
        return gdf
        
    except Exception as e:
        raise ValueError(f"Error getting river geometry: {e}")


def get_states_for_river(river_name):
    """
    Find all states that a river flows through using GeoConnex.
    
    Args:
        river_name (str): Name of the river
    
    Returns:
        list: List of state names
    """
    print(f"Step 2: Finding states that {river_name} flows through...")
    
    query = f'''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
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
    
    try:
        df = sparql_dataframe.get(GEOCONNEX_ENDPOINT, query)
        states = df['stateName'].tolist()
        
        if not states:
            # Fallback: get states from river bounding box
            print("  ! Could not find states via spatial query, using bounding box fallback")
            return None
        
        print(f"  ✓ Found {len(states)} states: {', '.join(states)}")
        return states
        
    except Exception as e:
        print(f"  ! Error finding states: {e}")
        return None


def get_state_codes_from_names(state_names):
    """
    Convert state names to 2-letter codes.
    
    Args:
        state_names (list): List of state names (e.g., ["Ohio", "Kentucky"])
    
    Returns:
        list: List of 2-letter state codes (e.g., ["OH", "KY"])
    """
    state_mapping = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
        "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
        "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
        "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
        "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
        "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
        "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
        "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
        "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
        "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
        "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
        "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
        "wisconsin": "WI", "wyoming": "WY"
    }
    
    codes = []
    for name in state_names:
        code = state_mapping.get(name.lower())
        if code:
            codes.append(code)
    
    return codes


def get_usgs_gauges_by_states(state_codes):
    """
    Get active USGS stream gauges from multiple states with both flow and stage data.
    
    Args:
        state_codes (list): List of 2-letter state codes (e.g., ["OH", "KY"])
    
    Returns:
        GeoDataFrame: Combined gauges from all states with flow and stage data
    """
    print(f"Step 3: Getting active USGS stream gauges from {len(state_codes)} states...")
    
    all_gauges = {}  # Use dict to group by site
    
    for state_code in state_codes:
        url = "https://waterservices.usgs.gov/nwis/iv/"
        
        params = {
            "stateCd": state_code,
            "parameterCd": "00060,00065",  # Both discharge and gage height
            "siteType": "ST",  # Stream only
            "siteStatus": "active",
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Process each timeSeries entry
            for ts in data.get('value', {}).get('timeSeries', []):
                site = ts['sourceInfo']
                site_code = site['siteCode'][0]['value']
                
                # Initialize site entry if not exists
                if site_code not in all_gauges:
                    all_gauges[site_code] = {
                        'usgs_site_no': site_code,
                        'site_name': site['siteName'],
                        'latitude': float(site['geoLocation']['geogLocation']['latitude']),
                        'longitude': float(site['geoLocation']['geogLocation']['longitude']),
                        'state': state_code,
                        'current_flow_cfs': None,
                        'current_stage_ft': None,
                        'flow_time': None,
                        'stage_time': None,
                        'geometry': Point(
                            float(site['geoLocation']['geogLocation']['longitude']),
                            float(site['geoLocation']['geogLocation']['latitude'])
                        )
                    }
                
                # Get parameter code and current value
                variable = ts.get('variable', {})
                param_code = variable.get('variableCode', [{}])[0].get('value', '')
                
                current_value = None
                current_time = None
                if 'values' in ts and len(ts['values']) > 0:
                    values_list = ts['values'][0].get('value', [])
                    if len(values_list) > 0:
                        latest = values_list[-1]
                        current_value = latest.get('value')
                        current_time = latest.get('dateTime')
                
                # Store value based on parameter code
                if param_code == '00060' and current_value:  # Discharge
                    all_gauges[site_code]['current_flow_cfs'] = float(current_value)
                    all_gauges[site_code]['flow_time'] = current_time
                elif param_code == '00065' and current_value:  # Gage height
                    all_gauges[site_code]['current_stage_ft'] = float(current_value)
                    all_gauges[site_code]['stage_time'] = current_time
            
            state_count = len([g for g in all_gauges.values() if g['state'] == state_code])
            print(f"  ✓ {state_code}: {state_count} gauges")
            
        except Exception as e:
            print(f"  ! Error fetching {state_code} gauges: {e}")
            continue
    
    if not all_gauges:
        return gpd.GeoDataFrame()
    
    gauge_list = list(all_gauges.values())
    gdf = gpd.GeoDataFrame(gauge_list, crs="EPSG:4326")
    print(f"  ✓ Total: {len(gdf)} active stream gauges")
    return gdf


def get_usgs_gauges_by_bbox(west, south, east, north):
    """
    Get active USGS stream gauges in a bounding box with both flow and stage data.
    
    Args:
        west, south, east, north (float): Bounding box coordinates
    
    Returns:
        GeoDataFrame: Active stream gauges with flow and stage data
    """
    print(f"Step 3: Getting active USGS stream gauges in bounding box...")
    print(f"  Bounds: [{west:.4f}, {south:.4f}, {east:.4f}, {north:.4f}]")
    
    url = "https://waterservices.usgs.gov/nwis/iv/"
    
    params = {
        "bBox": f"{west},{south},{east},{north}",
        "parameterCd": "00060,00065",  # Both discharge and gage height
        "siteType": "ST",
        "siteStatus": "active",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        all_gauges = {}  # Use dict to group by site
        
        for ts in data.get('value', {}).get('timeSeries', []):
            site = ts['sourceInfo']
            site_code = site['siteCode'][0]['value']
            
            # Initialize site entry if not exists
            if site_code not in all_gauges:
                all_gauges[site_code] = {
                    'usgs_site_no': site_code,
                    'site_name': site['siteName'],
                    'latitude': float(site['geoLocation']['geogLocation']['latitude']),
                    'longitude': float(site['geoLocation']['geogLocation']['longitude']),
                    'current_flow_cfs': None,
                    'current_stage_ft': None,
                    'flow_time': None,
                    'stage_time': None,
                    'geometry': Point(
                        float(site['geoLocation']['geogLocation']['longitude']),
                        float(site['geoLocation']['geogLocation']['latitude'])
                    )
                }
            
            # Get parameter code and current value
            variable = ts.get('variable', {})
            param_code = variable.get('variableCode', [{}])[0].get('value', '')
            
            current_value = None
            current_time = None
            if 'values' in ts and len(ts['values']) > 0:
                values_list = ts['values'][0].get('value', [])
                if len(values_list) > 0:
                    latest = values_list[-1]
                    current_value = latest.get('value')
                    current_time = latest.get('dateTime')
            
            # Store value based on parameter code
            if param_code == '00060' and current_value:  # Discharge
                all_gauges[site_code]['current_flow_cfs'] = float(current_value)
                all_gauges[site_code]['flow_time'] = current_time
            elif param_code == '00065' and current_value:  # Gage height
                all_gauges[site_code]['current_stage_ft'] = float(current_value)
                all_gauges[site_code]['stage_time'] = current_time
        
        gauge_list = list(all_gauges.values())
        gdf = gpd.GeoDataFrame(gauge_list, crs="EPSG:4326")
        print(f"  ✓ Found {len(gdf)} active stream gauges")
        return gdf
        
    except Exception as e:
        print(f"  ! Error fetching gauges: {e}")
        return gpd.GeoDataFrame()


def find_gauges_near_river(river_gdf, gauges_gdf, buffer_meters):
    """
    Find gauges within buffer distance of river using spatial intersection.
    
    Args:
        river_gdf (GeoDataFrame): River geometry
        gauges_gdf (GeoDataFrame): All gauges in the area
        buffer_meters (int): Buffer distance in meters
    
    Returns:
        GeoDataFrame: Gauges within buffer of river
    """
    print(f"Step 4: Finding gauges within {buffer_meters}m of river...")
    
    if len(gauges_gdf) == 0:
        print("  ! No gauges to filter")
        return gpd.GeoDataFrame()
    
    # Project to Web Mercator for buffering in meters
    river_projected = river_gdf.to_crs("EPSG:3857")
    gauges_projected = gauges_gdf.to_crs("EPSG:3857")
    
    # Apply buffer to river
    river_buffered = river_projected.copy()
    river_buffered['geometry'] = river_projected.geometry.buffer(buffer_meters)
    
    # Find gauges that intersect the buffered river
    gauges_on_river = gauges_projected[gauges_projected.intersects(river_buffered.unary_union)]
    
    # Convert back to WGS84
    gauges_on_river = gauges_on_river.to_crs("EPSG:4326")
    
    print(f"  ✓ Found {len(gauges_on_river)} gauges within buffer")
    
    return gauges_on_river


def estimate_buffer_size(river_gdf):
    """
    Estimate appropriate buffer size based on river geometry.
    
    Uses river length as proxy for river size:
    - Longer rivers are typically larger/wider
    - Returns recommended buffer in meters
    
    Args:
        river_gdf (GeoDataFrame): River geometry
    
    Returns:
        int: Recommended buffer size in meters
    """
    # Calculate total river length in meters
    river_projected = river_gdf.to_crs("EPSG:3857")
    total_length = river_projected.geometry.length.sum()
    
    # Length-based heuristic (in meters)
    if total_length < 50000:  # < 50 km - small stream
        buffer = 100
    elif total_length < 150000:  # < 150 km - medium river
        buffer = 200
    elif total_length < 300000:  # < 300 km - large river
        buffer = 400
    else:  # >= 300 km - major river
        buffer = 800
    
    print(f"  River length: {total_length/1000:.1f} km → Recommended buffer: {buffer}m")
    return buffer


def get_gages_on_river(river_name, buffer_size=None):
    """
    Find all active USGS stream gauges on a river with both flow and stage data.
    
    This function:
    1. Gets river geometry from GeoConnex
    2. Auto-calculates appropriate buffer size based on river length (if not provided)
    3. Finds states the river flows through
    4. Gets all active USGS stream gauges in those states
    5. Filters to gauges within buffer distance of river
    
    Args:
        river_name (str): Name of the river (e.g., "Scioto River", "Ohio River")
        buffer_size (int, optional): Buffer distance in meters. 
                                     If None, automatically calculated based on river size.
                                     Recommended: let function auto-calculate for best results.
    
    Returns:
        GeoDataFrame: Active stream gauges on the river with current flow and stage data
        
        Columns:
        - usgs_site_no: USGS site number
        - site_name: Gauge name
        - latitude, longitude: Coordinates
        - current_flow_cfs: Current streamflow in cubic feet per second (None if unavailable)
        - current_stage_ft: Current gage height in feet (None if unavailable)
        - flow_time: Timestamp for flow measurement
        - stage_time: Timestamp for stage measurement
    
    Examples:
        >>> # Auto-calculate buffer (RECOMMENDED)
        >>> gauges = get_gages_on_river("Scioto River")
        
        >>> # Manual buffer size
        >>> gauges = get_gages_on_river("Ohio River", buffer_size=1000)
        
        >>> # Access results
        >>> print(f"Found {len(gauges)} gauges")
        >>> print(gauges[['usgs_site_no', 'site_name', 'current_flow_cfs', 'current_stage_ft']])
    """
    print(f"\n{'='*70}")
    print(f"Finding active stream gauges on {river_name}")
    if buffer_size is not None:
        print(f"Buffer size: {buffer_size} meters (user-specified)")
    else:
        print(f"Buffer size: Auto-calculating based on river characteristics")
    print(f"{'='*70}\n")
    
    try:
        # Step 1: Get river geometry from GeoConnex
        river_gdf = get_river_geometry_from_geoconnex(river_name)
        
        # Auto-calculate buffer size if not provided
        if buffer_size is None:
            buffer_size = estimate_buffer_size(river_gdf)
        
        # Step 2: Find states the river flows through
        state_names = get_states_for_river(river_name)
        
        # Step 3: Get gauges in those states or use bounding box
        if state_names:
            state_codes = get_state_codes_from_names(state_names)
            if state_codes:
                gauges_gdf = get_usgs_gauges_by_states(state_codes)
            else:
                print("  ! Could not convert state names to codes, using bounding box")
                bounds = river_gdf.total_bounds
                gauges_gdf = get_usgs_gauges_by_bbox(bounds[0], bounds[1], bounds[2], bounds[3])
        else:
            # Fallback: use bounding box from river
            bounds = river_gdf.total_bounds
            gauges_gdf = get_usgs_gauges_by_bbox(bounds[0], bounds[1], bounds[2], bounds[3])
        
        # Step 4: Filter to gauges near river
        gauges_on_river = find_gauges_near_river(river_gdf, gauges_gdf, buffer_size)
        
        # Display results
        print(f"\n{'='*70}")
        print(f"RESULTS: Found {len(gauges_on_river)} active gauges on {river_name}")
        print(f"{'='*70}\n")
        
        if len(gauges_on_river) > 0:
            print(f"Gauges on {river_name}:\n")
            for idx, row in gauges_on_river.iterrows():
                flow_str = f" | Flow: {row['current_flow_cfs']:.1f} cfs" if row['current_flow_cfs'] else " | Flow: N/A"
                stage_str = f" | Stage: {row['current_stage_ft']:.2f} ft" if row['current_stage_ft'] else " | Stage: N/A"
                print(f"  • {row['site_name']}")
                print(f"    ID: {row['usgs_site_no']} | Location: {row['latitude']:.6f}°N, {row['longitude']:.6f}°W{flow_str}{stage_str}")
                print()
        else:
            print("No gauges found within the buffer zone.")
            print(f"Try increasing buffer_size (current: {buffer_size}m)")
        
        print(f"{'='*70}\n")
        
        return gauges_on_river
        
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        return gpd.GeoDataFrame()


if __name__ == "__main__":
    # Example 1: Auto-calculate buffer (RECOMMENDED)
    print("Example 1: Scioto River (auto-buffer)")
    scioto_gauges = get_gages_on_river("Scioto River")
    
    print("\n" + "="*70 + "\n")
    
    # Example 2: Large river with auto-buffer
    print("Example 2: Ohio River (auto-buffer)")
    ohio_gauges = get_gages_on_river("Ohio River")
    
    print("\n" + "="*70 + "\n")
    
    # Example 3: Manual buffer override
    print("Example 3: Olentangy River (manual buffer)")
    olentangy_gauges = get_gages_on_river("Olentangy River", buffer_size=150)
    
    # Access the data
    if len(scioto_gauges) > 0:
        print("\nScioto River Gauges DataFrame:")
        print(scioto_gauges[['usgs_site_no', 'site_name', 'current_flow_cfs', 'current_stage_ft']].head())
