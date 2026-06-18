---
name: transboundary-monitoring-points
description: >-
  Retrieve the GRANDE-U transboundary groundwater monitoring wells (one row
  per well) as a GeoPandas GeoDataFrame in EPSG:4326. Use whenever the user
  asks where wells are, how deep they are, which aquifer they tap, whether a
  well is confined or karst, well lithology, ground altitude, or counts /
  locations of monitoring points across Ukraine, Poland, Lithuania, Latvia,
  Estonia, the United States or Mexico — including the Rio Grande / El Paso /
  Ciudad Juarez / Mesilla–Conejos-Medanos border area. Trigger on any of those
  country / region names or the word "transboundary". Do NOT use this skill for
  Italian wells (the Po basin, Lombardy, Piedmont / Piemonte, Emilia-Romagna) —
  those are served by `po-wells` and `er-well-registry`. This is the static
  per-well inventory; for water-level observations over time use the
  companion skill `transboundary-groundwater-timeseries`. Loads a bundled
  parquet, builds Point geometry from WGS84 coordinates, and returns one row
  per well ready to filter, map, or save as GeoJSON.
---

# Transboundary Groundwater — Monitoring Points (MP) Skill

This skill loads the **monitoring-point inventory** of the GRANDE-U
transboundary groundwater compilation: **305 wells across 7 countries** in
two regions — the Baltic / Eastern-European group (Ukraine, Poland,
Lithuania, Latvia, Estonia) and the **US–Mexico Rio Grande** border
(United States, Mexico). It returns a single **GeoPandas GeoDataFrame** in
EPSG:4326 with one Point per well, ready to filter, map, or save as GeoJSON.

It is the **static companion** to `transboundary-groundwater-timeseries`:
this skill answers *where / how deep / what aquifer*; the time-series skill
answers *how the water level changed over time*. Join the two on `well_ID`.

## What the data is

Each row is one groundwater monitoring well, with location and
well/aquifer metadata. Wells per country:

| Country | code | wells |
|---|---|---|
| Ukraine | UA | 124 |
| Mexico | MX | 60 |
| Latvia | LV | 52 |
| Poland | PL | 27 |
| Lithuania | LT | 19 |
| United States | US | 15 |
| Estonia | EE | 8 |
| **Total** | | **305** (299 unique IDs — see UA duplicates below) |

## Two bundled parquets — clean vs faithful

The data ships as two parquet files built from the per-country source CSVs
(see `data/DATA_NOTES.md` for the full merge log):

| File | Use |
|---|---|
| `data/transboundary_mp_clean.parquet` | **Default.** Typed and normalised — decimal commas fixed, booleans/flags parsed, IDs stripped, EPSG codes parsed, a lithology typo corrected, a duplicate column dropped. |
| `data/transboundary_mp_faithful.parquet` | Raw string values exactly as delivered (only headers harmonised + `country`/`source_file` added). Use only to audit an original value. |

The loader uses the **clean** file by default. Every transformation is
traceable to `DATA_NOTES.md`.

## Unified schema / data dictionary (clean)

After `load_monitoring_points()` runs, every well is one row:

| Column | Type | Meaning |
|---|---|---|
| `well_ID` | str | Well identifier (country-prefixed, e.g. `LV_12222`) |
| `country` | str | ISO-ish code: `UA PL LT LV EE US MX` |
| `country_name` | str | Full country name |
| `Long_WGS84` / `Lat_WGS84` | float | Longitude / latitude, WGS84 (EPSG:4326) |
| `Long_local` / `Lat_local` | float | National-grid coords — **only EE, LT, PL**; blank elsewhere |
| `EPSG_local` | Int64 | EPSG code of the local grid (e.g. 2180 PL, 3346 LT, 3301 EE) |
| `ground_altitude` | float | Land-surface elevation, m a.s.l. |
| `well_depth` | float | Borehole depth, m (sparse for MX — 1 of 60) |
| `open_from` / `open_to` | float | Screened interval top / bottom, m |
| `pumping` | boolean | Pumped well? (nullable) |
| `aquifer_thickness` | float | Aquifer thickness, m |
| `aquifer_lithology` | str | `carbonate`, `terrigenic`, `overburden`, `organic`, or combinations |
| `aquifer_karst` | boolean | Karst aquifer? (nullable) |
| `confinement` | boolean | Confined aquifer? (nullable; **all-null for MX**) |
| `greatest_permeability_zone` | float | **UA only** |
| `distance_to_nearest_river_m` | float | **UA only** |
| `gw_level_data_from` / `gw_level_data_to` | float | Year.month bounds of this well's record (e.g. `2009.01`) |
| `temporal_data_resolution` | str | Only MX states it (`annual`); blank elsewhere |
| `avg_gw_abs` | float | Mean absolute water level, m a.s.l. (UA: only 58 of 124) |
| `source_file` | str | Originating CSV |
| `geometry` | Point | Well location, EPSG:4326 (None for 11 wells with no coords) |

CRS: `EPSG:4326`. Coordinates are already WGS84 lon/lat — **no
reprojection needed**; project to a metric CRS only for distance work.

## Honest handling of the data's quirks

Do not paper over these — surface them when relevant:

- **11 wells have no coordinates** (all Ukraine). The loader sets their
  `geometry` to `None`; they appear in tabular results but not on the map.
  Exclude them with `mp[mp.geometry.notna()]` before any spatial operation.
- **6 duplicate `well_ID`s in Ukraine** (`UA_RDS_S237-?`, `UA_RDS_Sp1-?` …
  `UA_RDS_Sp4-?`, `UA_RDS_Sp10-?`). The `-?` marks an *unknown* well number;
  they could not be confirmed as the same well, so they are **left as-is**.
  Use `drop_duplicates("well_ID")` only with this caveat in mind.
- **Mexico metadata is sparse**: `well_depth` present for only 1 of 60
  wells, `confinement` entirely absent, no local coordinates. MX wells are
  best treated as location + lithology + altitude only.
- **Country-specific columns**: `greatest_permeability_zone` and
  `distance_to_nearest_river_m` exist only for Ukraine; `Long_local`/
  `Lat_local` only for EE/LT/PL. Expect nulls elsewhere — that is data
  structure, not data loss.
- **Not directly comparable across countries**: each national program
  measured and classified wells with its own methods. Treat cross-country
  comparisons (e.g. "deepest well overall") as indicative, and always state
  which country a value comes from.

## Standard loader

```python
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

SKILL_DATA = "skills/transboundary-monitoring-points/data"

def load_monitoring_points(version: str = "clean") -> gpd.GeoDataFrame:
    """Load all 305 transboundary monitoring wells as a GeoDataFrame (EPSG:4326).

    version="clean"   -> typed/normalised (default, use this for analysis)
    version="faithful"-> raw string values as delivered (audit only)
    """
    df = pd.read_parquet(f"{SKILL_DATA}/transboundary_mp_{version}.parquet")
    # Coerce coords to numeric so this works for the clean (float) and the
    # faithful (raw string, incl. Latvia's decimal comma) parquet alike.
    lon = pd.to_numeric(df["Long_WGS84"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    lat = pd.to_numeric(df["Lat_WGS84"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    geom = [Point(x, y) if pd.notna(x) and pd.notna(y) else None
            for x, y in zip(lon, lat)]
    return gpd.GeoDataFrame(df, geometry=gpd.GeoSeries(geom, crs="EPSG:4326"))
```

A single call returns the full inventory; subsequent steps filter it.

## Saving for the map

The WEN-OKN UI auto-loads any GeoJSON dropped into the session temp
directory. Drop rows with null geometry before writing:

```python
import os
os.makedirs(temp_dir, exist_ok=True)
out = os.path.join(temp_dir, "transboundary_wells.geojson")
gdf[gdf.geometry.notna()].to_file(out, driver="GeoJSON")
```

