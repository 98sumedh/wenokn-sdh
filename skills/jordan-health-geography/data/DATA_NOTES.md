# Jordan Health Geography — Data Notes

Built by `scripts/build_jordan_health_geography.py` from Ilya Zaslavsky's
`jordan-hsa-optimization` repository. Only non-sensitive geography is bundled;
no patient/disease-case data is included.

## Sources

- **Facilities**: union of `SYN(MOD)INF_facility_coordinates.csv` (infectious-
  disease network, 188) and `SYN(MOD)NCD_facility_coordinates.csv` (non-
  communicable-disease network, 195). Deduped to **201 unique facilities** with
  `in_infectious` / `in_ncd` flags. Facility *locations* are not sensitive.
- **Boundaries**: `jordan_governorates.gpkg` (12),
  `Jordan_districts_simplified20m.gpkg` (51), and
  `Jordan_subdistricts_simplified20m.gpkg` (89), reprojected to EPSG:4326.
  Original English **and Arabic** admin names are preserved (`district_ar`,
  `subdistrict_ar`).
- **Population**: `Population 2024` field of the district and subdistrict layers,
  aggregated to governorate level. Facility counts/locations are the **2024
  dataset** (a separate 2026 version is being prepared).

## Decisions / fixes

- **Governorate names harmonised** to one spelling — the sources disagreed
  (Jarash vs Jerash, Tafila vs Tafilah, Ajlun vs Ajloun, Maan vs Ma'an).
- **District → governorate by spatial join** to the governorate polygons, not
  the `name_en_2` text field, which had nulls (a district with 133,675 people
  was unassigned) and spelling drift. The spatial join assigns every district
  cleanly; national population total is unchanged.
- **District and subdistrict population totals differ slightly** (11,625,745 vs
  11,734,000). These are two separate tabulations in the source; kept as-is
  rather than forced to reconcile (state which level you used).

## Known limitations (do not paper over)

- **Facility counts are version-dependent.** This is the current synthetic-
  dataset facility list. Ilya has a newer Ministry of Health facility list
  (substantially larger, NCD) not yet incorporated — so facility counts should
  be reported as "current version", and could be tagged as a dataset version
  once the newer list is available.
- **No case data.** Disease burden must be reported as rates / model results
  from the synthetic dataset in the dedicated health skills, never as raw counts
  from here.
- Population is 2024 from the district boundaries file; not derived from the
  bundled WorldPop rasters (those remain available in the source repo for
  pixel-level allocation used by the HSA workflow).
