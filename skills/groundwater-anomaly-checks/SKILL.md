---
name: groundwater-anomaly-checks
description: >-
  Find anomalies, inconsistencies, data-quality problems, and values/patterns
  that contradict hydrogeological expectations in the transboundary groundwater
  wells (Ukraine, Poland, Lithuania, Latvia, Estonia, US, Mexico). Use whenever
  the user asks whether the data has errors, outliers, suspicious or impossible
  values, internal inconsistencies, things that "don't make sense", or patterns
  that contradict hydrogeology — e.g. karst flagged outside its usual area,
  confined aquifers that are too variable, a water table below the well bottom,
  or a well screen deeper than the borehole. Runs a documented battery of checks
  over the bundled monitoring-points and timeseries data and reports each hit as
  a likely data error, a flag-for-investigation, or a check that passed.
---

# Groundwater Anomaly & Consistency Checks Skill

This skill audits the transboundary groundwater data for **anomalies,
inconsistencies, and hydrogeological contradictions**. It does not bundle its
own data — it reads the parquets from `transboundary-monitoring-points` and
`transboundary-groundwater-timeseries` and runs a set of checks.

A flag is a **prompt to investigate, not a verdict.** Always classify a hit as
one of:
- **Likely data error** — physically impossible (e.g. a screen deeper than the
  borehole).
- **Flag for investigation** — surprising but possibly real (e.g. karst far
  from other karst; it may be a genuine separate karst zone).
- **Check passed** — the data is internally consistent on that axis; report
  that too, so "no anomalies" is an answerable result.

This skill covers the **transboundary** datasets. The Italian Po wells are not
audited here.

## The checks (all verified against the current data)

```python
import pandas as pd, numpy as np

MP="skills/transboundary-monitoring-points/data"
GW="skills/transboundary-groundwater-timeseries/data"

def _load():
    return (pd.read_parquet(f"{MP}/transboundary_mp_clean.parquet"),
            pd.read_parquet(f"{GW}/transboundary_gwts_clean.parquet"))

def _haversine_km(lo1, la1, lo2, la2):
    R=6371; p=np.pi/180
    a=np.sin((la2-la1)*p/2)**2+np.cos(la1*p)*np.cos(la2*p)*np.sin((lo2-lo1)*p/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

# --- 1. Impossible geometry: well screen deeper than the borehole ---
def check_screen_below_total_depth():
    mp,_=_load()
    return mp[(mp.open_to.notna()) & (mp.well_depth.notna()) & (mp.open_to > mp.well_depth+0.01)][
        ["well_ID","country_name","open_from","open_to","well_depth"]]

# --- 2. Impossible level: water table below the bottom of the well ---
def check_watertable_below_well():
    mp,ts=_load()
    dtw=ts.groupby("well_ID")["gw_level_from_ground"].max().rename("max_dtw")
    j=mp[["well_ID","country_name","well_depth"]].merge(dtw, on="well_ID")
    return j[(j.well_depth.notna()) & (j.max_dtw > j.well_depth+0.5)]

# --- 3. Attribute inconsistency: karst flagged on non-soluble rock ---
def check_karst_lithology():
    mp,_=_load()
    k=mp[mp.aquifer_karst==True]
    # karst forms in soluble rock (carbonate / gypsum); flag anything else
    return k[~k.aquifer_lithology.fillna("").str.contains("carbonate")][
        ["well_ID","country_name","aquifer_lithology"]]

# --- 4. Hydro contradiction: confined aquifers should be buffered/stable ---
def check_confined_but_variable(thresh=2.0):
    mp,ts=_load()
    v=ts.dropna(subset=["gw_level_from_ground"]).groupby("well_ID")["gw_level_from_ground"].std().rename("std_m")
    cf=mp[mp.confinement==True][["well_ID","country_name"]].merge(v, on="well_ID")
    return cf[cf.std_m>thresh].sort_values("std_m", ascending=False)

# --- 5. Spatial outlier: a flagged attribute far from its own cluster ---
def check_spatial_outliers(flag="aquifer_karst", min_km=50):
    mp,_=_load()
    k=mp[mp[flag]==True][["well_ID","country_name","Long_WGS84","Lat_WGS84"]].dropna().reset_index(drop=True)
    nn=[_haversine_km(r.Long_WGS84,r.Lat_WGS84,k.Long_WGS84.drop(i),k.Lat_WGS84.drop(i)).min()
        for i,r in k.iterrows()]
    k["nearest_km"]=np.round(nn,1)
    return k[k.nearest_km>min_km].sort_values("nearest_km", ascending=False)

# --- 6. Internal consistency: gw_level_abs == ground_altitude - depth_to_water ---
def check_level_consistency(tol=5.0):
    mp,ts=_load()
    m=ts[["well_ID","gw_level_abs","gw_level_from_ground"]].merge(mp[["well_ID","ground_altitude"]], on="well_ID")
    m["resid"]=m.gw_level_abs-(m.ground_altitude-m.gw_level_from_ground)
    per=m.dropna(subset=["resid"]).groupby("well_ID").resid.median()
    return per[per.abs()>tol]
```

