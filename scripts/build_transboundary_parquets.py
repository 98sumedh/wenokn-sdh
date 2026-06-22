#!/usr/bin/env python3
"""
ETL: build the unified transboundary MP (monitoring points) and GWTS
(groundwater time series) parquet files bundled in the well skills.

Produces, directly inside the skill data folders:
  skills/transboundary-monitoring-points/data/transboundary_mp_faithful.parquet
  skills/transboundary-monitoring-points/data/transboundary_mp_clean.parquet
  skills/transboundary-groundwater-timeseries/data/transboundary_gwts_faithful.parquet
  skills/transboundary-groundwater-timeseries/data/transboundary_gwts_clean.parquet

faithful  = values untouched (raw strings); only headers harmonised + country/source_file added.
clean     = typed + normalised (decimal comma fixed, booleans/flags parsed, IDs stripped,
            EPSG parsed, lithology typo fixed, duplicate US column dropped).

Every transformation is documented in
skills/transboundary-monitoring-points/data/DATA_NOTES.md.

SOURCE DATA
-----------
The GRANDE-U transboundary compilation (per-country `*_MP_*` / `*_GWTS_*` CSVs).
Download from the owncloud share and point GRANDEU_SRC at the folder that
contains 00_UA, 01_PL, ... 06_MX:

    export GRANDEU_SRC=/path/to/GRANDE-U_Task1
    python scripts/build_transboundary_parquets.py

If GRANDEU_SRC is unset it defaults to ./GRANDE-U_Task1 under the repo root.
When the source data is updated, re-run this script to regenerate the parquets;
if a country's canonical filename changes, update SOURCES below.
"""
import os
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.environ.get("GRANDEU_SRC", os.path.join(REPO, "GRANDE-U_Task1"))
MP_OUT   = os.path.join(REPO, "skills/transboundary-monitoring-points/data")
GWTS_OUT = os.path.join(REPO, "skills/transboundary-groundwater-timeseries/data")

# --- Canonical current source files: one matched (MP, GWTS) pair per country ---
SOURCES = {
    "UA": ("00_UA/UA_MP_20260615.csv",          "00_UA/UA_GWTS_20250516.csv"),
    "PL": ("01_PL/PL_MP_20250903.csv",          "01_PL/PL_GWTS_20250311_corrected.csv"),
    "LT": ("02_LT/LT_MP_20250903.csv",          "02_LT/LT_GWTS_20250219.csv"),
    "LV": ("03_LV/UL_MP_20250903.csv",          "03_LV/UL_GWTS_20250215.csv"),
    "EE": ("04_EE/UT_MP_20250903.csv",          "04_EE/UT_GWTS_20250827.csv"),
    "US": ("05_US/US_MP_20260303.csv",          "05_US/US_GWTS_20251010.csv"),
    "MX": ("06_MX/MX_MP_20250930.csv",          "06_MX/MX_GWTS_20250930.csv"),
}
COUNTRY_NAME = {"UA":"Ukraine","PL":"Poland","LT":"Lithuania","LV":"Latvia",
                "EE":"Estonia","US":"United States","MX":"Mexico"}

# Header harmonisation (renames headers only, never values)
HEADER_MAP = {
    "temporal data resolution": "temporal_data_resolution",
    "Distance to the nearest river. m": "distance_to_nearest_river_m",
}

def read_raw(relpath):
    """Read a source CSV as raw strings: semicolon-delimited, BOM-stripped headers."""
    df = pd.read_csv(os.path.join(SRC, relpath), sep=";", dtype=str,
                     keep_default_na=False, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns=HEADER_MAP)
    # US has a duplicate 'pumping' column (pandas -> 'pumping.1'); verified identical -> drop.
    if "pumping.1" in df.columns:
        assert (df["pumping"] == df["pumping.1"]).all(), "US pumping cols diverge!"
        df = df.drop(columns=["pumping.1"])
    return df

# ============================ MP ============================
MP_COL_ORDER = [
    "well_ID","country","country_name","Long_WGS84","Lat_WGS84","Long_local","Lat_local",
    "EPSG_local","ground_altitude","well_depth","open_from","open_to","pumping",
    "aquifer_thickness","aquifer_lithology","aquifer_karst","confinement",
    "greatest_permeability_zone","distance_to_nearest_river_m",
    "gw_level_data_from","gw_level_data_to","temporal_data_resolution","avg_gw_abs",
    "source_file",
]
MP_NUMERIC = ["Long_WGS84","Lat_WGS84","Long_local","Lat_local","ground_altitude",
              "well_depth","open_from","open_to","aquifer_thickness",
              "greatest_permeability_zone","distance_to_nearest_river_m",
              "gw_level_data_from","gw_level_data_to","avg_gw_abs"]

def num(s):
    """Comma-decimal -> dot, blanks -> NaN, coerce to float."""
    return pd.to_numeric(s.str.strip().str.replace(",", ".", regex=False)
                          .replace({"": None}), errors="coerce")

