---
name: rivers
description: Use this skill for the requests related to the geometry definitions of rivers in USA; it provides a way to get the geometries of rivers as a GeoDataframe. 
---

# Rivers Skill

## MANDATORY INSTRUCTIONS - READ FIRST 

STOP! Before writing ANY code:

1. IDENTIFY your request type below
2. SCROLL to the corresponding Example number
3. READ the complete example before writing code
4. COPY the SPARQL query or function EXACTLY as written
5. REPLACE only the specific values indicated (e.g., state name, river name)

If you create your own query or logic instead of copying from examples, it WILL return incorrect results and FAIL.

## DOWNSTREAM DETECTION

If the request contains "downstream", you MUST use Example 6. 
For these requests: immediately scroll to Example 6, read it completely, then use get_downstream_segments() function.

## REQUEST TYPE MAPPING

Match your request to the pattern below, then use the specified example:

State-level rivers:
- Pattern: "all rivers in [State]"
- Use: Example 1 SPARQL (S2Cell spatial join)
- Do not use: bounding box, name filters

County-level rivers:
- Pattern: "all rivers in [County]"
- Use: Example 2 SPARQL (S2Cell spatial join)
- Do not use: bounding box, name filters

Single river by name:
- Pattern: "find [River Name]"
- Use: Example 3 SPARQL (name query)

Counties a river passes:
- Pattern: "counties [River] passes through"
- Use: Example 4 SPARQL

States a river passes:
- Pattern: "states [River] passes through"
- Use: Example 5 SPARQL

Downstream/upstream analysis:
- Pattern: see DOWNSTREAM DETECTION section above
- Use: Example 6 get_downstream_segments() function
- Do not use: manual buffering, coordinate math, cardinal directions

Proximity queries (find features within distance):
- Pattern: "[Feature A] within [X meters] of [Feature B]"
- Use: Example 7 buffer() + gpd.sjoin()
- Do not use: nested iterrows() loops (100-1000x slower)

## Description

This skill gets the geometries of rivers in USA by querying GeoConnex knowledge graph on FRINK using their names. 

## When to Use

- Find ALL rivers in a US state
- Find ALL rivers in a US county
- Find a specific river geometry by its complete name
- Find rivers with spatial relationships to other objects
- Find all counties or states a specific river flows through
- Find downstream/upstream segments from point sources (mines, facilities, etc.)

## How to Use

### Overview of Approach

All queries follow this three-step process:

1. Construct a SPARQL query (use the exact pattern for your request type from Examples below)
2. Send the SPARQL query to the FRINK endpoint
3. Convert the result to a GeoDataFrame

### Step 1: Construct a SPARQL Query

The SPARQL pattern you use depends entirely on your request type. See REQUEST TYPE MAPPING and Examples sections.

For state-level queries: You MUST use the S2Cell spatial join pattern from Example 1. DO NOT use bounding boxes, DO NOT filter by name.

For county-level queries: You MUST use the S2Cell spatial join pattern from Example 2. DO NOT use bounding boxes, DO NOT filter by name.

For single river by name: Use the pattern from Example 3.

For downstream analysis: Use the get_downstream_segments() function from Example 6. DO NOT write custom logic.

### Step 2: Send the SPARQL Query to the FRINK Endpoint

Use the library sparql_dataframe:

```python
import sparql_dataframe
endpoint_url = "https://frink.apps.renci.org/federation/sparql"
df = sparql_dataframe.get(endpoint_url, query)
```

### Step 3: Convert to GeoDataFrame

```python
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
    raise ValueError("No WKT geometry column found in SPARQL result.")

# Drop missing geometries
df = df.dropna(subset=[wkt_col]).copy()

# Convert WKT to shapely geometries
from shapely import wkt
df['geometry'] = df[wkt_col].apply(wkt.loads)

# Create GeoDataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
```

## Examples

### Example 1: Find ALL Rivers in a STATE

User Requests: 
- "Find all rivers in Kentucky"
- "Find all rivers in Ohio State"
- "Get all rivers in California"
- "What rivers are in Texas"

CRITICAL INSTRUCTIONS:

This is the REQUIRED approach for ANY request asking for all rivers in a state. 

YOU MUST:
1. Copy the SPARQL query below EXACTLY as written
2. Change ONLY the state name from "Ohio" to your target state
3. Use ALL the same prefixes, predicates, and ontology classes shown below