## What each check currently finds (verified)

### Likely data errors (physically impossible)

**Well screen deeper than the borehole** — `check_screen_below_total_depth()`:

| well_ID | country | open_to | well_depth |
|---|---|---|---|
| US_321332106443701 | United States | 92.05 | 36.58 |
| EE_PRK0007590 | Estonia | 144.40 | 141.90 |
| EE_PRK0011141 | Estonia | 43.40 | 42.80 |

The US one is a gross mismatch (screen at 92 m in a 37 m well); the two Estonian
ones are small (~2 m) and could be rounding.

**Water table below the well bottom** — `check_watertable_below_well()`:

| well_ID | country | well_depth | max depth-to-water |
|---|---|---|---|
| UA_RDS_Sp9 | Ukraine | 4.0 | 8.3 |

Water can't sit 8.3 m down in a 4 m well — the `well_depth = 4 m` is suspect
(this is one of the messy Ukrainian records noted in `transboundary-monitoring-points`).

### Attribute inconsistency

**Karst on non-soluble rock** — `check_karst_lithology()`: `LT_218` (Lithuania)
is flagged `aquifer_karst = True` but its lithology is `terrigenic`. Karst
develops in soluble rock (carbonate/gypsum), so the karst flag or the lithology
is wrong.

### Patterns that contradict the hydrogeological model

**Confined but highly variable** — `check_confined_but_variable()`: confined
aquifers should be buffered, yet these confined wells swing > 2 m:

| well_ID | country | water-table σ (m) |
|---|---|---|
| LT_837 | Lithuania | 3.39 |
| US_321332106443701 | United States | 3.09 |
| US_321332106443702 | United States | 3.04 |

(`US_321332106443701` also fails the screen check above — doubly suspect.)
These are candidates: real causes could be heavy pumping, a leaky/semi-confined
unit, or a mislabeled confinement flag — investigate, don't assume.

### Spatial outliers

**Karst far from any other karst** — `check_spatial_outliers("aquifer_karst", 50)`:
`PL_II_551_1` (Poland) sits **120 km** from the nearest other karst well, on the
**PL-UA border**. The karst wells actually fall into three pockets: the main
Baltic cluster (LT/LV ~56°N), a western-Ukraine/Podolia group (~49.8°N, real
gypsum karst), and this lone Polish well. So "karst is just a Baltic thing" is
itself contradicted by the data — flag for investigation rather than error.

### Checks that passed (report these too)

**Level identity** — `check_level_consistency()` returns **0 wells**: across all
records, `gw_level_abs` equals `ground_altitude - gw_level_from_ground` within
tolerance. The absolute vs depth-to-water levels are internally consistent — a
clean result worth stating.

## Example: run the full audit

```python
checks = {
    "screen_below_total_depth": check_screen_below_total_depth,
    "watertable_below_well":    check_watertable_below_well,
    "karst_on_non_carbonate":   check_karst_lithology,
    "confined_but_variable":    check_confined_but_variable,
    "karst_spatial_outliers":   check_spatial_outliers,
}
for name, fn in checks.items():
    hits = fn()
    print(f"{name}: {len(hits)} hit(s)")
n_consistency = len(check_level_consistency())
print(f"level_consistency_violations: {n_consistency}")
# Expect: screen 3, watertable 1, karst_on_non_carbonate 1,
#         confined_but_variable 3, karst_spatial_outliers 1, consistency 0.
```

Save flagged wells for the map when useful:

```python
import geopandas as gpd
from shapely.geometry import Point
mp,_=_load()
flagged_ids = set(check_karst_lithology().well_ID) | set(check_confined_but_variable().well_ID) \
            | set(check_spatial_outliers().well_ID) | set(check_watertable_below_well().well_ID)
f = mp[mp.well_ID.isin(flagged_ids)].dropna(subset=["Long_WGS84","Lat_WGS84"])
g = gpd.GeoDataFrame(f, geometry=[Point(x,y) for x,y in zip(f.Long_WGS84,f.Lat_WGS84)], crs="EPSG:4326")
g.to_file(os.path.join(temp_dir, "flagged_wells.geojson"), driver="GeoJSON")
```

## Reporting guidance

- Always label each hit: **likely error**, **flag for investigation**, or
  **check passed**. Never present a flag as a confirmed mistake.
- For impossible values, name the contradicting fields and their values.
- For the karst-placement and confined-variability flags, give the
  hydrogeological reason it's surprising and at least one plausible benign
  explanation (real gypsum karst; pumping/leaky confinement).
- Thresholds (`thresh`, `min_km`, `tol`) are conventions, not physics — state
  the threshold you used so a hit is reproducible.
- These checks cover the transboundary data only; the Italian Po wells aren't
  audited here.
- Cross-reference the known, documented quirks in
  `skills/transboundary-monitoring-points/data/DATA_NOTES.md` (duplicate UA IDs,
  the `?`-suffixed IDs, partial UA joins, sparse Mexican metadata) — several
  flags trace back to those.
