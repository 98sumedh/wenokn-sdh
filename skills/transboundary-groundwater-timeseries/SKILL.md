---
name: transboundary-groundwater-timeseries
description: >-
  Retrieve the GRANDE-U transboundary groundwater water-level time series as
  a pandas DataFrame: 28,125 periodic observations across 281 monitoring
  wells in Ukraine, Poland, Lithuania, Latvia, Estonia, the United States
  and Mexico, spanning 1965–2025. Use whenever the user asks how groundwater
  / the water table changed over time — trends, seasonal cycles, wettest /
  driest months, year-over-year change, "when did X happen", deepest /
  highest water level since a given year, single-well history, or which
  wells swing the most — for any of those seven countries (trigger on their
  names or "transboundary"). Do NOT use for Italian time series (Piemonte / Po
  basin) — use `po-wells-timeseries` for those. This is the time-axis companion
  to `transboundary-monitoring-points` (join on well_ID for depth / aquifer /
  location). Loads a bundled parquet — no network at runtime.
---

# Transboundary Groundwater — Time Series (GWTS) Skill

This skill exposes **28,125 groundwater water-level observations** across
**281 wells in 7 countries**, spanning **1965–2025**. It is the **time-axis
companion** to `transboundary-monitoring-points`: that skill returns one
static row per well (location, depth, aquifer); this one returns the
time-stamped water-level readings and answers questions about *when* and
*how* the water table changed. Join the two on `well_ID`.

The data ships as a bundled parquet — the loader reads it directly from
disk with **no network dependency at query time**.

## What the data is

Each row is one periodic water-level reading at a well:

- **`gw_level_from_ground`** — depth from ground surface down to the water,
  in meters. **Small = water near surface (wet); large = water deep (dry /
  pumped).** Negative values are valid (artesian / confined wells flowing
  above ground; 93 such rows).
- **`gw_level_abs`** — absolute water-level elevation, m above sea level.
- Observations are **monthly** for most countries; **Mexico is mostly annual**
  (only 61% of MX rows carry a month).

Coverage per country:

| Country | rows | years | cadence |
|---|---|---|---|
| Latvia | 8,908 | 2000–2023 | monthly |
| Ukraine | 5,266 | 2000–2025 | monthly |
| Lithuania | 4,937 | 1965–2024 | monthly |
| Poland | 4,703 | 2009–2023 | monthly |
| United States | 2,308 | 2000–2024 | monthly |
| Estonia | 1,638 | 1995–2023 | monthly |
| Mexico | 365 | 1999–2021 | mostly annual |

## Two bundled parquets — clean vs faithful

| File | Use |
|---|---|
| `data/transboundary_gwts_clean.parquet` | **Default.** Typed — IDs stripped, decimal commas fixed (Latvia), year/month as integers, levels as floats. |
| `data/transboundary_gwts_faithful.parquet` | Raw string values as delivered (only headers harmonised + `country`/`source_file` added). Audit only. |

See `data/DATA_NOTES.md` for the full merge log.

## Unified schema / data dictionary (clean)

| Column | Type | Meaning |
|---|---|---|
| `well_ID` | str | Well identifier — join key to `transboundary-monitoring-points` |
| `country` / `country_name` | str | `UA PL LT LV EE US MX` / full name |
| `observation_year` | Int64 | Year of reading |
| `observation_month` | Int64 | Month 1–12 (**null for 141 rows**, mostly MX annual) |
| `gw_level_abs` | float | Water-level elevation, m a.s.l. (7.6 – 1211.1) |
| `gw_level_from_ground` | float | Depth to water below ground, m (−0.74 – 111.45) |
| `ground_altitude` | float | **MX only** — per-row land-surface elevation (null elsewhere) |
| `source_file` | str | Originating CSV |

## Honest handling of the data's quirks

- **Mexico is annual**, not monthly: 39% of MX rows have no `observation_month`.
  Do monthly/seasonal analysis on monthly countries; for MX use the year only.
- **Different time spans and cadences** across countries (table above) — a
  raw cross-country average mixes eras and is misleading. Aggregate **within**
  a country/period, and state the window you used.
- **Not every series well has metadata.** The MP↔GWTS join is clean for PL,
  LT, LV, EE, US; **Ukraine is only partial** (60 of 118 MP wells have a
  series, and 40 series wells have no MP record), and **Mexico** has 2 series
  wells absent from MP. When joining to `transboundary-monitoring-points`,
  use `how="left"` and report wells with no metadata rather than dropping them.
- **Negative `gw_level_from_ground`** (93 rows) is real — confined/artesian
  wells where water rises above ground. Do not clip to zero.
- `ground_altitude` is present only because the Mexican file repeats it per
  row; it duplicates the MP value and is null for all other countries.

## Standard loader