YOU MUST NOT:
- Use schema:State (MUST use kwg-ont:AdministrativeRegion_1)
- Use schema:BodyOfWater (MUST use hyf:HY_FlowPath and hyf:HY_WaterBody)
- Use geo:sfIntersects (MUST use kwg-ont:sfWithin, kwg-ont:sfOverlaps, kwg-ont:sfCrosses)
- Create your own SPARQL pattern
- Use bounding boxes
- Filter by river names containing the state name

If you do not copy this query EXACTLY, you will get 0 results and the query will FAIL.

SPARQL Query to Copy:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>

SELECT ?riverName ?riverGeometry
WHERE {
  {
    SELECT ?riverName (SAMPLE(?geom) AS ?riverGeometry)
    WHERE {
      # Target state (change "Ohio" to your state name)
      ?state rdf:type kwg-ont:AdministrativeRegion_1 ;
             rdfs:label "Ohio" .

      # S2 cells for the state
      ?s2cell rdf:type kwg-ont:S2Cell_Level13 ;
              kwg-ont:sfWithin | kwg-ont:sfOverlaps ?state .

      # Rivers crossing those cells
      ?river rdf:type hyf:HY_FlowPath ;
             a hyf:HY_WaterBody ;
             schema:name ?riverName ;
             kwg-ont:sfCrosses ?s2cell ;
             geo:hasGeometry/geo:asWKT ?geom .

      FILTER(STRLEN(STR(?riverName)) > 0)
    }
    GROUP BY ?riverName
  }
}
```

Step-by-Step Example for Kentucky:
1. Copy the entire query above EXACTLY as shown
2. Find this line: rdfs:label "Ohio" .
3. Change it to: rdfs:label "Kentucky" .
4. Do not change any other part of the query
5. Run the query

Notes:
- Replace "Ohio" with your target state name (e.g., "Kentucky", "California", "Texas")
- State name should be just the state name, no abbreviations
- This query may take 30+ seconds on first run; if timeout occurs, run again (FRINK caches data)

### Example 2: Find ALL Rivers in a COUNTY

User Requests:
- "Find all rivers in Ross County, Ohio"
- "Find all rivers in Jefferson County"
- "What rivers flow through Knox County, Kentucky"

CRITICAL: This is the REQUIRED approach for ANY request asking for all rivers in a county.

DO NOT use bounding boxes. DO NOT filter by river names. DO NOT attempt any other approach.

Instructions: Copy this query EXACTLY and replace the county label with your target county.

SPARQL Query:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>

SELECT ?riverName (SAMPLE(?riverGeom) AS ?riverGeometry)
WHERE {
  ?county rdf:type kwg-ont:AdministrativeRegion_2 ;
          rdfs:label "Ross County, Ohio" .

  ?s2cell rdf:type kwg-ont:S2Cell_Level13 ;
          kwg-ont:sfWithin | kwg-ont:sfOverlaps ?county .

  ?river rdf:type hyf:HY_FlowPath ;
         a hyf:HY_WaterBody ;
         schema:name ?riverName ;
         kwg-ont:sfCrosses ?s2cell ;
         geo:hasGeometry/geo:asWKT ?riverGeom .
}
GROUP BY ?riverName
```

Notes:
- County name must use format: "Ross County, Ohio" (county name with state) or "Ross County" (county name only)
- If county name alone is ambiguous, include state name
- This query may take 30+ seconds on first run; if timeout occurs, run again

### Example 3: Find a Specific River by Name

User Requests:
- "Find Muskingum River"
- "Get the geometry of Rose Creek"
- "Show me the Ohio River"

Instructions: Copy this query EXACTLY and replace {river_name} with the complete river name.

SPARQL Query:

```sparql
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

SELECT DISTINCT ?riverName ?riverGeometry 
WHERE {
  ?river a hyf:HY_FlowPath ;
         a hyf:HY_WaterBody ;
         a schema:Place ;
         schema:name ?riverName ;
         geo:hasGeometry/geo:asWKT ?riverGeometry .
  FILTER(LCASE(?riverName) = LCASE("{river_name}")) .
}
ORDER BY DESC(STRLEN(?riverGeometry))
LIMIT 1
```

Notes:
- River name must be complete: "Muskingum River", "Rose Creek", "Ohio River"
- Do not modify this query structure when querying by name
- Replace {river_name} with the actual river name

#### SPECIAL CASE: MISSOURI RIVER

Missouri River is NOT available in GeoConnex with complete geometry. If the user requests Missouri River specifically, use HyRiver instead:

```python
# ONLY for Missouri River - use HyRiver directly
from pynhd import WaterData
import geopandas as gpd

river_name = "Missouri River"

# Skip GeoConnex, go straight to HyRiver
wd = WaterData("nhdflowline_network")
flowlines = wd.byid("gnis_name", river_name)

rivers_gdf = gpd.GeoDataFrame({
    'riverName': [river_name],
    'geometry': [flowlines.union_all()]
}, crs=flowlines.crs)

print(rivers_gdf)
```

### Example 4: Find All Counties a River Passes Through

User Request: "Find all counties that Ohio River passes through"

SPARQL Query:

```sparql
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>

SELECT DISTINCT ?countyName ?countyGeometry
WHERE {
  # Find counties
  ?county rdf:type kwg-ont:AdministrativeRegion_2 ;
          rdfs:label ?countyName ;
          geo:hasGeometry/geo:asWKT ?countyGeometry .
  FILTER(STRSTARTS(STR(?county), "http://stko-kwg.geog.ucsb.edu/lod/resource/"))
  
  # Check that county intersects with the target river
  FILTER EXISTS {
    ?targetRiver rdf:type hyf:HY_FlowPath ;
                 a hyf:HY_WaterBody ;
                 schema:name "Ohio River" ;
                 kwg-ont:sfCrosses ?s2cell1 .
    ?s2cell1 rdf:type kwg-ont:S2Cell_Level13 ;
             kwg-ont:sfWithin | kwg-ont:sfOverlaps ?county .
  }
}
```

Notes:
- Replace "Ohio River" with your target river name
- Returns all counties that intersect with the river

### Example 5: Find All States a River Passes Through

User Request: "Find all states that Ohio River passes through"

SPARQL Query:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX kwgr: <http://stko-kwg.geog.ucsb.edu/lod/resource/>
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>

SELECT DISTINCT ?stateName ?stateGeometry
WHERE {
  # The target river
  ?river rdf:type hyf:HY_FlowPath ;
         a hyf:HY_WaterBody ;
         schema:name "Ohio River" ;
         kwg-ont:sfCrosses ?s2cell ;
         geo:hasGeometry/geo:asWKT ?riverGeometry .

  # S2 cells crossed by the river
  ?s2cell rdf:type kwg-ont:S2Cell_Level13 .

  # States that overlap those S2 cells
  ?state rdf:type kwg-ont:AdministrativeRegion_1 ;
         rdfs:label ?stateName ;
         geo:hasGeometry/geo:asWKT ?stateGeometry .

  ?s2cell kwg-ont:sfWithin | kwg-ont:sfOverlaps ?state .

  FILTER(STRSTARTS(STR(?state), STR(kwgr:)))
  FILTER(STRLEN(?stateName) > 2)
}
```

Notes:
- Replace "Ohio River" with your target river name
- Returns all states that intersect with the river

### Example 6: Downstream Analysis - Find Regions Downstream from Point Sources

User Requests:
- "Find census tracts downstream from coal mines within 1000 meters"
- "Find counties downstream from dams within 2000 meters"
- "What regions are downstream from power plants within 3km"
- "Tracts intersecting downstream segment of river with mines within 1000m"

CRITICAL DEFINITION

A region (e.g., census tract) qualifies if and only if:
1. There exists at least one river R
2. There exists at least one point source P (e.g., coal mine) within X meters of river R
3. The region intersects the downstream segment of river R starting from P's projection onto R

ALGORITHM

1. Buffer point sources: Create X-meter buffer around each point source
2. Find rivers with nearby sources: For each river, identify ALL point sources whose buffers intersect that river
3. For each river with at least one nearby source:
   - Project all nearby sources onto the river
   - Find the most upstream projection (minimum distance from river start)
   - Split the river at the most upstream projection point
   - Keep only the portion from that point to river end (downstream segment)
4. Check region qualification: A region qualifies if it intersects ANY of the downstream segments

Key Clarifications:
- "Within X meters" means Euclidean distance from point source to river ≤ X meters
- Multiple sources on same river: Use the most upstream projection as split point
- Multiple rivers: A region qualifies if it meets criteria for ANY river (OR logic)
- Flow direction: Rivers flow from first coordinate to last coordinate in LineString geometry

MANDATORY FUNCTION - Copy this EXACTLY:

```python
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import substring

