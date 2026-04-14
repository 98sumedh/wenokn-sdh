---
name: kanawha-cascading-impact
description: Cascading flood impact analysis for the Kanawha River. Models three impact tiers — Primary (direct flooding of critical infrastructure), Secondary (power-dependent facilities losing service due to flooded electric substations, and residential population at risk from flooded wastewater plants), and Tertiary (population within range of power-impacted hospitals and EMS stations). Use when the user asks about cascading, indirect, secondary, or tertiary flood impacts, or infrastructure interdependencies.
---

# Kanawha Cascading Impact Skill

## Description

Models flood impact propagation across interdependent critical infrastructure along the Kanawha River using a proximity-based dependency approach. No external cascading tools (IN-CORE, CLIMADA) required — spatial buffers and dependency rules are applied directly to USACE CIKR and NSI data.

**Three impact tiers:**

| Tier | Type | Logic |
|------|------|-------|
| Primary | Direct flooding | CIKR facilities with flood depth > 0 |
| Secondary — Power outage | Infrastructure service loss | Non-flooded Hospitals, Schools, EMS, Fire Stations, Law Enforcement, Colleges within 10 km of a flooded Electric Substation |
| Secondary — Water service | Residential disruption | Non-flooded NSI residential structures (RES) within 8 km of a flooded Waste Water Treatment Plant |
| Tertiary | Population without emergency services | NSI population within 15 km of a power-impacted Hospital or EMS station |

**Dependency rules (hardcoded):**
- `Electric Substations` → powers → `Hospitals`, `Schools`, `EMS`, `Fire Stations`, `Fire Stations EMS`, `Law Enforcement`, `Colleges and Universities`
- `Waste Water Treatment Plants` → serves → NSI residential structures (`ST_DAMCAT == "RES"`)
- Power-impacted `Hospitals` + `EMS` → serve → NSI population (tertiary)

**Service radii (EPSG:5070 meters):**
- Electric Substation → power-dependent facilities: **10,000 m**
- Waste Water Treatment Plant → residential structures: **8,000 m**
- Hospital / EMS → served population: **15,000 m**

**Available flow scenarios (cfs) — always round UP to nearest:**
1,000 / 50,000 / 100,000 / 150,000 / 200,000 / 300,000 / 400,000 / 500,000 / 700,000 / 900,000 / 1,000,000 / 1,500,000 / 2,000,000

## When to Use

- User asks about cascading, indirect, secondary, or tertiary flood impacts
- User asks "what happens downstream when a substation floods?"
- User asks about infrastructure interdependencies or service disruption
- User asks for a full three-tier impact analysis at a given flow

## When NOT to Use

- User only wants direct damage counts or economic losses → use **kanawha-cikr-impact** or **kanawha-nsi-impact**
- User asks about physical network propagation (power grid simulation, hydraulic failure) → those require IN-CORE or WNTR

## Example

### Three-tier cascading impact analysis at 400,000 cfs