## Example queries (verified against the bundled data)

### All monitoring wells

```python
gdf = load_monitoring_points()
gdf[gdf.geometry.notna()].to_file(os.path.join(temp_dir, "all_wells.geojson"), driver="GeoJSON")
print(len(gdf), "wells;", gdf.country_name.value_counts().to_dict())
# 305 wells; {'Ukraine':124,'Mexico':60,'Latvia':52,'Poland':27,'Lithuania':19,'United States':15,'Estonia':8}
```

### Deepest wells (borehole depth)

```python
gdf = load_monitoring_points()
deepest = gdf.nlargest(5, "well_depth")
print(deepest[["well_ID","country_name","well_depth","aquifer_lithology"]])
# LV_2908 (Latvia, 347 m, carbonate), LV_24318 (338 m), MX_PM-6 (333.87 m),
# US_4904106 (332.23 m), LV_9636 (270 m).
```

### Wells tapping a karst aquifer

```python
gdf = load_monitoring_points()
karst = gdf[gdf.aquifer_karst == True]
karst[karst.geometry.notna()].to_file(os.path.join(temp_dir, "karst_wells.geojson"), driver="GeoJSON")
print(len(karst), karst.country_name.value_counts().to_dict())
# 17 wells: {'Lithuania':9,'Latvia':4,'Ukraine':3,'Poland':1}
```

### How many wells within 50 km of El Paso / Ciudad Juarez

```python
gdf = load_monitoring_points()
target = gpd.GeoSeries([Point(-106.485, 31.759)], crs="EPSG:4326").to_crs(3857).iloc[0]
m = gdf[gdf.geometry.notna()].to_crs(3857)
near = m[m.geometry.distance(target) <= 50_000].to_crs(4326)
print(len(near), near.country_name.value_counts().to_dict())
# 39 wells within 50 km: {'Mexico':30,'United States':9}
```

### Confined wells in Latvia, with depth and lithology

```python
gdf = load_monitoring_points()
lv = gdf[(gdf.country == "LV") & (gdf.confinement == True)]
print(len(lv), "confined LV wells")
print(lv[["well_ID","well_depth","aquifer_lithology"]].head())
# 28 confined wells in Latvia.
```

### Wells in one country (e.g. Estonia), full inventory map

```python
gdf = load_monitoring_points()
ee = gdf[gdf.country == "EE"]
ee.to_file(os.path.join(temp_dir, "estonia_wells.geojson"), driver="GeoJSON")
```

## Provenance — name the source file when reporting

Every reported value traces to a country source CSV via the `source_file`
column. Use the bare filename. The mapping is uniform: a value for a UA well
comes from `UA_MP_20260615.csv`, a PL well from `PL_MP_20250903.csv`,
LT `LT_MP_20250903.csv`, LV `UL_MP_20250903.csv`, EE `UT_MP_20250903.csv`,
US `US_MP_20260303.csv`, MX `MX_MP_20250930.csv` (note LV/EE files carry the
`UL_`/`UT_` prefix — University of Latvia / Tartu — not `LV_`/`EE_`).

When the user asks where a value came from, asks about reproducibility, or
asks about data sources, cite `source_file` and, for any normalised value,
point to `data/DATA_NOTES.md` (e.g. "Latvia coordinates use a decimal comma
in the raw file; converted in the clean parquet").

## Reporting tips

- Always state the **country**; cross-country comparisons are indicative only.
- `well_depth` = borehole depth; `aquifer_thickness` = aquifer thickness;
  `ground_altitude` and `avg_gw_abs` are elevations in m a.s.l. — don't mix
  "depth" (down from surface) with "level" (elevation).
- `aquifer_karst`, `confinement`, `pumping` are **nullable booleans** — filter
  with `== True` / `== False`, and remember `confinement` is all-null for MX.
- For "how deep is the water" (depth to water table over time) use the
  companion skill `transboundary-groundwater-timeseries`, not this one.
- Mention missing coordinates / sparse MX metadata when they affect an answer.