def get_downstream_segments(rivers_gdf: gpd.GeoDataFrame,
                            points_gdf: gpd.GeoDataFrame,
                            distance: float) -> gpd.GeoDataFrame:
    """
    Find downstream segments of rivers that have nearby points.

    For each river, finds all points within the specified distance. If multiple
    points are near a river, uses the upmost (furthest upstream) point to determine
    where downstream begins. Returns the portion of each river from that point
    to its end.

    Args:
        rivers_gdf: GeoDataFrame with MultiLineString or LineString river geometries.
                    Lines should be oriented in flow direction (start = upstream).
        points_gdf: GeoDataFrame with Point geometries.
        distance: Distance threshold in meters. Points within this distance of a river
                  will trigger downstream extraction for that river.

    Returns:
        GeoDataFrame with downstream river segments. Includes columns:
        - 'river_id': index or identifier of the source river
        - 'downstream_geom': the downstream line segment geometry
        - 'upmost_point_idx': index of the point that defines the downstream start
        - 'upmost_point_geom': the point geometry used
        - 'distance_to_river': distance from upmost point to river
        - 'position_along_river': position of upmost point along river (0-1 normalized)
    """
    print(f"Finding downstream segments within {distance}m of points...")

    # Ensure we're working with projected CRS for accurate distance calculations
    if rivers_gdf.crs.is_geographic:
        print("  Warning: Rivers CRS is geographic. Converting to EPSG:3857 for distance calculations.")
        rivers_proj = rivers_gdf.to_crs(epsg=3857)
        points_proj = points_gdf.to_crs(epsg=3857)
        input_was_geographic = True
    else:
        rivers_proj = rivers_gdf.copy()
        points_proj = points_gdf.copy()
        input_was_geographic = False

    downstream_segments = []

    for river_idx, river in rivers_proj.iterrows():
        river_geom = river.geometry

        # Handle both LineString and MultiLineString
        if isinstance(river_geom, MultiLineString):
            lines = list(river_geom.geoms)
        elif isinstance(river_geom, LineString):
            lines = [river_geom]
        else:
            print(f"  Skipping river {river_idx}: not a line geometry")
            continue

        # Find all points within distance of this river
        nearby_points = []
        for pt_idx, point in points_proj.iterrows():
            point_geom = point.geometry

            # For MultiLineString, check distance to each component
            if isinstance(river_geom, MultiLineString):
                min_dist = min(point_geom.distance(line) for line in lines)
            else:
                min_dist = point_geom.distance(river_geom)

            if min_dist <= distance:
                nearby_points.append({
                    'idx': pt_idx,
                    'geom': point_geom,
                    'distance': min_dist
                })

        if not nearby_points:
            continue

        # Find the upmost point (minimum position along the line)
        upmost_point = None
        upmost_position = float('inf')
        upmost_line_idx = 0
        upmost_line = None
        upmost_projected_point = None

        for pt_info in nearby_points:
            pt_geom = pt_info['geom']

            # For MultiLineString, find which line segment the point is closest to
            if isinstance(river_geom, MultiLineString):
                for line_idx, line in enumerate(lines):
                    projected_dist = line.project(pt_geom)
                    line_length = line.length

                    if line_length > 0:
                        normalized_position = projected_dist / line_length
                    else:
                        normalized_position = 0

                    # Check if this is the upmost (smallest position = most upstream)
                    if normalized_position < upmost_position:
                        upmost_position = normalized_position
                        upmost_point = pt_info
                        upmost_line_idx = line_idx
                        upmost_line = line
                        upmost_projected_point = line.interpolate(projected_dist)
            else:
                # Single LineString
                line = river_geom
                projected_dist = line.project(pt_geom)
                line_length = line.length

                if line_length > 0:
                    normalized_position = projected_dist / line_length
                else:
                    normalized_position = 0

                if normalized_position < upmost_position:
                    upmost_position = normalized_position
                    upmost_point = pt_info
                    upmost_line_idx = 0
                    upmost_line = line
                    upmost_projected_point = line.interpolate(projected_dist)

        # Extract downstream segment from the upmost point
        if upmost_line is not None and upmost_position < 1.0:
            try:
                start_dist = upmost_line.project(upmost_projected_point)
                end_dist = upmost_line.length

                # Add small buffer to start_dist to avoid including the point itself
                start_dist = min(start_dist + 0.001, end_dist)

                downstream_geom = substring(upmost_line, start_dist, end_dist)

                if downstream_geom and not downstream_geom.is_empty:
                    downstream_segments.append({
                        'river_id': river_idx,
                        'downstream_geom': downstream_geom,
                        'upmost_point_idx': upmost_point['idx'],
                        'upmost_point_geom': upmost_point['geom'],
                        'distance_to_river': upmost_point['distance'],
                        'position_along_river': upmost_position
                    })

                    print(f"  River {river_idx}: downstream segment from point {upmost_point['idx']}")
            except Exception as e:
                print(f"  River {river_idx}: error extracting downstream: {e}")

    # Create result GeoDataFrame
    if downstream_segments:
        result = pd.DataFrame(downstream_segments)
        result_gdf = gpd.GeoDataFrame(
            result,
            geometry='downstream_geom',
            crs=rivers_proj.crs
        )

        # Convert back to original CRS if input was geographic
        if input_was_geographic:
            result_gdf = result_gdf.to_crs(rivers_gdf.crs)

        print(f"\nFound {len(result_gdf)} downstream segments")
        return result_gdf
    else:
        print(f"\nNo downstream segments found (no points within {distance}m of rivers)")
        # Return empty GeoDataFrame with correct structure
        empty_df = pd.DataFrame(columns=[
            'river_id', 'downstream_geom', 'upmost_point_idx',
            'upmost_point_geom', 'distance_to_river', 'position_along_river'
        ])
        return gpd.GeoDataFrame(
            empty_df,
            geometry='downstream_geom',
            crs=rivers_gdf.crs
        )
