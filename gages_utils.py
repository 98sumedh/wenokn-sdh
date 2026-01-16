import requests
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt
import sparql_dataframe

# SPARQL endpoint for GeoConnex
GEOCONNEX_ENDPOINT = "https://frink.apps.renci.org/federation/sparql"

def get_river_geometry_from_geoconnex(river_name):
    """Get river geometry from GeoConnex using SPARQL."""
    print(f"Step 1: Getting geometry for {river_name} from GeoConnex...")
    
    # Braces are already escaped here with {{ }}
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
    try:
        df = sparql_dataframe.get(GEOCONNEX_ENDPOINT, query)
        if len(df) == 0:
            raise ValueError(f"River '{river_name}' not found in GeoConnex")
        
        wkt_col = None
        for col in df.columns:
            if any(x in col.lower() for x in ['geometry', 'geom', 'wkt']):
                wkt_col = col
                break
        
        df['geometry'] = df[wkt_col].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
        print(f"  ✓ Found river: {gdf.iloc[0]['riverName']}")
        return gdf
    except Exception as e:
        raise ValueError(f"Error getting river geometry: {e}")

def get_states_for_river(river_name):
    """Find all states that a river flows through using GeoConnex SPARQL."""
    print(f"Step 2: Finding states that {river_name} flows through...")
    
    # FIXED: Doubled the curly braces to {{ and }} so Python f-strings ignore them
    query = f'''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>

SELECT DISTINCT ?stateName 
WHERE {{
  ?river rdf:type hyf:HY_FlowPath ;
         schema:name "{river_name}" ;
         kwg-ont:sfCrosses ?s2cell .

  ?s2cell rdf:type kwg-ont:S2Cell_Level13 .

  ?state rdf:type kwg-ont:AdministrativeRegion_1 ;
         rdfs:label ?stateName .

  ?s2cell kwg-ont:sfWithin | kwg-ont:sfOverlaps ?state .

  FILTER(STRSTARTS(STR(?state), STR(kwgr:)))
  FILTER(STRLEN(?stateName) > 2)
}}
'''
    try:
        df = sparql_dataframe.get(GEOCONNEX_ENDPOINT, query)
        states = df['stateName'].tolist()
        if not states:
            print("  ! Could not find states via spatial query.")
            return None
        print(f"  ✓ Found {len(states)} states: {', '.join(states)}")
        return states
    except Exception as e:
        print(f"  ! Error finding states: {e}")
        return None

def get_state_codes_from_names(state_names):
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
    return [state_mapping[n.lower()] for n in state_names if n.lower() in state_mapping]

def get_usgs_gauges_by_states(state_codes):
    print(f"Step 3: Getting active USGS stream gauges from {len(state_codes)} states...")
    all_gauges = {}
    for state_code in state_codes:
        url = "https://waterservices.usgs.gov/nwis/iv/"
        params = {
            "stateCd": state_code,
            "parameterCd": "00060,00065",
            "siteType": "ST",
            "siteStatus": "active",
            "format": "json"
        }
        try:
            resp = requests.get(url, params=params, timeout=60)
            data = resp.json()
            for ts in data.get('value', {}).get('timeSeries', []):
                site = ts['sourceInfo']
                site_code = site['siteCode'][0]['value']
                if site_code not in all_gauges:
                    all_gauges[site_code] = {
                        'usgs_site_no': site_code,
                        'site_name': site['siteName'],
                        'latitude': float(site['geoLocation']['geogLocation']['latitude']),
                        'longitude': float(site['geoLocation']['geogLocation']['longitude']),
                        'current_flow_cfs': None,
                        'current_stage_ft': None,
                        'geometry': Point(float(site['geoLocation']['geogLocation']['longitude']), 
                                          float(site['geoLocation']['geogLocation']['latitude']))
                    }
                
                # Extract values
                values = ts.get('values', [{}])[0].get('value', [])
                if values:
                    val = float(values[-1]['value'])
                    p_code = ts['variable']['variableCode'][0]['value']
                    if p_code == '00060': all_gauges[site_code]['current_flow_cfs'] = val
                    elif p_code == '00065': all_gauges[site_code]['current_stage_ft'] = val
        except Exception: continue
    return gpd.GeoDataFrame(list(all_gauges.values()), crs="EPSG:4326")

def find_gauges_near_river(river_gdf, gauges_gdf, buffer_meters):
    print(f"Step 4: Finding gauges within {buffer_meters}m of river...")
    river_proj = river_gdf.to_crs("EPSG:3857")
    gauges_proj = gauges_gdf.to_crs("EPSG:3857")
    river_buffer = river_proj.geometry.buffer(buffer_meters).unary_union
    on_river = gauges_proj[gauges_proj.intersects(river_buffer)]
    return on_river.to_crs("EPSG:4326")

def get_gages_on_river(river_name, buffer_size=500):
    print(f"\n{'='*70}\nAnalyzing {river_name}\n{'='*70}")
    river_gdf = get_river_geometry_from_geoconnex(river_name)
    state_names = get_states_for_river(river_name)
    if state_names:
        codes = get_state_codes_from_names(state_names)
        gauges_gdf = get_usgs_gauges_by_states(codes)
    else:
        # Fallback to bounding box if state query fails
        from pygeohydro import NWIS
        print("Using bounding box fallback...")
        bbox = river_gdf.total_bounds
        gauges_gdf = get_usgs_gauges_by_bbox(bbox[0], bbox[1], bbox[2], bbox[3])
    
    results = find_gauges_near_river(river_gdf, gauges_gdf, buffer_size)
    print(f"Found {len(results)} gauges on {river_name}.")
    return results

if __name__ == "__main__":
    get_gages_on_river("Scioto River", buffer_size=200)
