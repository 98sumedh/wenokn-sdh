"""
FRS Facilities Utilities

Pre-validated functions for querying EPA's Facility Registry Service (FRS)
data from the SAWGraph knowledge graph.

DO NOT MODIFY THIS FILE - Functions are validated against specific SPARQL endpoints.
"""

import json
import requests
import geopandas as gpd
import sparql_dataframe
from shapely import wkt
from shapely.ops import linemerge
from shapely.geometry import Point

def load_FRS_facilities(state: str, naics_name: str, limit: int = 1000) -> gpd.GeoDataFrame:
    """
    Load FRS facilities for a specified state and NAICS industry.
    
    This function queries the SAWGraph knowledge graph via SPARQL endpoint
    to retrieve EPA FRS facility data with geometries.

    Args:
        state: State name (e.g., "California", "Texas", "New York")
        naics_name: NAICS industry name - must be from ALLOWED_NAICS list:
            - Waste Treatment and Disposal
            - Converted Paper Manufacturing
            - Water Supply and Irrigation
            - Sewage Treatment
            - Plastics Product Manufacturing
            - Textile and Fabric Finishing and Coating
            - Basic Chemical Manufacturing
            - Paint, Coating, and Adhesive Manufacturing
            - Aerospace Product and Parts
            - Drycleaning and Laundry Services
            - Carpet and Upholstery Cleaning Services
            - Solid Waste Landfill
        limit: Maximum number of facilities to retrieve (default: 1000)

    Returns:
        GeoDataFrame with facility geometries and attributes including:
        - facilityName: Name of the facility
        - industryCodes: Industry classifications (comma-separated if multiple)
        - geometry: Point geometry in EPSG:4326

    Raises:
        ValueError: If state or NAICS name is not in the allowed lists

    Example:
        >>> sewage = load_FRS_facilities("California", "Sewage Treatment")
        >>> print(f"Found {len(sewage)} facilities")
        >>> print(sewage.head())
    """

    # Validate inputs
    ALLOWED_NAICS = [
        "Waste Treatment and Disposal",
        "Converted Paper Manufacturing",
        "Water Supply and Irrigation",
        "Sewage Treatment",
        "Plastics Product Manufacturing",
        "Textile and Fabric Finishing and Coating",
        "Basic Chemical Manufacturing",
        "Paint, Coating, and Adhesive Manufacturing",
        "Aerospace Product and Parts",
        "Drycleaning and Laundry Services",
        "Carpet and Upholstery Cleaning Services",
        "Solid Waste Landfill",
    ]

    if naics_name not in ALLOWED_NAICS:
        raise ValueError(f"Invalid NAICS '{naics_name}'. Allowed: {ALLOWED_NAICS}")

    # Map all US state names to FIPS codes
    STATE_FIPS = {
        "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
        "California": "06", "Colorado": "08", "Connecticut": "09", "Delaware": "10",
        "Florida": "12", "Georgia": "13", "Hawaii": "15", "Idaho": "16",
        "Illinois": "17", "Indiana": "18", "Iowa": "19", "Kansas": "20",
        "Kentucky": "21", "Louisiana": "22", "Maine": "23", "Maryland": "24",
        "Massachusetts": "25", "Michigan": "26", "Minnesota": "27", "Mississippi": "28",
        "Missouri": "29", "Montana": "30", "Nebraska": "31", "Nevada": "32",
        "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35", "New York": "36",
        "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40",
        "Oregon": "41", "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45",
        "South Dakota": "46", "Tennessee": "47", "Texas": "48", "Utah": "49",
        "Vermont": "50", "Virginia": "51", "Washington": "53", "West Virginia": "54",
        "Wisconsin": "55", "Wyoming": "56",
        # Territories
        "District of Columbia": "11", "Puerto Rico": "72", "Virgin Islands": "78",
        "Guam": "66", "American Samoa": "60", "Northern Mariana Islands": "69"
    }
    
    if state not in STATE_FIPS:
        raise ValueError(f"Invalid state '{state}'. Must be a valid US state or territory name.")
    
    state_fips = STATE_FIPS[state]
    
    # Updated endpoint URL
    endpoint_url = "https://frink.apps.renci.org/fiokg/sparql"

    # Updated SPARQL query with new namespace prefixes and filtering logic
    # The double braces {{ }} are f-string escapes that become single braces in SPARQL
    query = f"""
PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX frs: <http://w3id.org/fio/v1/epa-frs#>
PREFIX fio: <http://w3id.org/fio/v1/fio#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

SELECT DISTINCT 
    ?facilityName
    (GROUP_CONCAT(DISTINCT ?industryCode; separator=", ") AS ?industryCodes)
    ?facilityWKT
WHERE {{
    ?facility a frs:FRS-Facility ;
              rdfs:label ?facilityName ;
              fio:ofIndustry/rdfs:label ?industryCode ;
              geo:hasGeometry/geo:asWKT ?facilityWKT;
              kwg-ont:sfWithin ?county .
    FILTER(CONTAINS(LCASE(?industryCode), LCASE("{naics_name}"))) .
    FILTER(STRSTARTS(STR(?county), "http://stko-kwg.geog.ucsb.edu/lod/resource/administrativeRegion.USA.{state_fips}")) .
    FILTER(STRLEN(STR(?county)) = 73) .
}} 
GROUP BY ?facilityName ?facilityWKT ?industryCode
LIMIT {limit}
"""    
    # Execute query and process results
    df = sparql_dataframe.get(endpoint_url, query)
    df = df.dropna(subset=["facilityWKT"]).copy()
    df["geometry"] = df["facilityWKT"].apply(wkt.loads)
    df = df.drop(columns=["facilityWKT"])

    # Return as GeoDataFrame with WGS84 coordinate system
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
