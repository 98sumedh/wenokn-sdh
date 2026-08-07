#!/usr/bin/env python3
"""
ETL: build the transboundary river-network parquet bundled in the
`transboundary-rivers` skill, from the Copernicus EU-Hydro River Network
Database.

Produces, directly inside the skill data folder:
  skills/transboundary-rivers/data/transboundary_rivers.parquet   (all regions)
  skills/transboundary-rivers/data/DATA_NOTES.md                  (provenance; hand-maintained)

WHY THIS SKILL EXISTS
---------------------
Every river/hydrology skill already in the repo (rivers, hydrology-basins,
watersheds, stream-gauges) is USA-only. The European transboundary groundwater
areas have wells but no surface-water context. EU-Hydro fills that gap so the
agent can relate groundwater to the rivers above it in the same region.

SOURCE DATA  (manual download — requires a free Copernicus account)
-------------------------------------------------------------------
Copernicus EU-Hydro River Network Database:
  https://land.copernicus.eu/en/products/eu-hydro
Download the River Network layer for the basins covering the transboundary
areas (File Geodatabase .gdb or shapefile), then point EU_HYDRO_SRC at the
folder (or .gdb) that holds the river-network features:

    export EU_HYDRO_SRC=/path/to/eu_hydro_river_net       # .gdb or dir of shapefiles
    python scripts/build_eu_hydro_rivers.py

Notes on the source:
  * EU-Hydro ships in EPSG:3035 (ETRS89-LAEA, metric). We reproject to
    EPSG:4326 (lon/lat) so rivers align with the wells and the web map.
  * The full networks are large; we CLIP to the transboundary regions before
    writing so the bundled parquet stays small and the repo does not bloat.
  * Copernicus data requires attribution — keep the note in DATA_NOTES.md.

CLIP REGIONS
------------
By default the clip boxes are derived from the actual transboundary well
locations (the monitoring-points parquet), buffered by BUFFER_DEG degrees, so
the rivers we keep are exactly those near the wells. If that parquet is not
present, we fall back to the documented FALLBACK_BBOXES below.
"""
import os
import sys

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("EU_HYDRO_SRC", os.path.join(REPO, "eu_hydro_river_net"))
OUT_DIR = os.path.join(REPO, "skills/transboundary-rivers/data")
OUT = os.path.join(OUT_DIR, "transboundary_rivers.parquet")

# Source of well locations used to derive clip regions.
MP_PARQUET = os.path.join(
    REPO, "skills/transboundary-monitoring-points/data/transboundary_mp_clean.parquet"
)

SRC_CRS = "EPSG:3035"   # EU-Hydro native
DST_CRS = "EPSG:4326"   # lon/lat, matches the wells + web map
BUFFER_DEG = 0.5        # ~50 km padding around the wells

# Region → the countries whose wells define it. Regions mirror the transboundary
# groundwater areas so the river skill lines up with the well skills.
REGIONS = {
    "PL-UA": ["PL", "UA"],
    "LT-LV": ["LT", "LV"],
    "LV-EE": ["LV", "EE"],
}

# Used only if the well parquet is unavailable. Rough boxes (lon_min, lat_min,
# lon_max, lat_max) around each border area — refine from the wells when possible.
FALLBACK_BBOXES = {
    "PL-UA": (22.0, 48.0, 27.5, 52.0),
    "LT-LV": (20.9, 55.0, 27.0, 57.2),
    "LV-EE": (24.0, 56.8, 28.2, 59.0),
}


def region_boxes():
    """Return {region: (minx, miny, maxx, maxy)} in EPSG:4326."""
    if os.path.exists(MP_PARQUET):
        mp = gpd.read_parquet(MP_PARQUET) if MP_PARQUET.endswith(".parquet") else None
        # mp may be a plain DataFrame with lon/lat columns; handle both.
        if mp is None or "geometry" not in getattr(mp, "columns", []):
            df = pd.read_parquet(MP_PARQUET)
            loncol = next((c for c in df.columns if c.lower() in ("lon", "long", "longitude")), None)
            latcol = next((c for c in df.columns if c.lower() in ("lat", "latitude")), None)
            countrycol = next((c for c in df.columns if c.lower() == "country"), None)
            if loncol and latcol and countrycol:
                boxes = {}
                for region, countries in REGIONS.items():
                    sub = df[df[countrycol].isin(countries)].dropna(subset=[loncol, latcol])
                    if len(sub):
                        boxes[region] = (
                            sub[loncol].min() - BUFFER_DEG, sub[latcol].min() - BUFFER_DEG,
                            sub[loncol].max() + BUFFER_DEG, sub[latcol].max() + BUFFER_DEG,
                        )
                if boxes:
                    print(f"Derived clip boxes from wells in {MP_PARQUET}")
                    return boxes
    print("Well parquet not usable; falling back to documented FALLBACK_BBOXES.")
    return dict(FALLBACK_BBOXES)


def main():
    if not os.path.exists(SRC):
        sys.exit(
            f"EU_HYDRO_SRC not found: {SRC}\n"
            "Download the EU-Hydro River Network Database from\n"
            "  https://land.copernicus.eu/en/products/eu-hydro\n"
            "and set EU_HYDRO_SRC to the .gdb or shapefile folder."
        )
    os.makedirs(OUT_DIR, exist_ok=True)
    boxes = region_boxes()

    print(f"Reading river network from {SRC} ...")
    rivers = gpd.read_file(SRC)                       # auto-detects .gdb / shapefile
    if rivers.crs is None:
        rivers = rivers.set_crs(SRC_CRS)
    rivers = rivers.to_crs(DST_CRS)                   # reproject to lon/lat
    print(f"  {len(rivers):,} river features read; reprojected to {DST_CRS}")

    parts = []
    for region, (minx, miny, maxx, maxy) in boxes.items():
        clip = gpd.clip(rivers, box(minx, miny, maxx, maxy))
        clip = clip.assign(region=region)
        print(f"  {region}: {len(clip):,} river segments after clip")
        parts.append(clip)

    out = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=DST_CRS)
    # Keep the columns light; a name column is nice-to-have if EU-Hydro provides one.
    out.to_parquet(OUT)
    print(f"Wrote {len(out):,} segments across {len(boxes)} regions → {OUT}")
    print("Remember: update DATA_NOTES.md with the Copernicus attribution + download date.")


if __name__ == "__main__":
    main()
