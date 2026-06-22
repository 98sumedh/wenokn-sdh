# ETL scripts — regenerating the bundled groundwater parquets

These scripts rebuild the Parquet files that the groundwater skills bundle, so
the data can be regenerated when the upstream source data is updated.

## Source data

The GRANDE-U transboundary groundwater compilation (not stored in this repo).
Download the share and note the top folder that contains `00_UA`, `01_PL`, …
`06_MX`, and `08_mergedTimeseries`:

- owncloud share: https://owncloud.ut.ee/owncloud/s/ksLaqQypdXiYqWs

Point `GRANDEU_SRC` at that folder:

```bash
export GRANDEU_SRC=/path/to/GRANDE-U_Task1
```

If unset, the scripts default to `./GRANDE-U_Task1` under the repo root.

## Requirements

```bash
pip install pandas pyarrow
```

## Run (order matters)

```bash
# 1) Unified monitoring-points + time-series parquets (4 files)
python scripts/build_transboundary_parquets.py

# 2) Climate + GRACE parquet (depends on step 1's GWTS output)
python scripts/build_climate_grace_parquet.py
```

## What each script produces

| Script | Outputs |
|---|---|
| `build_transboundary_parquets.py` | `skills/transboundary-monitoring-points/data/transboundary_mp_{faithful,clean}.parquet`, `skills/transboundary-groundwater-timeseries/data/transboundary_gwts_{faithful,clean}.parquet` |
| `build_climate_grace_parquet.py` | `skills/groundwater-regional-comparison/data/transboundary_climate_grace.parquet` |

The scripts write **directly into the skill `data/` folders**. Running them on
the current source data reproduces the committed parquets exactly.

## Notes

- `faithful` keeps raw values untouched; `clean` is typed and normalised. Every
  transformation is documented in
  `skills/transboundary-monitoring-points/data/DATA_NOTES.md` and
  `skills/groundwater-regional-comparison/data/DATA_NOTES.md`.
- If a country ships a new canonical filename, update the `SOURCES` map in
  `build_transboundary_parquets.py`.
- The climate file lacks Latvia water levels and omits Italy/Mexico entirely;
  `build_climate_grace_parquet.py` re-joins authoritative water levels from the
  GWTS parquet to fix Latvia. See the comparison skill's `DATA_NOTES.md`.
- The regional-comparison and anomaly-check skills compute their results live
  from these parquets, so they need no separate ETL.
