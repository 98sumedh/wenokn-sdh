#!/usr/bin/env python3
"""
ETL: build the bundled data for the `jordan-health-geography` skill from Ilya's
jordan-hsa-optimization repo.

Produces (all small, in the skill's data/ folder):
  jordan_health_facilities.parquet   - master facility list (name, type, governorate,
                                        lon/lat, in_infectious/in_ncd network flags)
  jordan_governorates.geojson         - 12 governorate polygons (EPSG:4326)
  jordan_districts.geojson            - 51 district polygons + 2024 population
  population_by_governorate.csv       - 2024 population per governorate
  population_by_district.csv          - 2024 population per district

Only non-sensitive geography is bundled: public health-facility *locations* and
administrative boundaries/population. No patient/case data is included here
(that is synthetic and handled separately, with rates not counts).

SOURCE
------
    export JORDAN_SRC=/path/to/jordan-hsa-optimization
    python scripts/build_jordan_health_geography.py
Defaults to ~/jordan-hsa-optimization.
"""
import os
import pandas as pd
import geopandas as gpd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.environ.get("JORDAN_SRC", os.path.expanduser("~/jordan-hsa-optimization"))
OUT  = os.path.join(REPO, "skills/jordan-health-geography/data")

# Governorate name harmonisation -> canonical English spelling (12 governorates).
GOV_CANON = {
    "Ajlun": "Ajloun", "Ajloun": "Ajloun",
    "Jarash": "Jerash", "Jerash": "Jerash",
    "Tafila": "Tafilah", "Tafilah": "Tafilah",
    "Amman": "Amman", "Irbid": "Irbid", "Zarqa": "Zarqa", "Balqa": "Balqa",
    "Mafraq": "Mafraq", "Karak": "Karak", "Madaba": "Madaba", "Aqaba": "Aqaba",
    "Ma'an": "Ma'an", "Maan": "Ma'an",
}
def canon(s):
    return s.map(lambda x: GOV_CANON.get(str(x).strip(), str(x).strip()))

def build_facilities():
    """Union the per-network facility lists into one master table with network flags."""
    inf_files = ["SYNINF_facility_coordinates.csv", "SYNMODINF_facility_coordinates.csv"]
    ncd_files = ["SYNNCD_facility_coordinates.csv", "SYNMODNCD_facility_coordinates.csv"]
    def load(files):
        fr = [pd.read_csv(os.path.join(SRC, "data", f), encoding="utf-8-sig") for f in files]
        df = pd.concat(fr, ignore_index=True)
        df.columns = [c.strip() for c in df.columns]
        return df
    inf, ncd = load(inf_files), load(ncd_files)
    inf["in_infectious"], inf["in_ncd"] = True, False
    ncd["in_infectious"], ncd["in_ncd"] = False, True
    both = pd.concat([inf, ncd], ignore_index=True)
    both["governorate"] = canon(both["governorate"])
    agg = (both.groupby(["healthfacility","healthfacilitytype","governorate",
                         "Latitude","Longitude"], as_index=False)
                .agg(in_infectious=("in_infectious","max"), in_ncd=("in_ncd","max")))
    agg = agg.rename(columns={"healthfacility":"facility","healthfacilitytype":"facility_type",
                              "Longitude":"lon","Latitude":"lat"})
    return agg[["facility","facility_type","governorate","lon","lat","in_infectious","in_ncd"]]

def build_boundaries_and_population():
    gov = gpd.read_file(os.path.join(SRC, "data", "jordan_governorates.gpkg")).to_crs(4326)
    gov["governorate"] = canon(gov["shapeName"])
    gov = gov[["governorate","geometry"]]

    dist = gpd.read_file(os.path.join(SRC, "data",
                         "adm_boundaries/Jordan_districts_simplified20m.gpkg")).to_crs(4326)
    dist = dist.rename(columns={"name_en":"district","name_ar":"district_ar",
                                "Population 2024":"population_2024"})
    # Assign each district's governorate by spatial join to the governorate polygons
    # (authoritative; the name_en_2 text field has nulls/spelling drift).
    pts = dist[["district","geometry"]].copy()
    pts["geometry"] = dist.representative_point()
    j = gpd.sjoin(pts, gov[["governorate","geometry"]], predicate="within", how="left")
    j = j.drop_duplicates("district").set_index("district")["governorate"]
    dist["governorate"] = dist["district"].map(j)
    dist.loc[dist.governorate.isna(), "governorate"] = canon(dist["name_en_2"])  # fallback
    dist = dist[["district","district_ar","governorate","population_2024","geometry"]]

    # Subdistricts (finer admin level; keep original English + Arabic names + parent district).
    sub = gpd.read_file(os.path.join(SRC, "data",
                        "adm_boundaries/Jordan_subdistricts_simplified20m.gpkg")).to_crs(4326)
    sub["population_2024"] = pd.to_numeric(
        sub["Population 2024"].astype(str).str.replace(",", "", regex=False).replace({"": None}),
        errors="coerce").astype("Int64")
    sub["governorate"] = canon(sub["Governorate"])
    sub = sub.rename(columns={"name_en":"subdistrict",
                              "Sub-District Name in Arabic":"subdistrict_ar",
                              "District":"district"})
    sub = sub[["subdistrict","subdistrict_ar","district","governorate","population_2024","geometry"]]

    pop_gov = (dist.groupby("governorate", as_index=False)["population_2024"].sum()
                   .sort_values("population_2024", ascending=False))
    pop_dist = dist[["district","governorate","population_2024"]].sort_values(
        "population_2024", ascending=False)
    pop_sub = sub[["subdistrict","district","governorate","population_2024"]].sort_values(
        "population_2024", ascending=False)
    return gov, dist, sub, pop_gov, pop_dist, pop_sub

if __name__ == "__main__":
    if not os.path.isdir(os.path.join(SRC, "data")):
        raise SystemExit(f"Source not found: {SRC}. Set JORDAN_SRC to the jordan-hsa-optimization repo.")
    os.makedirs(OUT, exist_ok=True)
    fac = build_facilities()
    gov, dist, sub, pop_gov, pop_dist, pop_sub = build_boundaries_and_population()

    fac.to_parquet(f"{OUT}/jordan_health_facilities.parquet", index=False)
    gov.to_file(f"{OUT}/jordan_governorates.geojson", driver="GeoJSON")
    dist.to_file(f"{OUT}/jordan_districts.geojson", driver="GeoJSON")
    sub.to_file(f"{OUT}/jordan_subdistricts.geojson", driver="GeoJSON")
    pop_gov.to_csv(f"{OUT}/population_by_governorate.csv", index=False)
    pop_dist.to_csv(f"{OUT}/population_by_district.csv", index=False)
    pop_sub.to_csv(f"{OUT}/population_by_subdistrict.csv", index=False)

    print("facilities:", fac.shape, "| INF:", int(fac.in_infectious.sum()), "NCD:", int(fac.in_ncd.sum()))
    print("governorates:", len(gov), "| districts:", len(dist), "| subdistricts:", len(sub))
    print("total 2024 population (gov):", int(pop_gov.population_2024.sum()),
          "| (subdistricts):", int(pop_sub.population_2024.dropna().sum()))
    print("largest subdistrict:", pop_sub.iloc[0].to_dict())
    print("WROTE ->", OUT)