```

COMPLETE USAGE EXAMPLE:

```python
import sparql_dataframe
import geopandas as gpd
from shapely import wkt

# Step 1: Get rivers in the region (use Example 1 or 2)
query = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX kwg-ont: <http://stko-kwg.geog.ucsb.edu/lod/ontology/>
PREFIX hyf: <https://www.opengis.net/def/schema/hy_features/hyf/>
PREFIX schema: <https://schema.org/>

SELECT ?riverName ?riverGeometry
WHERE {
  {
    SELECT ?riverName (SAMPLE(?geom) AS ?riverGeometry)
    WHERE {
      ?state rdf:type kwg-ont:AdministrativeRegion_1 ;
             rdfs:label "Ohio" .
      ?s2cell rdf:type kwg-ont:S2Cell_Level13 ;
              kwg-ont:sfWithin | kwg-ont:sfOverlaps ?state .
      ?river rdf:type hyf:HY_FlowPath ;
             a hyf:HY_WaterBody ;
             schema:name ?riverName ;
             kwg-ont:sfCrosses ?s2cell ;
             geo:hasGeometry/geo:asWKT ?geom .
      FILTER(STRLEN(STR(?riverName)) > 0)
    }
    GROUP BY ?riverName
  }
}
'''

endpoint_url = "https://frink.apps.renci.org/federation/sparql"
df = sparql_dataframe.get(endpoint_url, query)

wkt_col = [c for c in df.columns if 'geom' in c.lower()][0]
df = df.dropna(subset=[wkt_col]).copy()
df['geometry'] = df[wkt_col].apply(wkt.loads)
rivers_gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# Step 2: Get point sources (coal mines, dams, etc.)
points_gdf = ...  # Load your point sources

# Step 3: Get downstream segments using the mandatory function
downstream_segments = get_downstream_segments(
    rivers_gdf=rivers_gdf,
    points_gdf=points_gdf,
    distance=1000  # 1000 meters
)

# Step 4: Find regions intersecting downstream segments
regions_gdf = ...  # Load your regions (census tracts, counties, etc.)
qualifying_regions = regions_gdf[
    regions_gdf.intersects(downstream_segments.unary_union)
]
```

WRONG APPROACHES - DO NOT USE:

DO NOT buffer points and intersect with full rivers:
```python
# WRONG - This finds nearby rivers, NOT downstream segments
buffered = points.buffer(1000)
nearby_rivers = rivers[rivers.intersects(buffered.unary_union)]
result = regions[regions.intersects(nearby_rivers.unary_union)]
```

DO NOT manually manipulate coordinates:
```python
# WRONG - Cannot determine flow or split correctly
coords = list(river.coords)
split_point = coords[len(coords)//2]
```

DO NOT assume downstream based on cardinal directions:
```python
# WRONG - Rivers do not flow based on north/south/east/west
downstream = river[river.y < point.y]
```

DO NOT use line.interpolate without proper projection:
```python
# WRONG - Does not account for point position or flow
split_geom = river.interpolate(0.5, normalized=True)
```

RIGHT APPROACH:
```python
# CORRECT - Use get_downstream_segments() function
downstream_segments = get_downstream_segments(rivers_gdf, points_gdf, distance)
qualifying_regions = regions_gdf[regions_gdf.intersects(downstream_segments.unary_union)]
```

Notes:
- Rivers flow from first coordinate to last coordinate in LineString
- For MultiLineString rivers, function processes each component separately
- Distance must be in meters when using projected CRS (EPSG:3857)
- The function automatically handles CRS conversion if needed

### Example 7: Performance Optimization - Find Features Within Distance

User Requests:
- "Find rivers with NPDES facilities within 1000 meters"
- "Find coal mines within 2000 meters of rivers"
- "Find census tracts near rivers"
- Any request asking "what [features] are within [distance] of [other features]"

CRITICAL PERFORMANCE RULE

For simple proximity queries (find features within distance of other features), ALWAYS use the spatial join optimization with buffer() and gpd.sjoin(). This is 100-1000x faster than nested loops.

SLOW APPROACH - DO NOT USE:
```python
# SLOW - O(n × m) complexity with nested loops
for river_idx, river in rivers.iterrows():
    for fac_idx, facility in facilities.iterrows():
        dist = facility.geometry.distance(river.geometry)
        if dist <= 1000:
            nearby.append(fac_idx)
```

FAST APPROACH - USE THIS INSTEAD:
```python
# FAST - O((n + m) × log(n)) with R-tree spatial index
import geopandas as gpd

# Convert to projected CRS for accurate distance (meters)
rivers_proj = rivers.to_crs(epsg=3857)
facilities_proj = facilities.to_crs(epsg=3857)

# Step 1: Create buffer around features (converts "within distance" to "intersects buffer")
facility_buffers = facilities_proj.buffer(1000)
buffer_gdf = gpd.GeoDataFrame(geometry=facility_buffers, crs=facilities_proj.crs)

# Step 2: Spatial join uses R-tree index internally - MUCH faster
rivers_near_facilities = gpd.sjoin(
    rivers_proj,
    buffer_gdf,
    how='inner',
    predicate='intersects'
)

# Get unique river indices that have facilities nearby
rivers_with_nearby_facilities = rivers_near_facilities.index.unique().tolist()
result_rivers = rivers.loc[rivers_with_nearby_facilities]
```

TEMPLATE FOR ANY PROXIMITY QUERY:
```python
# Template: Find A within distance of B
# 1. Convert to projected CRS (epsg=3857 for meters)
a_proj = a_gdf.to_crs(epsg=3857)
b_proj = b_gdf.to_crs(epsg=3857)

# 2. Create buffer around B (the thing you're measuring distance FROM)
b_buffers = b_proj.buffer(distance_in_meters)
buffer_gdf = gpd.GeoDataFrame(geometry=b_buffers, crs=b_proj.crs)

# 3. Spatial join - finds A that intersects B's buffers
result = gpd.sjoin(a_proj, buffer_gdf, how='inner', predicate='intersects')

# 4. Map back to original indices if needed
result_indices = result.index.unique().tolist()
result_gdf = a_gdf.loc[result_indices]
```

SPECIFIC TEMPLATES:

Template: Find POINTS within distance of LINES (e.g., facilities near rivers):
```python
# Buffer the LINES, then join with POINTS
river_buffers = rivers.to_crs(epsg=3857).buffer(1000)
nearby_facilities = gpd.sjoin(
    facilities.to_crs(epsg=3857),
    gpd.GeoDataFrame(geometry=river_buffers, crs="EPSG:3857"),
    how='inner',
    predicate='intersects'
)
```

Template: Find LINES within distance of POINTS (e.g., rivers near facilities):
```python
# Buffer the POINTS, then join with LINES
facility_buffers = facilities.to_crs(epsg=3857).buffer(1000)
nearby_rivers = gpd.sjoin(
    rivers.to_crs(epsg=3857),
    gpd.GeoDataFrame(geometry=facility_buffers, crs="EPSG:3857"),
    how='inner',
    predicate='intersects'
)
```

Template: Find POLYGONS intersecting other features (e.g., tracts near rivers):
```python
# Either buffer the lines OR use intersects directly (for polygons)
# Method 1: Buffer approach (for "within distance")
river_buffers = rivers.to_crs(epsg=3857).buffer(distance)
nearby_tracts = gpd.sjoin(
    tracts.to_crs(epsg=3857),
    gpd.GeoDataFrame(geometry=river_buffers, crs="EPSG:3857"),
    how='inner',
    predicate='intersects'
)

# Method 2: Direct intersect (for "touches/overlaps")
nearby_tracts = gpd.sjoin(
    tracts.to_crs(epsg=3857),
    rivers.to_crs(epsg=3857),
    how='inner',
    predicate='intersects'
)
```

WHEN TO USE BUFFER + SJOIN vs get_downstream_segments():
- Use buffer() + sjoin(): Simple "find nearby features" (no flow direction needed)
- Use get_downstream_segments(): Need actual downstream segments (flow direction matters)

Examples:
- "Rivers with facilities within 1000m" → buffer + sjoin
- "Tracts downstream from mines" → get_downstream_segments
- "Mines near rivers" → buffer + sjoin
- "Counties intersecting downstream segments" → buffer + sjoin (after getting segments)

## Common Pitfalls - DO NOT MAKE THESE MISTAKES

### PITFALL 1: Using intersects WITHOUT buffer on line geometries

WRONG - Points rarely exactly intersect lines:
```python
# WRONG - This will return 0 or very few results!
points_near_rivers = gpd.sjoin(
    points_gdf.to_crs(epsg=3857),
    gpd.GeoDataFrame(geometry=rivers_gdf.to_crs(epsg=3857).geometry, crs="EPSG:3857"),
    how='inner',
    predicate='intersects'  # Points don't exactly touch line geometries!
)
```

CORRECT - Always buffer when finding features within distance:
```python
# CORRECT - Buffer the rivers, then find points within that buffer
river_buffers = rivers_gdf.to_crs(epsg=3857).buffer(distance)
points_near_rivers = gpd.sjoin(
    points_gdf.to_crs(epsg=3857),
    gpd.GeoDataFrame(geometry=river_buffers, crs="EPSG:3857"),
    how='inner',
    predicate='intersects'
)
```

RULE: When using `predicate='intersects'` for proximity queries, ONE side must be a buffer. Points intersect lines only if they exactly touch - which almost never happens.

### PITFALL 2: Reversing the query without adjusting buffer logic

When you need BOTH "A near B" AND "B near A", you must buffer the CORRECT side:

WRONG - Reverses the query but forgets to buffer the lines:
```python
# Step 1: Find rivers near facilities (CORRECT)
facility_buffers = facilities.to_crs(epsg=3857).buffer(1000)
rivers_near_facilities = gpd.sjoin(rivers.to_crs(epsg=3857), buffer_gdf, ...)

# Step 2: Find facilities near rivers (WRONG - no buffer!)
facilities_near_rivers = gpd.sjoin(
    facilities.to_crs(epsg=3857),
    gpd.GeoDataFrame(geometry=rivers.to_crs(epsg=3857).geometry, ...),
    predicate='intersects'  # Wrong! Points don't intersect lines!
)
```

CORRECT - Buffer the appropriate side for each query:
```python
# Step 1: Find rivers near facilities
facility_buffers = facilities.to_crs(epsg=3857).buffer(1000)
rivers_near_facilities = gpd.sjoin(rivers.to_crs(epsg=3857), buffer_gdf, ...)

# Step 2: Find facilities near rivers
river_buffers = rivers.to_crs(epsg=3857).buffer(1000)
facilities_near_rivers = gpd.sjoin(facilities.to_crs(epsg=3857), buffer_gdf, ...)
```

### PITFALL 3: Fetching too much data from APIs (causes 500 errors)

When fetching census data, do NOT fetch all data then filter:

WRONG:
```python
# WRONG - Fetches ALL census tracts in US (100,000+ rows) - API will error!
all_tracts = client.observations_dataframe(
    variable_dcids=["Median_Income_Person"],
    entity_type='CensusTract',
    parent_entity='country/USA',  # Too much!
    date='latest'
)
# Then filter to Kentucky...
ky_tracts = all_tracts[all_tracts['state_fips'] == '21']
```

CORRECT - Fetch only the data you need:
```python
# CORRECT - Build list of specific entity DCIDs you need
tract_dcids = [f"geoId/{geoid}" for geoid in kentucky_tracts['GEOID']]
ky_tracts_income = client.observations_dataframe(
    variable_dcids=["Median_Income_Person"],
    entity_dcids=tract_dcids,  # Only Kentucky tracts
    date='latest'
)
```

RULE: Always filter BEFORE fetching from APIs. Use specific entity IDs, not broad filters like `parent_entity='country/USA'`.

## Common Mistakes to Avoid

WRONG: Using Bounding Box Queries

DO NOT do this for "find all rivers in Kentucky":
```python
bbox = get_state_bbox("Kentucky")
rivers = query_rivers_in_bbox(bbox)
```

Why wrong: Bounding boxes are rectangular and don't match state/county boundaries. This will include rivers outside the target region and miss rivers in concave boundary areas.

WRONG: Filtering by Name

DO NOT do this for "find all rivers in Kentucky":
```sparql
SELECT ?riverName ?riverGeometry
WHERE {
  ?river schema:name ?riverName ;
         geo:hasGeometry/geo:asWKT ?riverGeometry .
  FILTER(CONTAINS(LCASE(?riverName), "kentucky"))
}
```

Why wrong: Most rivers don't have the state/county name in their name. This will miss the vast majority of rivers.

WRONG: Using Non-Existent SPARQL Functions

DO NOT attempt to use functions not shown in examples:
```sparql
FILTER(geof:sfIntersects(?river, ?state))
BIND("<POLYGON(...)>"^^geo:wktLiteral AS ?geom)
```

Why wrong: FRINK/Qlevel has very limited geospatial function support. Only use patterns shown in the examples above.

WRONG: Custom Downstream Logic

DO NOT invent your own downstream logic:
```python
buffered = points.buffer(1000)
nearby_rivers = rivers[rivers.intersects(buffered.unary_union)]
downstream = nearby_rivers  # This is not downstream, just nearby
```

Why wrong: This does not account for actual river flow direction, proper point projection, or the concept of "most upstream" point when multiple sources exist.

RIGHT: Use S2Cell Spatial Join for Regions

CORRECT approach for "find all rivers in Kentucky":
```sparql
?state rdf:type kwg-ont:AdministrativeRegion_1 ;
       rdfs:label "Kentucky" .
?s2cell kwg-ont:sfWithin | kwg-ont:sfOverlaps ?state .
?river kwg-ont:sfCrosses ?s2cell .
```

Why right: This uses the S2Cell indexing system that FRINK supports, ensuring accurate spatial relationships.

RIGHT: Use get_downstream_segments() for Downstream

CORRECT approach for downstream analysis:
```python
downstream_segments = get_downstream_segments(rivers_gdf, points_gdf, distance=1000)
qualifying_regions = regions_gdf[regions_gdf.intersects(downstream_segments.unary_union)]
```

Why right: This function correctly identifies downstream segments by projecting points onto rivers, finding the most upstream point, and extracting the segment from that point to the river end.

## Important Notes

River Flow Direction: The river flow direction is determined by the coordinate order in the LineString geometry - rivers flow from the first coordinate to the last coordinate.

Function Limitations: Any functions not appearing in the example SPARQL queries do not exist in FRINK. FRINK is implemented on top of Qlevel; Qlevel provides only very limited geospatial support. Do not attempt to use any other functions not shown in the examples.

WKT Literal Conversion: FRINK/Qlevel doesn't support "<string>"^^geo:wktLiteral, i.e., you can't convert a string into a WKT literal.

Query Performance: Finding all rivers in a county or a state may take more than 30 seconds. When encountering a 30-second timeout, run the same query again because FRINK/Qlevel may cache the data and the second query can be processed much faster.

Downstream/Upstream Analysis: To find all downstream/upstream counties of a river starting from a specific object near the river, use the get_downstream_segments() function from Example 6 to first calculate the downstream segment, then check which counties intersect that segment.

## Pre-Execution Validation

Before running code for any request, verify:

For State/County River Queries:
- I am using the EXACT SPARQL query from Example 1 or 2
- I am only changing the state/county name
- I am NOT using bounding boxes
- I am NOT filtering by river names
- I am NOT using schema:State or schema:BodyOfWater

For Downstream Analysis:
- I read Example 6 completely
- I copied the get_downstream_segments() function EXACTLY as shown
- I am NOT buffering points and intersecting with full rivers
- I am NOT writing my own coordinate splitting logic
- I am NOT assuming downstream means south/east/lower coordinates
- I understand: downstream = from most upstream nearby point to river end
- My final step is: regions[regions.intersects(downstream_segments.unary_union)]

For Proximity Queries (find features within distance):
- I read Example 7 completely
- I am using buffer() + gpd.sjoin() pattern from Example 7
- I am NOT using nested iterrows() loops
- I converted to projected CRS (epsg=3857) for accurate distance
- My pattern is: buffer_b = b.to_crs(epsg=3857).buffer(distance); result = gpd.sjoin(a_proj, buffer_gdf, ...)
- CRITICAL: When finding POINTS near LINES, I buffer the LINES (not vice versa)
- CRITICAL: I am NOT using `predicate='intersects'` on raw line geometries with points
- CRITICAL: When fetching API data (census, income, etc.), I filter BEFORE fetching (specific IDs, not `parent_entity='country/USA'`)