def tribool(s):
    """TRUE/True/1 -> True, FALSE/False/0 -> False, blank -> NA (nullable boolean)."""
    m = {"true": True, "false": False, "1": True, "0": False}
    return s.str.strip().str.lower().map(m).astype("boolean")

def build_mp():
    faith, clean = [], []
    for cc,(mpf,_) in SOURCES.items():
        raw = read_raw(mpf)
        raw.insert(1, "country", cc)
        raw.insert(2, "country_name", COUNTRY_NAME[cc])
        raw["source_file"] = os.path.basename(mpf)
        faith.append(raw.copy())

        cl = raw.copy()
        cl["well_ID"] = cl["well_ID"].str.strip()
        for col in MP_NUMERIC:
            if col in cl.columns: cl[col] = num(cl[col])
        if "pumping" in cl.columns: cl["pumping"] = tribool(cl["pumping"])
        for col in ["aquifer_karst","confinement"]:
            if col in cl.columns: cl[col] = tribool(cl[col])
        if "aquifer_lithology" in cl.columns:
            cl["aquifer_lithology"] = (cl["aquifer_lithology"].str.strip()
                                       .replace({"": None, "terrigenc": "terrigenic"}))
        if "EPSG_local" in cl.columns:
            cl["EPSG_local"] = pd.to_numeric(
                cl["EPSG_local"].str.extract(r"(\d+)")[0], errors="coerce").astype("Int64")
        if "temporal_data_resolution" in cl.columns:
            cl["temporal_data_resolution"] = (cl["temporal_data_resolution"].str.strip()
                                              .str.lower().replace({"": None}))
        clean.append(cl)

    faith = pd.concat(faith, ignore_index=True)
    clean = pd.concat(clean, ignore_index=True)
    for df in (faith, clean):
        for c in MP_COL_ORDER:
            if c not in df.columns: df[c] = pd.NA
    faith = faith[[c for c in MP_COL_ORDER if c in faith.columns]]
    clean = clean[[c for c in MP_COL_ORDER if c in clean.columns]]
    os.makedirs(MP_OUT, exist_ok=True)
    faith.to_parquet(f"{MP_OUT}/transboundary_mp_faithful.parquet", index=False)
    clean.to_parquet(f"{MP_OUT}/transboundary_mp_clean.parquet", index=False)
    return faith, clean

# ============================ GWTS ============================
GWTS_COL_ORDER = ["well_ID","country","country_name","observation_year","observation_month",
                  "gw_level_abs","gw_level_from_ground","ground_altitude","source_file"]

def build_gwts():
    faith, clean = [], []
    for cc,(_,gtf) in SOURCES.items():
        raw = read_raw(gtf)
        raw.insert(1, "country", cc)
        raw.insert(2, "country_name", COUNTRY_NAME[cc])
        raw["source_file"] = os.path.basename(gtf)
        faith.append(raw.copy())

        cl = raw.copy()
        cl["well_ID"] = cl["well_ID"].str.strip()
        cl["observation_year"]  = pd.to_numeric(cl["observation_year"].str.strip().replace({"":None}),  errors="coerce").astype("Int64")
        cl["observation_month"] = pd.to_numeric(cl["observation_month"].str.strip().replace({"":None}), errors="coerce").astype("Int64")
        for col in ["gw_level_abs","gw_level_from_ground","ground_altitude"]:
            if col in cl.columns: cl[col] = num(cl[col])
        clean.append(cl)

    faith = pd.concat(faith, ignore_index=True)
    clean = pd.concat(clean, ignore_index=True)
    for df in (faith, clean):
        for c in GWTS_COL_ORDER:
            if c not in df.columns: df[c] = pd.NA
    faith = faith[[c for c in GWTS_COL_ORDER if c in faith.columns]]
    clean = clean[[c for c in GWTS_COL_ORDER if c in clean.columns]]
    os.makedirs(GWTS_OUT, exist_ok=True)
    faith.to_parquet(f"{GWTS_OUT}/transboundary_gwts_faithful.parquet", index=False)
    clean.to_parquet(f"{GWTS_OUT}/transboundary_gwts_clean.parquet", index=False)
    return faith, clean

if __name__ == "__main__":
    if not os.path.isdir(SRC):
        raise SystemExit(f"Source folder not found: {SRC}\n"
                         f"Set GRANDEU_SRC to the GRANDE-U folder containing 00_UA ... 06_MX.")
    mp_f, mp_c = build_mp()
    gw_f, gw_c = build_gwts()
    print(f"MP   : faithful {mp_f.shape}  clean {mp_c.shape}  -> {MP_OUT}")
    print(f"GWTS : faithful {gw_f.shape}  clean {gw_c.shape}  -> {GWTS_OUT}")
    print("by country (MP):", mp_c.groupby('country').size().to_dict())
    print("done.")