```python
import json, os
import numpy as np
import pandas as pd
import geopandas as gpd
import requests
import streamlit as st
from rasterio.io import MemoryFile
from shapely.ops import unary_union

GEOSERVER = "https://sparcal.sdsc.edu/geoserver/tiger"
SCENARIOS = [1_000, 50_000, 100_000, 150_000, 200_000, 300_000,
             400_000, 500_000, 700_000, 900_000, 1_000_000, 1_500_000, 2_000_000]

# ← substitute from user's request
flow_cfs = 400_000

scenario = next((s for s in SCENARIOS if s >= flow_cfs), SCENARIOS[-1])
flow_k = scenario // 1000
print(f"Flow scenario: {scenario:,} cfs")

temp_dir = os.environ.get("TEMP_DIR", st.session_state.temp_dir)

# Dependency configuration
POWER_SOURCES    = {"Electric Substations"}
POWER_DEPENDENTS = {"Hospitals", "Schools", "EMS", "Fire Stations",
                    "Fire Stations EMS", "Law Enforcement",
                    "Colleges and Universities"}
WATER_SOURCES    = {"Waste Water Treatment Plants"}
EMS_TYPES        = {"Hospitals", "EMS", "Fire Stations EMS"}

SUBSTATION_RADIUS_M = 10_000   # 10 km power service radius
WASTEWATER_RADIUS_M = 8_000    # 8 km water service radius
EMS_RADIUS_M        = 15_000   # 15 km emergency service radius

# --- Step 1: Add WMS flood depth layer to map ---
wms_layer = {
    "url": f"{GEOSERVER}/wms",
    "layers": f"tiger:Depth_{scenario}_5070",
    "name": f"Kanawha Flood {flow_k}k cfs",
    "opacity": 0.7,
    "bbox": [37.5, -82.5, 39.0, -80.5],
}
with open(os.path.join(temp_dir, f"kanawha_flood_{flow_k}k.wms.json"), "w") as f:
    json.dump(wms_layer, f)

# --- Step 2: Fetch all CIKR points (EPSG:5070) ---
print("Fetching CIKR facilities from WFS ...")
cikr = gpd.read_file(
    f"{GEOSERVER}/ows?service=WFS&version=2.0.0&request=GetFeature"
    f"&typeName=tiger:Kanawha_CKR_Points_5070&outputFormat=application/json"
)  # EPSG:5070
print(f"CIKR facilities fetched: {len(cikr)}")

# --- Step 3: Fetch depth raster via WCS ---
xmin, ymin, xmax, ymax = cikr.total_bounds
margin = 500
wcs_url = (
    f"{GEOSERVER}/ows?service=WCS&version=2.0.1&request=GetCoverage"
    f"&coverageId=tiger:Depth_{scenario}_5070&format=image/tiff"
    f"&SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/5070"
    f"&SUBSET=X({xmin-margin:.0f},{xmax+margin:.0f})"
    f"&SUBSET=Y({ymin-margin:.0f},{ymax+margin:.0f})"
)
print("Fetching depth raster from WCS ...")
resp = requests.get(wcs_url, timeout=120)
resp.raise_for_status()

# --- Step 4: Sample depth at each CIKR point ---
with MemoryFile(resp.content) as memfile:
    with memfile.open() as src:
        nodata = src.nodata
        coords = [(geom.x, geom.y) for geom in cikr.geometry]
        raw = [v[0] for v in src.sample(coords)]

depths = [np.nan if ((nodata is not None and v == nodata) or v <= 0) else float(v)
          for v in raw]
cikr["depth_ft"] = depths

def classify(d):
    if np.isnan(d): return "Not Flooded"
    if d <= 1:      return "Nuisance"
    if d <= 3:      return "Minor"
    if d <= 6:      return "Moderate"
    return "Severe"

cikr["severity"] = cikr["depth_ft"].apply(classify)
cikr["tier"] = "Not Impacted"

# --- Step 5: Tier 1 — Primary (directly flooded) ---
primary_mask = cikr["severity"] != "Not Flooded"
cikr.loc[primary_mask, "tier"] = "Primary"

primary = cikr[primary_mask]
flooded_substations  = primary[primary["Point_Type"].isin(POWER_SOURCES)]
flooded_wastewater   = primary[primary["Point_Type"].isin(WATER_SOURCES)]

print(f"\nTier 1 — Primary (directly flooded):")
print(f"  Total flooded CIKR: {len(primary)}")
print(f"  Flooded Electric Substations: {len(flooded_substations)}")
print(f"  Flooded Waste Water Plants:   {len(flooded_wastewater)}")

# --- Step 6: Tier 2a — Secondary power outage ---
# Non-flooded power-dependent facilities within buffer of each flooded substation
secondary_power_idx = set()

if len(flooded_substations) > 0:
    # Union of all substation service buffers
    substation_service_area = unary_union(
        flooded_substations.geometry.buffer(SUBSTATION_RADIUS_M)
    )
    # Non-flooded power-dependent candidates
    candidates = cikr[
        (cikr["tier"] == "Not Impacted") &
        (cikr["Point_Type"].isin(POWER_DEPENDENTS))
    ]
    within_power = candidates[candidates.geometry.within(substation_service_area)]
    secondary_power_idx = set(within_power.index)
    cikr.loc[list(secondary_power_idx), "tier"] = "Secondary-Power"
    print(f"\nTier 2a — Secondary (power outage from flooded substations):")
    print(f"  Service radius: {SUBSTATION_RADIUS_M/1000:.0f} km")
    print(f"  Flooded substations: {len(flooded_substations)}")
    print(f"  Affected facilities (non-flooded, within range): {len(secondary_power_idx)}")
    if len(secondary_power_idx) > 0:
        by_type = cikr.loc[list(secondary_power_idx)].groupby("Point_Type").size()
        for t, n in by_type.items():
            print(f"    {t}: {n}")
else:
    print("\nTier 2a — No electric substations flooded at this flow.")

# --- Step 7: Tier 2b — Secondary water service disruption ---
# Fetch NSI residential structures within buffer of flooded wastewater plants
secondary_water_nsi = None
water_pop_at_risk = 0

if len(flooded_wastewater) > 0:
    wastewater_service_area = unary_union(
        flooded_wastewater.geometry.buffer(WASTEWATER_RADIUS_M)
    )
    # Fetch NSI — residential only (filter by ST_DAMCAT=RES to reduce transfer size)
    from urllib.parse import quote
    print(f"\nFetching NSI residential structures for water disruption analysis ...")
    nsi_url = (
        f"{GEOSERVER}/ows?service=WFS&version=2.0.0&request=GetFeature"
        f"&typeName=tiger:NSI2022_2026pricelevel&outputFormat=application/json"
        f"&CQL_FILTER=" + quote("ST_DAMCAT='RES'")
    )
    nsi_res = gpd.read_file(nsi_url)  # EPSG:4326
    nsi_res_5070 = nsi_res.to_crs(epsg=5070)

    # Find non-flooded residential structures within wastewater service area
    # "non-flooded" = outside the flood extent (depth is NaN from raster)
    # We use a separate raster sample for NSI
    xmin2, ymin2, xmax2, ymax2 = nsi_res_5070.total_bounds
    wcs_url2 = (
        f"{GEOSERVER}/ows?service=WCS&version=2.0.1&request=GetCoverage"
        f"&coverageId=tiger:Depth_{scenario}_5070&format=image/tiff"
        f"&SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/5070"
        f"&SUBSET=X({xmin2-margin:.0f},{xmax2+margin:.0f})"
        f"&SUBSET=Y({ymin2-margin:.0f},{ymax2+margin:.0f})"
    )
    resp2 = requests.get(wcs_url2, timeout=120)
    resp2.raise_for_status()
    with MemoryFile(resp2.content) as memfile:
        with memfile.open() as src:
            nodata2 = src.nodata
            coords2 = [(g.x, g.y) for g in nsi_res_5070.geometry]
            raw2 = [v[0] for v in src.sample(coords2)]
    nsi_depths = [np.nan if ((nodata2 is not None and v == nodata2) or v <= 0) else float(v)
                  for v in raw2]
    nsi_res["depth_ft"] = nsi_depths

    # Within service area + not already flooded
    in_service_area = nsi_res_5070.geometry.within(wastewater_service_area)
    not_flooded_nsi  = nsi_res["depth_ft"].isna()
    secondary_water_nsi = nsi_res[in_service_area & not_flooded_nsi].copy()

    water_pop_at_risk = (
        secondary_water_nsi["POP2AMU65"].sum() +
        secondary_water_nsi["POP2AMO65"].sum()
    )
    print(f"\nTier 2b — Secondary (water service disruption from flooded wastewater plants):")
    print(f"  Service radius: {WASTEWATER_RADIUS_M/1000:.0f} km")
    print(f"  Flooded wastewater plants: {len(flooded_wastewater)}")
    print(f"  Residential structures in service area (non-flooded): {len(secondary_water_nsi):,}")
    print(f"  Residential population at risk of water disruption: {int(water_pop_at_risk):,}")
else:
    print("\nTier 2b — No waste water treatment plants flooded at this flow.")

# --- Step 8: Tier 3 — Tertiary (population without emergency services) ---
# NSI population within range of power-impacted Hospitals + EMS
tertiary_pop = 0
tertiary_nsi = None

power_impacted_ems = cikr[
    (cikr["tier"] == "Secondary-Power") &
    (cikr["Point_Type"].isin(EMS_TYPES))
]

if len(power_impacted_ems) > 0:
    ems_service_area = unary_union(
        power_impacted_ems.geometry.buffer(EMS_RADIUS_M)
    )
    # Use the full NSI (or reload if not already fetched)
    print(f"\nFetching full NSI for tertiary population analysis ...")
    nsi_full_url = (
        f"{GEOSERVER}/ows?service=WFS&version=2.0.0&request=GetFeature"
        f"&typeName=tiger:NSI2022_2026pricelevel&outputFormat=application/json"
    )
    nsi_full = gpd.read_file(nsi_full_url)  # EPSG:4326
    nsi_full_5070 = nsi_full.to_crs(epsg=5070)

    in_ems_area = nsi_full_5070.geometry.within(ems_service_area)
    tertiary_nsi = nsi_full[in_ems_area].copy()
    tertiary_pop = (
        tertiary_nsi["POP2AMU65"].sum() +
        tertiary_nsi["POP2AMO65"].sum()
    )
    print(f"\nTier 3 — Tertiary (population served by power-impacted hospitals/EMS):")
    print(f"  Service radius: {EMS_RADIUS_M/1000:.0f} km")
    print(f"  Power-impacted Hospitals + EMS: {len(power_impacted_ems)}")
    print(f"  Structures in their service area: {len(tertiary_nsi):,}")
    print(f"  Population at risk of lost emergency coverage: {int(tertiary_pop):,}")
else:
    print("\nTier 3 — No hospitals or EMS stations lost power at this flow.")

# --- Step 9: Save map layers ---
# Layer 1: All CIKR color-coded by tier
cikr_wgs84 = cikr.to_crs(epsg=4326)
cikr_wgs84.to_file(
    os.path.join(temp_dir, f"kanawha_cascade_cikr_{flow_k}k.geojson"), driver="GeoJSON"
)
print(f"\nSaved CIKR tier layer ({len(cikr_wgs84)} facilities).")

# Layer 2: Buffer zones (substation + wastewater service areas)
buffer_features = []
for _, row in flooded_substations.to_crs(epsg=4326).iterrows():
    buf = row.geometry.buffer(SUBSTATION_RADIUS_M / 111320)  # rough degrees
    buffer_features.append({"type": "Feature",
                             "geometry": buf.__geo_interface__,
                             "properties": {"type": "Electric Substation Service Area",
                                            "radius_km": SUBSTATION_RADIUS_M / 1000}})
for _, row in flooded_wastewater.to_crs(epsg=4326).iterrows():
    buf = row.geometry.buffer(WASTEWATER_RADIUS_M / 111320)
    buffer_features.append({"type": "Feature",
                             "geometry": buf.__geo_interface__,
                             "properties": {"type": "Wastewater Service Area",
                                            "radius_km": WASTEWATER_RADIUS_M / 1000}})
if buffer_features:
    buffers_gdf = gpd.GeoDataFrame.from_features(buffer_features, crs="EPSG:4326")
    buffers_gdf.to_file(
        os.path.join(temp_dir, f"kanawha_cascade_buffers_{flow_k}k.geojson"), driver="GeoJSON"
    )
    print(f"Saved {len(buffer_features)} service area buffer(s).")

# Layer 3: Secondary water-disruption NSI (if any)
if secondary_water_nsi is not None and len(secondary_water_nsi) > 0:
    water_cols = ["geometry", "ST_DAMCAT", "OCCTYPE", "depth_ft",
                  "POP2AMU65", "POP2AMO65", "VAL_STRUCT", "RESUNITS"]
    secondary_water_nsi[water_cols].to_file(
        os.path.join(temp_dir, f"kanawha_cascade_water_nsi_{flow_k}k.geojson"), driver="GeoJSON"
    )
    print(f"Saved {len(secondary_water_nsi):,} residential structures at water-disruption risk.")

# --- Step 10: Print final summary ---
print(f"\n{'='*55}")
print(f"  KANAWHA CASCADING FLOOD IMPACT SUMMARY")
print(f"  Flow: {flow_cfs:,} cfs → scenario: {scenario:,} cfs")
print(f"{'='*55}")

tier_counts = cikr["tier"].value_counts()
print(f"\n  Tier 1 — Primary (directly flooded CIKR):")
print(f"    {tier_counts.get('Primary', 0)} facilities")
if len(primary) > 0:
    for pt, cnt in primary.groupby("Point_Type").size().items():
        print(f"      {pt}: {cnt}")

print(f"\n  Tier 2a — Secondary (power outage):")
print(f"    {tier_counts.get('Secondary-Power', 0)} non-flooded facilities lose power")

print(f"\n  Tier 2b — Secondary (water service disruption):")
if secondary_water_nsi is not None:
    print(f"    {len(secondary_water_nsi):,} residential structures affected")
    print(f"    {int(water_pop_at_risk):,} residents at risk of water disruption")
else:
    print(f"    0 (no wastewater plants flooded)")

print(f"\n  Tier 3 — Tertiary (population without emergency services):")
if tertiary_nsi is not None:
    print(f"    {int(tertiary_pop):,} people in service areas of power-impacted hospitals/EMS")
else:
    print(f"    0 (no hospitals or EMS lost power)")

print(f"\n  Map layers saved:")
print(f"    kanawha_cascade_cikr_{flow_k}k      — all CIKR, color-coded by tier")
print(f"    kanawha_cascade_buffers_{flow_k}k   — service area buffers")
if secondary_water_nsi is not None and len(secondary_water_nsi) > 0:
    print(f"    kanawha_cascade_water_nsi_{flow_k}k — residential structures at water-disruption risk")
```

## Notes

- **Tier classification**: Each CIKR facility gets exactly one tier — `Primary` takes precedence over `Secondary-Power`. A flooded hospital is Primary, not Secondary.
- **Buffer geometry**: Buffers are computed in EPSG:5070 (meters) for accuracy. The map layer uses a rough degree conversion for display — use the EPSG:5070 geometry for analysis.
- **NSI fetch**: The full NSI (88,460 structures) is only fetched for Tier 3. Tier 2b fetches only residential structures (`ST_DAMCAT='RES'`) to reduce transfer time.
- **Dependency rules are simplified**: The skill assumes any non-flooded power-dependent facility within 10 km of a flooded substation loses power. Real power grid topology is not modeled.
- **Wastewater**: The 8 km radius approximates a municipal service area. Downstream contamination spread is not modeled.
- **Tertiary population**: This is the population *within range* of a degraded emergency facility — it is an upper-bound estimate of people with reduced emergency coverage, not confirmed casualties.
- **CRS**: CIKR is fetched in EPSG:5070. NSI is fetched in EPSG:4326 and reprojected to EPSG:5070 for spatial operations.
