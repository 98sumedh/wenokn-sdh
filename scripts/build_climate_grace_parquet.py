#!/usr/bin/env python3
"""
ETL: build the climate + GRACE parquet bundled in the groundwater-regional-
comparison skill (used for the "why" analysis).

Produces:
  skills/groundwater-regional-comparison/data/transboundary_climate_grace.parquet

SOURCE DATA
-----------
GRANDE-U `08_mergedTimeseries/GWTS_with_climate_and_GRACE.csv` — monthly
climate (E-OBS precip, GLEAM PET/AET, temperature) + GRACE storage per well.
Point GRANDEU_SRC at the GRANDE-U folder that contains 08_mergedTimeseries:

    export GRANDEU_SRC=/path/to/GRANDE-U_Task1
    python scripts/build_transboundary_parquets.py      # run FIRST (dependency)
    python scripts/build_climate_grace_parquet.py

DEPENDENCY / KNOWN FIX
----------------------
The source file's `gw_level_from_ground` is blank for Latvia (and `rel_gw_change`
is missing there). This script therefore takes the climate/GRACE DRIVERS from
the source file but RE-JOINS the authoritative water levels from the cleaned
GWTS parquet (built by build_transboundary_parquets.py) on well_ID + year +
month. Run that script first. See the skill's data/DATA_NOTES.md for details.
Italy and Mexico are not present in the source climate file (documented gap).
"""
import os
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.environ.get("GRANDEU_SRC", os.path.join(REPO, "GRANDE-U_Task1"))
SRC_CSV = os.path.join(SRC, "08_mergedTimeseries", "GWTS_with_climate_and_GRACE.csv")
GWTS_CLEAN = os.path.join(REPO, "skills/transboundary-groundwater-timeseries/data/transboundary_gwts_clean.parquet")
OUT_DIR = os.path.join(REPO, "skills/groundwater-regional-comparison/data")
OUT = os.path.join(OUT_DIR, "transboundary_climate_grace.parquet")

COUNTRY_NAME = {"UA":"Ukraine","PL":"Poland","LT":"Lithuania","LV":"Latvia",
                "EE":"Estonia","US":"United States","MX":"Mexico"}

def build():
    cl = pd.read_csv(SRC_CSV, sep=";", encoding="utf-8-sig")
    cl["well_ID"] = cl["well_ID"].str.strip()
    cl["date"] = pd.to_datetime(cl["date"], errors="coerce")
    cl["observation_year"]  = cl["date"].dt.year.astype("Int64")
    cl["observation_month"] = cl["date"].dt.month.astype("Int64")
    for c in ["aet","pet","precip","temp","grace_value"]:
        cl[c] = pd.to_numeric(cl[c], errors="coerce")
    cl["country"] = cl["well_ID"].str.extract(r"^([A-Z]{2})_")[0]
    cl["country_name"] = cl["country"].map(COUNTRY_NAME)

    climate = cl[["well_ID","country","country_name","observation_year","observation_month",
                  "precip","pet","aet","temp","grace_value"]].copy()

    # Re-join authoritative GW levels (fixes the blank Latvia gw_level_from_ground).
    gw = pd.read_parquet(GWTS_CLEAN)[["well_ID","observation_year","observation_month",
                                      "gw_level_from_ground","gw_level_abs"]]
    merged = climate.merge(gw, on=["well_ID","observation_year","observation_month"], how="left")

    os.makedirs(OUT_DIR, exist_ok=True)
    merged.to_parquet(OUT, index=False)
    return merged

if __name__ == "__main__":
    if not os.path.isfile(SRC_CSV):
        raise SystemExit(f"Source file not found: {SRC_CSV}\n"
                         f"Set GRANDEU_SRC to the GRANDE-U folder containing 08_mergedTimeseries/.")
    if not os.path.isfile(GWTS_CLEAN):
        raise SystemExit(f"Missing {GWTS_CLEAN}\nRun scripts/build_transboundary_parquets.py first.")
    m = build()
    print(f"climate+GRACE: {m.shape} -> {OUT}")
    print("gw_level present by country:",
          m.groupby('country_name')['gw_level_from_ground'].apply(lambda s:int(s.notna().sum())).to_dict())
    print("done.")