```python
import os
import pandas as pd

SKILL_DATA = "skills/transboundary-groundwater-timeseries/data"

def load_timeseries(version: str = "clean") -> pd.DataFrame:
    """Load all 28,125 transboundary water-level observations.

    version="clean"    -> typed (default)
    version="faithful" -> raw strings as delivered (audit only)
    """
    return pd.read_parquet(f"{SKILL_DATA}/transboundary_gwts_{version}.parquet")

def load_with_metadata(version: str = "clean") -> pd.DataFrame:
    """Time series left-joined to monitoring-point metadata (depth, aquifer…)."""
    ts = load_timeseries(version)
    mp = pd.read_parquet(
        "skills/transboundary-monitoring-points/data/transboundary_mp_clean.parquet")
    cols = ["well_ID","well_depth","aquifer_lithology","aquifer_karst",
            "confinement","Long_WGS84","Lat_WGS84"]
    return ts.merge(mp[cols], on="well_ID", how="left")
```

## Example queries (verified against the bundled data)

### Groundwater-level history for one Latvian well

```python
ts = load_timeseries()
well = "LV_9695"
h = ts[ts.well_ID == well].sort_values(["observation_year","observation_month"])
print(f"{well}: {len(h)} obs, {int(h.observation_year.min())}-{int(h.observation_year.max())}")
# LV_9695: 285 obs, 2000-2023.
```

### When did Latvia have its deepest basin-wide water table since 2000?

```python
ts = load_timeseries()
lv = ts[(ts.country == "LV") & (ts.observation_year >= 2000)].dropna(subset=["gw_level_from_ground"])
g = lv.groupby(["observation_year","observation_month"])["gw_level_from_ground"].mean()
y, m = g.idxmax()
print(f"Deepest basin-wide water table: {int(y)}-{int(m):02d} at {g.max():.2f} m below ground")
# 2006-02, mean 10.06 m below ground.
```

### Seasonal cycle of a Polish well — wettest vs driest months

```python
ts = load_timeseries()
pw = ts[ts.well_ID == "PL_I_495_1"].dropna(subset=["gw_level_from_ground"])
m = pw.groupby("observation_month")["gw_level_from_ground"].mean()
print(f"Wettest month {int(m.idxmin())} ({m.min():.2f} m); driest month {int(m.idxmax())} ({m.max():.2f} m)")
# Wettest = April (2.05 m to water); driest = September (2.39 m).
```

### How has the average depth to water in Estonia changed year over year?

```python
ts = load_timeseries()
ee = ts[ts.country == "EE"].dropna(subset=["gw_level_from_ground"])
yoy = ee.groupby("observation_year")["gw_level_from_ground"].mean().round(2)
print(yoy)
# Deepening trend: 1995 ~3.68 m -> 2021 ~23.17 m -> 2023 ~22.73 m below ground.
```

### Most variable wells (largest water-level swings), with depth and aquifer type

```python
df = load_with_metadata()
swing = (df.dropna(subset=["gw_level_from_ground"])
           .groupby("well_ID")["gw_level_from_ground"]
           .agg(lambda s: s.max() - s.min())
           .sort_values(ascending=False).head(5).rename("swing_m").reset_index())
swing = swing.merge(df[["well_ID","country_name","well_depth","aquifer_lithology"]].drop_duplicates(),
                    on="well_ID", how="left")
print(swing)
# Largest swings are US Mesilla wells: US_4904476 (29.22 m), US_315712106361803 (23.62 m), …
```

### Map the wells behind a time-series result

```python
# After computing a per-well result `swing`, attach coordinates from MP and save GeoJSON.
import geopandas as gpd
from shapely.geometry import Point
mp = pd.read_parquet("skills/transboundary-monitoring-points/data/transboundary_mp_clean.parquet")
out = swing.merge(mp[["well_ID","Long_WGS84","Lat_WGS84"]], on="well_ID", how="left").dropna(subset=["Long_WGS84"])
g = gpd.GeoDataFrame(out, geometry=[Point(x,y) for x,y in zip(out.Long_WGS84, out.Lat_WGS84)], crs="EPSG:4326")
os.makedirs(temp_dir, exist_ok=True)
g.to_file(os.path.join(temp_dir, "variable_wells.geojson"), driver="GeoJSON")
```

## Provenance — name the source file when reporting

Each row carries its `source_file`. Per country: UA `UA_GWTS_20250516.csv`,
PL `PL_GWTS_20250311_corrected.csv` (the corrected file), LT
`LT_GWTS_20250219.csv`, LV `UL_GWTS_20250215.csv`, EE `UT_GWTS_20250827.csv`,
US `US_GWTS_20251010.csv`, MX `MX_GWTS_20250930.csv`. For any normalised
value (e.g. Latvia's decimal-comma levels) point to `data/DATA_NOTES.md`.
When asked about sources or reproducibility, cite `source_file` and the
aggregation window you used.

## Reporting tips

- Distinguish **depth to water** (`gw_level_from_ground`, larger = deeper/drier)
  from **water-level elevation** (`gw_level_abs`, m a.s.l.).
- Always state the **country and time window** of any aggregate; cadences and
  spans differ, so cross-country comparisons are indicative only.
- For seasonal / monthly analysis, exclude Mexico (annual) or note the gap.
- "Deepest water table" → max `gw_level_from_ground`; "highest / wettest" →
  min. Negative depth-to-water means artesian flow — report it as such.
- For well depth, aquifer type, karst or location, pull from
  `transboundary-monitoring-points` (or use `load_with_metadata()`).
