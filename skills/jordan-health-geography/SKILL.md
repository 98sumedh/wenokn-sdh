---
name: jordan-health-geography
description: >-
  Jordan health facilities and administrative geography: where hospitals and
  health centers are, counts and types of facilities by governorate, the 12
  governorates, 51 districts, and 89 subdistricts of Jordan as map layers, and
  2024 population by governorate, district, and subdistrict. Use whenever the
  user asks about health facilities, hospitals, clinics/centers, governorates,
  districts, subdistricts, or population IN JORDAN — e.g. "hospitals in Amman",
  "facilities per governorate", "population of each district", "largest
  subdistrict". Returns GeoPandas layers ready to map or save as GeoJSON. This
  skill is Jordan-only and does NOT cover the groundwater, surface-water, or US
  energy datasets. Hospital Service Area (HSA) delineation and disease/health-
  outcome analysis are handled by separate Jordan skills.
---

# Jordan Health Geography Skill

This skill exposes **non-sensitive geography** for the Jordan health system:
health-facility **locations**, the country's **administrative boundaries**
(12 governorates, 51 districts, 89 subdistricts), and **2024 population**. It
answers "where / how many / how big" questions and produces map-ready layers.

It deliberately contains **no patient or disease-case data** — that data is
sensitive (Ministry of Health), so case-level analysis is done separately on a
synthetic dataset and reported as **rates or model results, not raw counts**
(see the planned `jordan-health-rates` / `jordan-hsa` skills).

## What's bundled (all built from Ilya's `jordan-hsa-optimization` repo)

| File | Contents |
|---|---|
| `data/jordan_health_facilities.parquet` | 201 facilities: name, type, governorate, lon/lat, `in_infectious` / `in_ncd` network flags |
| `data/jordan_governorates.geojson` | 12 governorate polygons (EPSG:4326) |
| `data/jordan_districts.geojson` | 51 district polygons + `district_ar` + `population_2024` |
| `data/jordan_subdistricts.geojson` | 89 subdistrict polygons + `subdistrict_ar` + parent `district` + `population_2024` |
| `data/population_by_governorate.csv` | 2024 population per governorate |
| `data/population_by_district.csv` | 2024 population per district |
| `data/population_by_subdistrict.csv` | 2024 population per subdistrict |

Total 2024 population: **11,625,745** (district tabulation). Facilities by type:
Primary Center 103, Comprehensive Center 70, Hospital 21, Specialized Medical
Center 3, Field Hospital 3, Educational Hospital 1. Original English **and
Arabic** admin names are preserved.

## Honest caveats (state these when relevant)

- **Facilities are the "2024 dataset."** Label facility counts and locations as
  the **2024 dataset** (188 in the infectious-disease network, 195 in the
  non-communicable-disease network, 201 unique overall). A separate 2026 version
  is being prepared and may change these counts. Use the `in_infectious` /
  `in_ncd` flags to say which network a facility belongs to.
- **No case data here.** Do not report disease counts from this skill; it has
  none. Population is public 2024 data.
- **District vs subdistrict totals differ slightly** (district total 11,625,745
  vs subdistrict total 11,734,000) — these are two separate tabulations in the
  source data, preserved as-is rather than forced to reconcile. State which
  level you used.
