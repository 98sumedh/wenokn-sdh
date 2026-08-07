# Data provenance — transboundary rivers (EU-Hydro)

## Status: NOT YET BUILT
`transboundary_rivers.parquet` is not in the repo until someone downloads the
source and runs the ETL. Steps below.

## Source
**Copernicus EU-Hydro — River Network Database and Coastline**
https://land.copernicus.eu/en/products/eu-hydro

- Requires a free Copernicus account to download.
- Ships as File Geodatabase (`.gdb`) or shapefile, in **EPSG:3035** (ETRS89-LAEA).
- **Attribution required** (Copernicus Land Monitoring Service). Keep this notice
  and record the download date once built.

## Basins to download
Download the River Network layer for the River Basin Districts covering the
transboundary groundwater areas:

| Region | Countries | Basins (approx.) |
|--------|-----------|------------------|
| PL-UA  | Poland, Ukraine    | Vistula, Dniester |
| LT-LV  | Lithuania, Latvia  | Nemunas, Lielupe, Venta |
| LV-EE  | Latvia, Estonia    | Daugava, Gauja |

## Build
```
export EU_HYDRO_SRC=/path/to/eu_hydro_river_net     # the .gdb or shapefile folder
python scripts/build_eu_hydro_rivers.py
```
The ETL reprojects 3035 → 4326, clips each region to the transboundary well
locations (buffered ~50 km, derived from
`transboundary-monitoring-points/data/transboundary_mp_clean.parquet`; falls back
to documented bounding boxes if that parquet is absent), and writes
`transboundary_rivers.parquet` here with a `region` column.

## Why clipped
The full national river networks are large. We keep only segments near the wells
so the bundled parquet stays small and the repo does not bloat — same policy as
the well timeseries (the full GWTS CSV is not bundled either).

## Download date
_(fill in once built: YYYY-MM-DD, EU-Hydro release version)_
