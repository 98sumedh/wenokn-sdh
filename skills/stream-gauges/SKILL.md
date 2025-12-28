---
name: stream-gauge
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

SELECT DISTINCT ?gageName ?gageGeometry
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

SELECT DISTINCT ?gageName ?gageGeometry
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

### Example 3: Find Dam by Name

**User Request:** "Find Deer Creek Dam" or "Find dam named Deer Creek"

**Complete Code:**

```python
import sparql_dataframe
import geopandas as gpd
from shapely import wkt

# SPARQL query with name filtering
query = '''
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

SELECT ?damName ?damGeometry ?damDescription
WHERE {  
    ?dam a schema:Place;
         schema:provider "https://nid.usace.army.mil"^^<https://schema.org/url>;
         schema:name ?damName;
         schema:description ?damDescription;
         geo:hasGeometry/geo:asWKT ?damGeometry.
    FILTER(STRSTARTS(STR(?dam), "https://geoconnex.us/ref/gages/"))
    
    # Filter by name (case-insensitive prefix match)
    FILTER(STRSTARTS(LCASE(STR(?damName)), LCASE("Deer Creek")))
}
LIMIT 10
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
print(f"Found {len(gdf)} gages matching 'Deer Creek'")
for _, row in gdf.iterrows():
    print(f"- {row['damName']}")
    print(f"  Description: {row['damDescription']}")
```

**Key Points:**
- Uses `STRSTARTS` for case-insensitive prefix matching
- No spatial filtering needed for name-based queries
- Returns dam name, geometry, and description
- Use LIMIT to avoid returning too many results

---