- **Governorate names are harmonised** to one spelling (Jerash, Tafilah,
  Ajloun, Ma'an), since the source files disagreed (Jarash/Jerash, etc.).

## Standard loaders

```python
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

D = "skills/jordan-health-geography/data"

def load_facilities() -> gpd.GeoDataFrame:
    df = pd.read_parquet(f"{D}/jordan_health_facilities.parquet")
    geom = [Point(x, y) for x, y in zip(df.lon, df.lat)]
    return gpd.GeoDataFrame(df, geometry=geom, crs="EPSG:4326")

def load_governorates() -> gpd.GeoDataFrame:
    return gpd.read_file(f"{D}/jordan_governorates.geojson")

def load_districts() -> gpd.GeoDataFrame:
    # includes district_ar and the population_2024 column
    return gpd.read_file(f"{D}/jordan_districts.geojson")

def load_subdistricts() -> gpd.GeoDataFrame:
    # 89 subdistricts, with parent district, subdistrict_ar, and population_2024
    return gpd.read_file(f"{D}/jordan_subdistricts.geojson")

def population_by_governorate() -> pd.DataFrame:
    return pd.read_csv(f"{D}/population_by_governorate.csv")

def population_by_district() -> pd.DataFrame:
    return pd.read_csv(f"{D}/population_by_district.csv")

def population_by_subdistrict() -> pd.DataFrame:
    return pd.read_csv(f"{D}/population_by_subdistrict.csv")
```

## Example queries (verified against the bundled data)

### Hospitals in a governorate (e.g. Amman)

```python
fac = load_facilities()
amman_hosp = fac[(fac.governorate == "Amman") & (fac.facility_type == "Hospital")]
amman_hosp.to_file(os.path.join(temp_dir, "amman_hospitals.geojson"), driver="GeoJSON")
print(len(amman_hosp))   # 3 hospitals; 59 facilities of all types in Amman
```

### Health facilities per governorate

```python
fac = load_facilities()
print(fac.governorate.value_counts())
# Amman 59, Karak 41, Irbid 21, Mafraq 16, Zarqa 13, Balqa 12, Madaba 11,
# Jerash 10, Ajloun 6, Aqaba 5, Ma'an 4, Tafilah 3  (current synthetic version)
```

### Facilities in one governorate, mapped (e.g. Irbid)

```python
fac = load_facilities()
irbid = fac[fac.governorate == "Irbid"]           # 21 facilities
irbid.to_file(os.path.join(temp_dir, "irbid_facilities.geojson"), driver="GeoJSON")
```

### 2024 population by governorate / district

```python
print(population_by_governorate())     # Amman 4,920,100 is largest
d = load_districts()
d.nlargest(5, "population_2024")[["district","governorate","population_2024"]]
# Most populous district: Marka District (Amman), 1,173,825
d.to_file(os.path.join(temp_dir, "jordan_districts.geojson"), driver="GeoJSON")
```

### Facilities of the non-communicable-disease network

```python
fac = load_facilities()
ncd = fac[fac.in_ncd]      # 195 facilities (infectious network: 188)
```

### Map all governorate boundaries

```python
load_governorates().to_file(os.path.join(temp_dir, "jordan_governorates.geojson"),
                            driver="GeoJSON")
```

### Largest subdistrict, and subdistricts of a district

```python
sub = load_subdistricts()
biggest = sub.loc[sub.population_2024.idxmax()]
print(biggest[["subdistrict","district","governorate","population_2024"]])
# Largest subdistrict: Marka Sub-District (Marka District, Amman), 1,173,825

# Subdistricts in the largest district (by population)
pd_ = population_by_district()
top_district = pd_.iloc[0].district                      # Marka District
in_district = sub[sub.district == top_district]          # 1 subdistrict (Marka)

# Subdistrict count per governorate
print(sub.governorate.value_counts())
# Mafraq 14, Amman 13, Karak 10, Irbid 9, Balqa 8, Ma'an 8, Madaba 7,
# Zarqa 6, Aqaba 4, Ajloun 4, Jerash 3, Tafilah 3
```

## Provenance

All data is derived from Ilya Zaslavsky's `jordan-hsa-optimization` repository:
facility coordinates from the `SYN*_facility_coordinates.csv` files, boundaries
from `jordan_governorates.gpkg` and `Jordan_districts_simplified20m.gpkg`, and
2024 population from the districts layer. The ETL that builds these bundled
files is `scripts/build_jordan_health_geography.py` (re-runnable via
`JORDAN_SRC`).

## Reporting tips

- Always say **Jordan**, and name the **governorate/district**.
- When reporting facility counts, add the caveat that this is the current
  synthetic-dataset version and may change with an updated MoH facility list.
- For disease burden, HSA service areas, or climate-health relationships, defer
  to the dedicated Jordan health skills — this one is geography only.
