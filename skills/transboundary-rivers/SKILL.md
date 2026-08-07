---
name: transboundary-rivers
description: >-
  Rivers and surface-water network for the EUROPEAN transboundary groundwater
  areas — the Poland–Ukraine, Lithuania–Latvia, and Latvia–Estonia border
  regions. Use whenever the user asks about rivers, streams, the river network,
  or surface water IN THOSE AREAS or in Poland, Ukraine, Lithuania, Latvia, or
  Estonia — e.g. "rivers near the LT-LV wells", "show the river network in the
  PL-UA border area", "which wells are close to a river". Returns river-line
  GeoPandas layers ready to map or save as GeoJSON, aligned with the
  transboundary well datasets. Source: Copernicus EU-Hydro. This skill is for
  the European transboundary regions ONLY and does NOT cover United States
  rivers/streams/watersheds (use the `rivers`, `hydrology-basins`, `watersheds`,
  or `stream-gauges` skills for the USA), nor the Italian Po-basin wells.
---

# Transboundary Rivers Skill (Europe)

Surface-water context for the European transboundary groundwater areas. The
existing `rivers` / `watersheds` / `stream-gauges` skills are **USA-only**, so
this skill provides the river network for the **PL–UA, LT–LV, and LV–EE** border
regions, clipped to the areas where the transboundary wells sit and reprojected
to lon/lat so it overlays the wells directly.

> **Data status.** The bundled `data/transboundary_rivers.parquet` is produced by
> `scripts/build_eu_hydro_rivers.py` from the Copernicus EU-Hydro River Network
> Database. If the parquet is not present yet, the data has not been downloaded
> and built — see `data/DATA_NOTES.md` for the one-time download + build steps.

## What is bundled

`data/transboundary_rivers.parquet` — river-line segments (EPSG:4326) with a
`region` column (`PL-UA`, `LT-LV`, `LV-EE`) and, where EU-Hydro provides it, a
river name. One row per river segment.

## How to answer

```python
import geopandas as gpd, os
rivers = gpd.read_parquet("data/transboundary_rivers.parquet")

# Rivers in one region, ready to map:
lt_lv = rivers[rivers.region == "LT-LV"]
lt_lv.to_file(os.path.join(temp_dir, "lt_lv_rivers.geojson"), driver="GeoJSON")
```

### Relating rivers to wells (the cross-dataset value)
Because both are EPSG:4326, you can spatially relate them. To find wells near a
river, load the transboundary monitoring points and do a distance/`sjoin_nearest`
against these rivers — e.g. "which LT-LV wells are within 1 km of a river". Keep
the two datasets’ regions consistent (`LT-LV` here ↔ LT/LV wells there).

## Scope / routing

- **This skill:** rivers/surface water in PL, UA, LT, LV, EE (the transboundary
  border areas).
- **NOT this skill:**
  - United States rivers, streams, watersheds, stream gauges → `rivers`,
    `hydrology-basins`, `subwatersheds`, `watersheds`, `stream-gauges`.
  - Italian Po-basin wells / groundwater → the Italy well skills.
  - Groundwater levels/aquifers in the transboundary areas → the
    `transboundary-monitoring-points` / `transboundary-groundwater-timeseries`
    skills. This skill is surface water only.
