# Notebook Results: HSA_FINAL

- Generated: 2026-07-13T10:56:42
- Network: INF
- HSA mode: footprint

## Important Output Files

- `out/INF_governorate_fewest_map_v8.png`
- `out/INF_governorate_tau_coverage_map_v8.png`
- `out/INF_distance_map_v8.png`
- `out/INF_footprint_map_v8.png`
- `out/INF_fewest_map_v8.png`
- `out/INF_governorate_fewest_map_v7.png`
- `out/INF_governorate_tau_coverage_map_v7.png`
- `out/INF_distance_map_v7.png`
- `out/INF_footprint_map_v7.png`
- `out/INF_fewest_map_v7.png`
- `out/INF_governorate_fewest_map_v6.png`
- `out/INF_governorate_tau_coverage_map_v6.png`
- `out/INF_distance_map_v6.png`
- `out/INF_footprint_map_v6.png`
- `out/INF_fewest_map_v6.png`
- `out/INF_governorate_fewest_hsas_v8.geojson`
- `out/INF_governorate_fewest_satellite_bubble_audit_v8.csv`
- `out/INF_governorate_fewest_major_orphan_anchor_audit_v8.csv`
- `out/INF_governorate_fewest_anchor_upgrade_audit_v8.csv`
- `out/INF_governorate_tau_coverage_hsas_v8.geojson`
- `out/INF_governorate_tau_coverage_satellite_bubble_audit_v8.csv`
- `out/INF_governorate_tau_coverage_major_orphan_anchor_audit_v8.csv`
- `out/INF_governorate_tau_coverage_anchor_upgrade_audit_v8.csv`
- `out/INF_distance_hsas_v8.geojson`
- `out/INF_distance_satellite_bubble_audit_v8.csv`
- `out/INF_distance_major_orphan_anchor_audit_v8.csv`
- `out/INF_distance_anchor_upgrade_audit_v8.csv`
- `out/INF_footprint_hsas_v8.geojson`
- `out/INF_footprint_satellite_bubble_audit_v8.csv`
- `out/INF_footprint_major_orphan_anchor_audit_v8.csv`
- `out/INF_footprint_anchor_upgrade_audit_v8.csv`
- `out/INF_fewest_hsas_v8.geojson`
- `out/INF_fewest_satellite_bubble_audit_v8.csv`
- `out/INF_fewest_major_orphan_anchor_audit_v8.csv`
- `out/INF_fewest_anchor_upgrade_audit_v8.csv`
- `out/INF_governorate_fewest_hsas_v7.geojson`
- `out/INF_governorate_fewest_major_orphan_anchor_audit_v7.csv`
- `out/INF_governorate_fewest_anchor_upgrade_audit_v7.csv`
- `out/INF_governorate_tau_coverage_hsas_v7.geojson`
- `out/INF_governorate_tau_coverage_major_orphan_anchor_audit_v7.csv`
- `out/INF_governorate_tau_coverage_anchor_upgrade_audit_v7.csv`
- `out/INF_distance_hsas_v7.geojson`
- `out/INF_distance_major_orphan_anchor_audit_v7.csv`
- `out/INF_distance_anchor_upgrade_audit_v7.csv`
- `out/INF_footprint_hsas_v7.geojson`
- `out/INF_footprint_major_orphan_anchor_audit_v7.csv`
- `out/INF_footprint_anchor_upgrade_audit_v7.csv`
- `out/INF_fewest_hsas_v7.geojson`
- `out/INF_fewest_major_orphan_anchor_audit_v7.csv`
- `out/INF_fewest_anchor_upgrade_audit_v7.csv`
- `out/INF_governorate_fewest_hsas_v6.geojson`
- `out/INF_governorate_tau_coverage_hsas_v6.geojson`
- `out/INF_distance_hsas_v6.geojson`
- `out/INF_footprint_hsas_v6.geojson`
- `out/INF_fewest_hsas_v6.geojson`
- `out/INF_footprint_patient_data_discrepancies.txt`
- `out/INF_footprint_diagnosis_counts_pivot.csv`
- `out/INF_footprint_diagnosis_counts_by_group.csv`
- `out/INF_footprint_diagnosis_counts_total.csv`
- `out/INF_Facilities_Climate_Features_with_clusters.csv`

## Displayed Cell Outputs

### Cell 2

```text
================================================================================
CONFIGURATION LOADED
================================================================================
Network: INF
Main modes target coverage: 90%
Governorate mode coverage: 90%
Coarsen factor: 4x (full resolution)
Urban base radius: 10.0 km
Rural base radius: 18.0 km
Climate diversity: True
  v6: promote_major=False, upgrade_anchors=False, satellite_bubbles=False
  v7: promote_major=True, upgrade_anchors=True, satellite_bubbles=False
  v8: promote_major=True, upgrade_anchors=True, satellite_bubbles=True
Optimization is score-driven, with major uncovered facilities promoted after selection
================================================================================
```

### Cell 3

```text
Preparing diagnosis counts for INF...
================================================================================
GENERATE DIAGNOSIS COUNTS FROM AUTHORITATIVE FACILITIES (V2)
================================================================================
Networks: INF

================================================================================
PROCESSING INF NETWORK
================================================================================

Loading authoritative facilities: SYNMODINF_facility_coordinates.csv
  Loaded 188 authoritative facilities
  Unique governorates: 12

Loading diagnosis groups: SYNMODINF_groups_of_diagnoses.csv
  Loaded 157 diagnosis mappings
  Unique groups: 15

Loading patient data: SYNMODINF_patient_visits.csv
  Total records: 66,876
  Unique patients: 66,876
  Unique facility-governorate pairs: 188

Matching patient data to authoritative facilities...

  Records matched to authoritative: 66,876 (100.0%)
  Records NOT in authoritative: 0
  Discrepancy types found: 0

Assigning diagnosis groups...
  Diagnoses with groups: 66,876 (100.0%)

Deduplicating diagnoses...
  Original diagnoses: 66,876
  Duplicates removed: 0 (0.0%)
  Unique diagnoses: 66,876

Creating diagnosis count tables...
  [OK] Saved: INF_footprint_diagnosis_counts_total.csv (188 facilities)
  [OK] Saved: INF_footprint_diagnosis_counts_by_group.csv (1640 rows)
  [OK] Saved: INF_footprint_diagnosis_counts_pivot.csv (188 facilities)

================================================================================
GENERATING DISCREPANCY REPORT
================================================================================

[OK] Saved: INF_footprint_patient_data_discrepancies.txt

================================================================================
PROCESSING COMPLETE
================================================================================

INF Network:
  Total diagnoses: 66,876
  Facilities: 188
  Discrepancies: 0

Output files:
  - INF_footprint_diagnosis_counts_total.csv
  - INF_footprint_diagnosis_counts_by_group.csv
  - INF_footprint_diagnosis_counts_pivot.csv
  - INF_footprint_patient_data_discrepancies.txt
✓ Diagnosis counts ready: out/INF_footprint_diagnosis_counts_pivot.csv
```

### Cell 4

```text
The autoreload extension is already loaded. To reload it, use:
  %reload_ext autoreload
Injecting parameters into hsa_optimization module...
================================================================================
IMPORTS AND PARAMETER INJECTION COMPLETE
================================================================================
Parameters injected: 22/22
================================================================================
```

### Cell 6

```text

################################################################################
ALGORITHM VARIANT: v6 — Greedy only (original algorithm)
################################################################################


Merged climate + diagnosis data:
  Facilities with climate data: 188
  Facilities with diagnosis counts: 188
  Facilities after merge: 188
  Facilities with Total column: 188
  Facilities with Total > 0: 188
  Facilities with HealthFacility column: True
Loaded 188 INF facilities 
  climate_k column present: YES
  climate_k values: [np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4), np.int64(5), np.int64(6), np.int64(7)]

================================================================================
Running FEWEST optimization...
================================================================================

============================================================
Running FEWEST optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running FEWEST algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=15.00, progress=0.00, overlap=0.10, patient_vol=0.00, climate=0.00, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Target coverage for fewest: 90.0%
    Selected 5 so far; 68.1% coverage.
    Selected 10 so far; 83.9% coverage.
    [STOPPED] Reached 90% coverage with 15 HSAs
  [4/4] Finalizing selection...
  Final: 15 HSAs, 90.2% coverage

Post-processing FEWEST: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 15/15 facilities (removed 0)

Optimization complete:
  Selected facilities: 15
  Population covered: 9,205,451 (90.2%)

================================================================================
FEWEST OPTIMIZATION COMPLETE
================================================================================
Selected: 15 HSAs
Coverage: 90.2%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 8074 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4338 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4149 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 5294 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 4990 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2739 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] Arish Primary Center: 5384 populated cells (smoothed)
  [pop-clip] Bsaira Comprehensive Center: 1298 populated cells (smoothed)
  [pop-clip] East Thhaibeh Primary Center: 6324 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3572 populated cells (smoothed)
  [pop-clip] Aqaba Comprehensive Center: 1608 populated cells (smoothed)
  Saved: INF_fewest_hsas_v6.geojson
  Columns in saved file: 51
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running FOOTPRINT optimization...
================================================================================

============================================================
Running FOOTPRINT optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running FOOTPRINT algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=0.80, progress=0.00, overlap=0.01, patient_vol=0.00, climate=1.20, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Target coverage for footprint: 90.0%
    Selected 5 so far; 66.3% coverage.
    Selected 10 so far; 80.1% coverage.
    Selected 15 so far; 86.1% coverage.
    [STOPPED] Reached 90% coverage with 19 HSAs
  [4/4] Finalizing selection...
  Final: 19 HSAs, 90.4% coverage

Post-processing FOOTPRINT: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 17/19 facilities (removed 2)

Optimization complete:
  Selected facilities: 17
  Population covered: 9,210,142 (90.3%)

================================================================================
FOOTPRINT OPTIMIZATION COMPLETE
================================================================================
Selected: 17 HSAs
Coverage: 90.3%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3209 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 5143 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4338 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1518 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4149 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 4864 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 5294 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 4990 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2739 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] Bsaira Comprehensive Center: 1298 populated cells (smoothed)
  [pop-clip] Al-Salaihy Primary Center: 6214 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3572 populated cells (smoothed)
  [pop-clip] Jadaa Primary Center: 1369 populated cells (smoothed)
  Saved: INF_footprint_hsas_v6.geojson
  Columns in saved file: 51
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running DISTANCE optimization...
================================================================================

============================================================
Running DISTANCE optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running DISTANCE algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=0.50, progress=0.00, overlap=0.20, patient_vol=0.00, climate=0.05, distance=8.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks with distance metrics...
    Built 188 coverage masks with distance metrics
  [3/4] Running greedy selection...
  Target coverage for distance: 90.0%
    Selected 5 so far; 60.4% coverage.
    Selected 10 so far; 73.3% coverage.
    Selected 15 so far; 85.0% coverage.
    Selected 20 so far; 89.8% coverage.
    [STOPPED] Reached 90% coverage with 21 HSAs
  [4/4] Finalizing selection...
  Final: 21 HSAs, 90.9% coverage

Post-processing DISTANCE: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 21/21 facilities (removed 0)

Optimization complete:
  Selected facilities: 21
  Population covered: 9,271,343 (90.9%)

================================================================================
DISTANCE OPTIMIZATION COMPLETE
================================================================================
Selected: 21 HSAs
Coverage: 90.9%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 5850 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3209 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 4864 populated cells (smoothed)
  [pop-clip] Marj AL Hamam CC: 5168 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] Zarqa Comprehensive Center: 3756 populated cells (smoothed)
  [pop-clip] Bsaira Comprehensive Center: 1298 populated cells (smoothed)
  [pop-clip] Petra Comprehensive Center: 917 populated cells (smoothed)
  [pop-clip] Hay Al-Hussein Primary Center: 4728 populated cells (smoothed)
  [pop-clip] West Ramtha Primary Center: 5435 populated cells (smoothed)
  [pop-clip] Mobes Primary Center: 2340 populated cells (smoothed)
  [pop-clip] Hawiyyeh Primary Center: 2610 populated cells (smoothed)
  [pop-clip] Souf Primary Center: 3835 populated cells (smoothed)
  [pop-clip] North Madaba Comprehensive Center: 4291 populated cells (smoothed)
  [pop-clip] Al Saro Primary Center: 3405 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3572 populated cells (smoothed)
  [pop-clip] Aqaba Comprehensive Center: 1608 populated cells (smoothed)
  [pop-clip] Jadaa Primary Center: 1369 populated cells (smoothed)
  Saved: INF_distance_hsas_v6.geojson
  Columns in saved file: 51
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running GOVERNORATE_TAU_COVERAGE optimization...
================================================================================

============================================================
Running GOVERNORATE_TAU_COVERAGE optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running GOVERNORATE algorithm (at least one HSA per governorate)...
  Governorate column: shapeName
  Unique governorates: 12
  Assigning adaptive radii to facilities...
    Adaptive radii stats: mean=10.0 km, p10=7.6 km, p90=12.4 km
  Building coverage masks with adaptive radii...
    Phase 1: Ensuring one facility per governorate...
    Phase 1 complete: 12 facilities (one per governorate)
    Phase 2: Continuing greedy selection to reach 90% coverage...
    Selected 15 total; 79.0% of total population covered.
    Selected 20 total; 80.6% of total population covered.
    Selected 25 total; 82.1% of total population covered.
    Selected 30 total; 84.9% of total population covered.
    Selected 35 total; 85.2% of total population covered.
    Selected 40 total; 87.0% of total population covered.
    Selected 45 total; 87.2% of total population covered.
    Selected 50 total; 87.2% of total population covered.
    Selected 55 total; 87.2% of total population covered.
    Selected 60 total; 87.2% of total population covered.
    Selected 65 total; 87.2% of total population covered.
    Selected 70 total; 88.0% of total population covered.
    Selected 75 total; 88.0% of total population covered.
    Selected 80 total; 88.5% of total population covered.
    Selected 85 total; 88.5% of total population covered.
    Selected 90 total; 89.0% of total population covered.
    Selected 95 total; 89.3% of total population covered.
    Selected 100 total; 89.3% of total population covered.
    Selected 105 total; 89.7% of total population covered.
    Selected 110 total; 89.8% of total population covered.
    Selected 115 total; 89.9% of total population covered.
    [ACCEPTED] 119 HSAs, coverage: 90.0%
    Governorates covered: 12/12

Post-processing GOVERNORATE_TAU_COVERAGE: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 35/119 facilities (removed 84)

Optimization complete:
  Selected facilities: 35
  Population covered: 9,105,233 (89.2%)

================================================================================
GOVERNORATE_TAU_COVERAGE OPTIMIZATION COMPLETE
================================================================================
Selected: 35 HSAs
Coverage: 89.2%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 13356 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 6631 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 4049 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 2013 populated cells (smoothed)
  [pop-clip] Maan Hospital: 837 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 2280 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 4448 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 6113 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1316 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 889 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 2571 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 2373 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 8145 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 2825 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 2933 populated cells (smoothed)
  [pop-clip] Marj AL Hamam CC: 9516 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2067 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 781 populated cells (smoothed)
  [pop-clip] Eskan Abu-Nsseir Al-Shamel Al-Tadribi: 7375 populated cells (smoothed)
  [pop-clip] Al-Razi Comprehensive Center: 2831 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 2412 populated cells (smoothed)
  [pop-clip] South Mazar Comprehensive Center: 1661 populated cells (smoothed)
  [pop-clip] Rehab Comprehensive Center: 1632 populated cells (smoothed)
  [pop-clip] Bsaira Comprehensive Center: 692 populated cells (smoothed)
  [pop-clip] Petra Comprehensive Center: 657 populated cells (smoothed)
  [pop-clip] Balaama Comprehensive Center: 1293 populated cells (smoothed)
  [pop-clip] Moaab Primary Center: 1356 populated cells (smoothed)
  [pop-clip] Muwaqqar Comprehensive Center: 2018 populated cells (smoothed)
  [pop-clip] That Ras Primary Center: 574 populated cells (smoothed)
  [pop-clip] Ader Primary Center: 1279 populated cells (smoothed)
  [pop-clip] Qafqafa Primary Center: 1675 populated cells (smoothed)
  [pop-clip] Qatraneh Comprehansive Center: 188 populated cells (smoothed)
  [pop-clip] North Badiyah Hospital: 1913 populated cells (smoothed)
  [pop-clip] Shehabyyeh Primary Center: 1139 populated cells (smoothed)
  [pop-clip] Al-Iman Hospital: 1379 populated cells (smoothed)
  Saved: INF_governorate_tau_coverage_hsas_v6.geojson
  Columns in saved file: 44
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 13.0 km (should be <= 30.0)
  File verified successfully

================================================================================
Running GOVERNORATE_FEWEST optimization...
================================================================================

============================================================
Running GOVERNORATE_FEWEST optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running GOVERNORATE_FEWEST algorithm (1 per governorate + FEWEST optimization)...
  Governorate column: shapeName
  Unique governorates: 12
  Step 1: Pre-selecting highest volume facility per governorate...
    Amman: Al-Basheer Hospital (3286 patients)
    Karak: Al-Karak Hospital (656 patients)
    Balqa: AL-Shuneh Hospital (1663 patients)
    Ajloun: Al-Iman Hospital (102 patients)
    Irbid: Princess Rahma Hospital (2880 patients)
    Madaba: AL-Nadeem Hospital (1450 patients)
    Mafraq: Al-Mafraq Gynecology and Pediatrics Hospital (669 patients)
    Jerash: Jarash Hospital (849 patients)
    Zarqa: AL-Zarqa Hospital (1050 patients)
    Aqaba: Khazzan Primary Center (899 patients)
    Tafilah: Tafilah Governmental Hospital (564 patients)
    Ma'an: Maan Hospital (1480 patients)
  Pre-selected 12 facilities (1 per governorate)

  Step 2: Running FEWEST optimization to reach 95% national coverage...

Running FEWEST algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=15.00, progress=0.00, overlap=0.10, patient_vol=0.00, climate=0.00, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Initializing with 12 pre-selected facilities...
  Target coverage for fewest: 90.0%
    Selected 15 so far; 85.6% coverage.
    [STOPPED] Reached 90% coverage with 18 HSAs
  [4/4] Finalizing selection...
  Final: 18 HSAs, 90.3% coverage

  GOVERNORATE_FEWEST complete: 18 HSAs
  Governorates represented: 12/12

Post-processing GOVERNORATE_FEWEST: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 18/18 facilities (removed 0)

Optimization complete:
  Selected facilities: 18
  Population covered: 9,214,720 (90.3%)

================================================================================
GOVERNORATE_FEWEST OPTIMIZATION COMPLETE
================================================================================
Selected: 18 HSAs
Coverage: 90.3%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 5850 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3209 populated cells (smoothed)
  [pop-clip] Maan Hospital: 862 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 5143 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 8074 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4338 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1518 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4149 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 5294 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 4990 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2739 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1041 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] West Thhaibeh Primary Center: 7908 populated cells (smoothed)
  [pop-clip] Al-Iman Hospital: 3524 populated cells (smoothed)
  Saved: INF_governorate_fewest_hsas_v6.geojson
  Columns in saved file: 53
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully


================================================================================
ALL OPTIMIZATIONS COMPLETE
================================================================================
  FEWEST                    :  15 HSAs, 90.2% coverage
  FOOTPRINT                 :  17 HSAs, 90.3% coverage
  DISTANCE                  :  21 HSAs, 90.9% coverage
  GOVERNORATE_TAU_COVERAGE  :  35 HSAs, 89.2% coverage
  GOVERNORATE_FEWEST        :  18 HSAs, 90.3% coverage

################################################################################
ALGORITHM VARIANT: v7 — Anchor upgrade/demotion + major-orphan promotion
################################################################################


Merged climate + diagnosis data:
  Facilities with climate data: 188
  Facilities with diagnosis counts: 188
  Facilities after merge: 188
  Facilities with Total column: 188
  Facilities with Total > 0: 188
  Facilities with HealthFacility column: True
Loaded 188 INF facilities 
  climate_k column present: YES
  climate_k values: [np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4), np.int64(5), np.int64(6), np.int64(7)]

================================================================================
Running FEWEST optimization...
================================================================================

============================================================
Running FEWEST optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running FEWEST algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=15.00, progress=0.00, overlap=0.10, patient_vol=0.00, climate=0.00, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Target coverage for fewest: 90.0%
    Selected 5 so far; 68.1% coverage.
    Selected 10 so far; 83.9% coverage.
    [STOPPED] Reached 90% coverage with 15 HSAs
  [4/4] Finalizing selection...
  Final: 15 HSAs, 90.2% coverage

Post-processing FEWEST: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 15/15 facilities (removed 0)

Optimization complete:
  Selected facilities: 15
  Population covered: 9,205,451 (90.2%)
  Anchor upgrade audit: upgraded 4 anchor(s): Arish Primary Center -> AL-Nadeem Hospital, Bsaira Comprehensive Center -> Tafilah Governmental Hospital, East Thhaibeh Primary Center -> Dr. Jamel Al-Totanji Hospital, Aqaba Comprehensive Center -> Khazzan Primary Center
  Saved anchor upgrade audit: INF_fewest_anchor_upgrade_audit_v7.csv
  Major orphan audit: promoted 2 additional anchor(s): Maan Hospital, Queen Rania Hospital
  Saved major-orphan anchor audit: INF_fewest_major_orphan_anchor_audit_v7.csv

================================================================================
FEWEST OPTIMIZATION COMPLETE
================================================================================
Selected: 17 HSAs
Coverage: 90.2%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 8074 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4338 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4149 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 5294 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 4990 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2739 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 3160 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1030 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 10570 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3572 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1461 populated cells (smoothed)
  [pop-clip] Maan Hospital: 853 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 965 populated cells (smoothed)
  Saved: INF_fewest_hsas_v7.geojson
  Columns in saved file: 56
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running FOOTPRINT optimization...
================================================================================

============================================================
Running FOOTPRINT optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running FOOTPRINT algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=0.80, progress=0.00, overlap=0.01, patient_vol=0.00, climate=1.20, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Target coverage for footprint: 90.0%
    Selected 5 so far; 66.3% coverage.
    Selected 10 so far; 80.1% coverage.
    Selected 15 so far; 86.1% coverage.
    [STOPPED] Reached 90% coverage with 19 HSAs
  [4/4] Finalizing selection...
  Final: 19 HSAs, 90.4% coverage

Post-processing FOOTPRINT: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 17/19 facilities (removed 2)

Optimization complete:
  Selected facilities: 17
  Population covered: 9,210,142 (90.3%)
  Anchor upgrade audit: upgraded 2 anchor(s): Bsaira Comprehensive Center -> Tafilah Governmental Hospital, Al-Salaihy Primary Center -> Al Hussain New Salt Hospital
  Saved anchor upgrade audit: INF_footprint_anchor_upgrade_audit_v7.csv
  Major orphan audit: promoted 2 additional anchor(s): Maan Hospital, Queen Rania Hospital
  Saved major-orphan anchor audit: INF_footprint_major_orphan_anchor_audit_v7.csv

================================================================================
FOOTPRINT OPTIMIZATION COMPLETE
================================================================================
Selected: 19 HSAs
Coverage: 90.3%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3209 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 5143 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4338 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1518 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4149 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 4864 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 5294 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 4990 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2739 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1030 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 6045 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3572 populated cells (smoothed)
  [pop-clip] Jadaa Primary Center: 1369 populated cells (smoothed)
  [pop-clip] Maan Hospital: 845 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 1017 populated cells (smoothed)
  Saved: INF_footprint_hsas_v7.geojson
  Columns in saved file: 56
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running DISTANCE optimization...
================================================================================

============================================================
Running DISTANCE optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running DISTANCE algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=0.50, progress=0.00, overlap=0.20, patient_vol=0.00, climate=0.05, distance=8.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks with distance metrics...
    Built 188 coverage masks with distance metrics
  [3/4] Running greedy selection...
  Target coverage for distance: 90.0%
    Selected 5 so far; 60.4% coverage.
    Selected 10 so far; 73.3% coverage.
    Selected 15 so far; 85.0% coverage.
    Selected 20 so far; 89.8% coverage.
    [STOPPED] Reached 90% coverage with 21 HSAs
  [4/4] Finalizing selection...
  Final: 21 HSAs, 90.9% coverage

Post-processing DISTANCE: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 21/21 facilities (removed 0)

Optimization complete:
  Selected facilities: 21
  Population covered: 9,271,343 (90.9%)
  Anchor upgrade audit: upgraded 10 anchor(s): Zarqa Comprehensive Center -> AL-Zarqa Hospital, Bsaira Comprehensive Center -> Tafilah Governmental Hospital, Petra Comprehensive Center -> Queen Rania Hospital, Hay Al-Hussein Primary Center -> AL-Mafraq Hospital, West Ramtha Primary Center -> AL-Ramtha Hospital, Hawiyyeh Primary Center -> Al-Karak Hospital, Souf Primary Center -> Jarash Hospital, North Madaba Comprehensive Center -> AL-Nadeem Hospital, Al Saro Primary Center -> Al Hussain New Salt Hospital, Aqaba Comprehensive Center -> Khazzan Primary Center
  Saved anchor upgrade audit: INF_distance_anchor_upgrade_audit_v7.csv
  Major orphan audit: no additional anchors required
  Saved major-orphan anchor audit: INF_distance_major_orphan_anchor_audit_v7.csv

================================================================================
DISTANCE OPTIMIZATION COMPLETE
================================================================================
Selected: 21 HSAs
Coverage: 90.9%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 5850 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3209 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 4864 populated cells (smoothed)
  [pop-clip] Marj AL Hamam CC: 5168 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 3825 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1030 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 950 populated cells (smoothed)
  [pop-clip] AL-Mafraq Hospital: 4741 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 4396 populated cells (smoothed)
  [pop-clip] Mobes Primary Center: 2340 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2625 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 3552 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 2878 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 1855 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3572 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1461 populated cells (smoothed)
  [pop-clip] Jadaa Primary Center: 1369 populated cells (smoothed)
  Saved: INF_distance_hsas_v7.geojson
  Columns in saved file: 54
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running GOVERNORATE_TAU_COVERAGE optimization...
================================================================================

============================================================
Running GOVERNORATE_TAU_COVERAGE optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running GOVERNORATE algorithm (at least one HSA per governorate)...
  Governorate column: shapeName
  Unique governorates: 12
  Assigning adaptive radii to facilities...
    Adaptive radii stats: mean=10.0 km, p10=7.6 km, p90=12.4 km
  Building coverage masks with adaptive radii...
    Phase 1: Ensuring one facility per governorate...
    Phase 1 complete: 12 facilities (one per governorate)
    Phase 2: Continuing greedy selection to reach 90% coverage...
    Selected 15 total; 79.0% of total population covered.
    Selected 20 total; 80.6% of total population covered.
    Selected 25 total; 82.1% of total population covered.
    Selected 30 total; 84.9% of total population covered.
    Selected 35 total; 85.2% of total population covered.
    Selected 40 total; 87.0% of total population covered.
    Selected 45 total; 87.2% of total population covered.
    Selected 50 total; 87.2% of total population covered.
    Selected 55 total; 87.2% of total population covered.
    Selected 60 total; 87.2% of total population covered.
    Selected 65 total; 87.2% of total population covered.
    Selected 70 total; 88.0% of total population covered.
    Selected 75 total; 88.0% of total population covered.
    Selected 80 total; 88.5% of total population covered.
    Selected 85 total; 88.5% of total population covered.
    Selected 90 total; 89.0% of total population covered.
    Selected 95 total; 89.3% of total population covered.
    Selected 100 total; 89.3% of total population covered.
    Selected 105 total; 89.7% of total population covered.
    Selected 110 total; 89.8% of total population covered.
    Selected 115 total; 89.9% of total population covered.
    [ACCEPTED] 119 HSAs, coverage: 90.0%
    Governorates covered: 12/12

Post-processing GOVERNORATE_TAU_COVERAGE: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 35/119 facilities (removed 84)

Optimization complete:
  Selected facilities: 35
  Population covered: 9,105,233 (89.2%)
  Anchor upgrade audit: upgraded 3 anchor(s): Marj AL Hamam CC -> Prince Hamzah Hospital, Eskan Abu-Nsseir Al-Shamel Al-Tadribi -> North Hashmi Comprehensive Center, Qafqafa Primary Center -> Jarash Comprehensive Center
  Saved anchor upgrade audit: INF_governorate_tau_coverage_anchor_upgrade_audit_v7.csv
  Major orphan audit: no additional anchors required
  Saved major-orphan anchor audit: INF_governorate_tau_coverage_major_orphan_anchor_audit_v7.csv

================================================================================
GOVERNORATE_TAU_COVERAGE OPTIMIZATION COMPLETE
================================================================================
Selected: 35 HSAs
Coverage: 89.2%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 13356 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 6631 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 4049 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 2013 populated cells (smoothed)
  [pop-clip] Maan Hospital: 837 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 2280 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 4448 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 6113 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1316 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 889 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 2571 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 2373 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 8145 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 2825 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 2933 populated cells (smoothed)
  [pop-clip] Prince Hamzah Hospital: 11603 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2067 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 781 populated cells (smoothed)
  [pop-clip] North Hashmi Comprehensive Center: 11128 populated cells (smoothed)
  [pop-clip] Al-Razi Comprehensive Center: 2831 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 2412 populated cells (smoothed)
  [pop-clip] South Mazar Comprehensive Center: 1661 populated cells (smoothed)
  [pop-clip] Rehab Comprehensive Center: 1632 populated cells (smoothed)
  [pop-clip] Bsaira Comprehensive Center: 692 populated cells (smoothed)
  [pop-clip] Petra Comprehensive Center: 657 populated cells (smoothed)
  [pop-clip] Balaama Comprehensive Center: 1293 populated cells (smoothed)
  [pop-clip] Moaab Primary Center: 1356 populated cells (smoothed)
  [pop-clip] Muwaqqar Comprehensive Center: 2018 populated cells (smoothed)
  [pop-clip] That Ras Primary Center: 574 populated cells (smoothed)
  [pop-clip] Ader Primary Center: 1279 populated cells (smoothed)
  [pop-clip] Jarash Comprehensive Center: 1818 populated cells (smoothed)
  [pop-clip] Qatraneh Comprehansive Center: 188 populated cells (smoothed)
  [pop-clip] North Badiyah Hospital: 1913 populated cells (smoothed)
  [pop-clip] Shehabyyeh Primary Center: 1139 populated cells (smoothed)
  [pop-clip] Al-Iman Hospital: 1379 populated cells (smoothed)
  Saved: INF_governorate_tau_coverage_hsas_v7.geojson
  Columns in saved file: 47
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 13.0 km (should be <= 30.0)
  File verified successfully

================================================================================
Running GOVERNORATE_FEWEST optimization...
================================================================================

============================================================
Running GOVERNORATE_FEWEST optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running GOVERNORATE_FEWEST algorithm (1 per governorate + FEWEST optimization)...
  Governorate column: shapeName
  Unique governorates: 12
  Step 1: Pre-selecting highest volume facility per governorate...
    Amman: Al-Basheer Hospital (3286 patients)
    Karak: Al-Karak Hospital (656 patients)
    Balqa: AL-Shuneh Hospital (1663 patients)
    Ajloun: Al-Iman Hospital (102 patients)
    Irbid: Princess Rahma Hospital (2880 patients)
    Madaba: AL-Nadeem Hospital (1450 patients)
    Mafraq: Al-Mafraq Gynecology and Pediatrics Hospital (669 patients)
    Jerash: Jarash Hospital (849 patients)
    Zarqa: AL-Zarqa Hospital (1050 patients)
    Aqaba: Khazzan Primary Center (899 patients)
    Tafilah: Tafilah Governmental Hospital (564 patients)
    Ma'an: Maan Hospital (1480 patients)
  Pre-selected 12 facilities (1 per governorate)

  Step 2: Running FEWEST optimization to reach 95% national coverage...

Running FEWEST algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=15.00, progress=0.00, overlap=0.10, patient_vol=0.00, climate=0.00, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Initializing with 12 pre-selected facilities...
  Target coverage for fewest: 90.0%
    Selected 15 so far; 85.6% coverage.
    [STOPPED] Reached 90% coverage with 18 HSAs
  [4/4] Finalizing selection...
  Final: 18 HSAs, 90.3% coverage

  GOVERNORATE_FEWEST complete: 18 HSAs
  Governorates represented: 12/12

Post-processing GOVERNORATE_FEWEST: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 18/18 facilities (removed 0)

Optimization complete:
  Selected facilities: 18
  Population covered: 9,214,720 (90.3%)
  Anchor upgrade audit: upgraded 1 anchor(s): West Thhaibeh Primary Center -> Dr. Jamel Al-Totanji Hospital
  Saved anchor upgrade audit: INF_governorate_fewest_anchor_upgrade_audit_v7.csv
  Major orphan audit: no additional anchors required
  Saved major-orphan anchor audit: INF_governorate_fewest_major_orphan_anchor_audit_v7.csv

================================================================================
GOVERNORATE_FEWEST OPTIMIZATION COMPLETE
================================================================================
Selected: 18 HSAs
Coverage: 90.3%

Saving results to GeoJSON...
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 11965 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 5850 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8803 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3209 populated cells (smoothed)
  [pop-clip] Maan Hospital: 862 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 5143 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 8074 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4338 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1518 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4149 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4003 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 5294 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 4990 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2739 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1041 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3396 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 10741 populated cells (smoothed)
  [pop-clip] Al-Iman Hospital: 3524 populated cells (smoothed)
  Saved: INF_governorate_fewest_hsas_v7.geojson
  Columns in saved file: 56
  climate_k preserved: True
  satellite bubbles preserved: False
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully


================================================================================
ALL OPTIMIZATIONS COMPLETE
================================================================================
  FEWEST                    :  17 HSAs, 90.2% coverage
  FOOTPRINT                 :  19 HSAs, 90.3% coverage
  DISTANCE                  :  21 HSAs, 90.9% coverage
  GOVERNORATE_TAU_COVERAGE  :  35 HSAs, 89.2% coverage
  GOVERNORATE_FEWEST        :  18 HSAs, 90.3% coverage

################################################################################
ALGORITHM VARIANT: v8 — Anchor quality-control + satellite bubble boundaries
################################################################################


Merged climate + diagnosis data:
  Facilities with climate data: 188
  Facilities with diagnosis counts: 188
  Facilities after merge: 188
  Facilities with Total column: 188
  Facilities with Total > 0: 188
  Facilities with HealthFacility column: True
Loaded 188 INF facilities 
  climate_k column present: YES
  climate_k values: [np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4), np.int64(5), np.int64(6), np.int64(7)]

================================================================================
Running FEWEST optimization...
================================================================================

============================================================
Running FEWEST optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running FEWEST algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=15.00, progress=0.00, overlap=0.10, patient_vol=0.00, climate=0.00, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Target coverage for fewest: 90.0%
    Selected 5 so far; 68.1% coverage.
    Selected 10 so far; 83.9% coverage.
    [STOPPED] Reached 90% coverage with 15 HSAs
  [4/4] Finalizing selection...
  Final: 15 HSAs, 90.2% coverage

Post-processing FEWEST: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 15/15 facilities (removed 0)

Optimization complete:
  Selected facilities: 15
  Population covered: 9,205,451 (90.2%)
  Anchor upgrade audit: upgraded 4 anchor(s): Arish Primary Center -> AL-Nadeem Hospital, Bsaira Comprehensive Center -> Tafilah Governmental Hospital, East Thhaibeh Primary Center -> Dr. Jamel Al-Totanji Hospital, Aqaba Comprehensive Center -> Khazzan Primary Center
  Saved anchor upgrade audit: INF_fewest_anchor_upgrade_audit_v8.csv
  Major orphan audit: promoted 2 additional anchor(s): Maan Hospital, Queen Rania Hospital
  Saved major-orphan anchor audit: INF_fewest_major_orphan_anchor_audit_v8.csv

================================================================================
FEWEST OPTIMIZATION COMPLETE
================================================================================
Selected: 17 HSAs
Coverage: 90.2%

Saving results to GeoJSON...
  Satellite bubble geometry: added 40 bubble(s), 625.6 km2 before population clipping
  Saved satellite bubble audit: INF_fewest_satellite_bubble_audit_v8.csv
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 12726 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 9089 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 8437 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4518 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4506 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4662 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 6603 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 5257 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2994 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3400 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 3218 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1083 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 11499 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3570 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1461 populated cells (smoothed)
  [pop-clip] Maan Hospital: 851 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 984 populated cells (smoothed)
  Saved: INF_fewest_hsas_v8.geojson
  Columns in saved file: 60
  climate_k preserved: True
  satellite bubbles preserved: True
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running FOOTPRINT optimization...
================================================================================

============================================================
Running FOOTPRINT optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running FOOTPRINT algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=0.80, progress=0.00, overlap=0.01, patient_vol=0.00, climate=1.20, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Target coverage for footprint: 90.0%
    Selected 5 so far; 66.3% coverage.
    Selected 10 so far; 80.1% coverage.
    Selected 15 so far; 86.1% coverage.
    [STOPPED] Reached 90% coverage with 19 HSAs
  [4/4] Finalizing selection...
  Final: 19 HSAs, 90.4% coverage

Post-processing FOOTPRINT: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 17/19 facilities (removed 2)

Optimization complete:
  Selected facilities: 17
  Population covered: 9,210,142 (90.3%)
  Anchor upgrade audit: upgraded 2 anchor(s): Bsaira Comprehensive Center -> Tafilah Governmental Hospital, Al-Salaihy Primary Center -> Al Hussain New Salt Hospital
  Saved anchor upgrade audit: INF_footprint_anchor_upgrade_audit_v8.csv
  Major orphan audit: promoted 2 additional anchor(s): Maan Hospital, Queen Rania Hospital
  Saved major-orphan anchor audit: INF_footprint_major_orphan_anchor_audit_v8.csv

================================================================================
FOOTPRINT OPTIMIZATION COMPLETE
================================================================================
Selected: 19 HSAs
Coverage: 90.3%

Saving results to GeoJSON...
  Satellite bubble geometry: added 42 bubble(s), 561.8 km2 before population clipping
  Saved satellite bubble audit: INF_footprint_satellite_bubble_audit_v8.csv
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 12726 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 9089 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3207 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 5166 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4518 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1518 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4506 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 4662 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 4879 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 6603 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 5257 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2957 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3400 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1083 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 6297 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3570 populated cells (smoothed)
  [pop-clip] Jadaa Primary Center: 1445 populated cells (smoothed)
  [pop-clip] Maan Hospital: 845 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 1017 populated cells (smoothed)
  Saved: INF_footprint_hsas_v8.geojson
  Columns in saved file: 60
  climate_k preserved: True
  satellite bubbles preserved: True
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running DISTANCE optimization...
================================================================================

============================================================
Running DISTANCE optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running DISTANCE algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=0.50, progress=0.00, overlap=0.20, patient_vol=0.00, climate=0.05, distance=8.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks with distance metrics...
    Built 188 coverage masks with distance metrics
  [3/4] Running greedy selection...
  Target coverage for distance: 90.0%
    Selected 5 so far; 60.4% coverage.
    Selected 10 so far; 73.3% coverage.
    Selected 15 so far; 85.0% coverage.
    Selected 20 so far; 89.8% coverage.
    [STOPPED] Reached 90% coverage with 21 HSAs
  [4/4] Finalizing selection...
  Final: 21 HSAs, 90.9% coverage

Post-processing DISTANCE: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 21/21 facilities (removed 0)

Optimization complete:
  Selected facilities: 21
  Population covered: 9,271,343 (90.9%)
  Anchor upgrade audit: upgraded 10 anchor(s): Zarqa Comprehensive Center -> AL-Zarqa Hospital, Bsaira Comprehensive Center -> Tafilah Governmental Hospital, Petra Comprehensive Center -> Queen Rania Hospital, Hay Al-Hussein Primary Center -> AL-Mafraq Hospital, West Ramtha Primary Center -> AL-Ramtha Hospital, Hawiyyeh Primary Center -> Al-Karak Hospital, Souf Primary Center -> Jarash Hospital, North Madaba Comprehensive Center -> AL-Nadeem Hospital, Al Saro Primary Center -> Al Hussain New Salt Hospital, Aqaba Comprehensive Center -> Khazzan Primary Center
  Saved anchor upgrade audit: INF_distance_anchor_upgrade_audit_v8.csv
  Major orphan audit: no additional anchors required
  Saved major-orphan anchor audit: INF_distance_major_orphan_anchor_audit_v8.csv

================================================================================
DISTANCE OPTIMIZATION COMPLETE
================================================================================
Selected: 21 HSAs
Coverage: 90.9%

Saving results to GeoJSON...
  Satellite bubble geometry: added 35 bubble(s), 299.2 km2 before population clipping
  Saved satellite bubble audit: INF_distance_satellite_bubble_audit_v8.csv
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 12024 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 5848 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8799 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3207 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 3999 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 4879 populated cells (smoothed)
  [pop-clip] Marj AL Hamam CC: 5442 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3400 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4108 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1083 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 949 populated cells (smoothed)
  [pop-clip] AL-Mafraq Hospital: 4842 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 4396 populated cells (smoothed)
  [pop-clip] Mobes Primary Center: 2460 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2835 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 3729 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 2972 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 2087 populated cells (smoothed)
  [pop-clip] Prince Hashem Primary Center: 3570 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1461 populated cells (smoothed)
  [pop-clip] Jadaa Primary Center: 1445 populated cells (smoothed)
  Saved: INF_distance_hsas_v8.geojson
  Columns in saved file: 58
  climate_k preserved: True
  satellite bubbles preserved: True
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully

================================================================================
Running GOVERNORATE_TAU_COVERAGE optimization...
================================================================================

============================================================
Running GOVERNORATE_TAU_COVERAGE optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running GOVERNORATE algorithm (at least one HSA per governorate)...
  Governorate column: shapeName
  Unique governorates: 12
  Assigning adaptive radii to facilities...
    Adaptive radii stats: mean=10.0 km, p10=7.6 km, p90=12.4 km
  Building coverage masks with adaptive radii...
    Phase 1: Ensuring one facility per governorate...
    Phase 1 complete: 12 facilities (one per governorate)
    Phase 2: Continuing greedy selection to reach 90% coverage...
    Selected 15 total; 79.0% of total population covered.
    Selected 20 total; 80.6% of total population covered.
    Selected 25 total; 82.1% of total population covered.
    Selected 30 total; 84.9% of total population covered.
    Selected 35 total; 85.2% of total population covered.
    Selected 40 total; 87.0% of total population covered.
    Selected 45 total; 87.2% of total population covered.
    Selected 50 total; 87.2% of total population covered.
    Selected 55 total; 87.2% of total population covered.
    Selected 60 total; 87.2% of total population covered.
    Selected 65 total; 87.2% of total population covered.
    Selected 70 total; 88.0% of total population covered.
    Selected 75 total; 88.0% of total population covered.
    Selected 80 total; 88.5% of total population covered.
    Selected 85 total; 88.5% of total population covered.
    Selected 90 total; 89.0% of total population covered.
    Selected 95 total; 89.3% of total population covered.
    Selected 100 total; 89.3% of total population covered.
    Selected 105 total; 89.7% of total population covered.
    Selected 110 total; 89.8% of total population covered.
    Selected 115 total; 89.9% of total population covered.
    [ACCEPTED] 119 HSAs, coverage: 90.0%
    Governorates covered: 12/12

Post-processing GOVERNORATE_TAU_COVERAGE: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 35/119 facilities (removed 84)

Optimization complete:
  Selected facilities: 35
  Population covered: 9,105,233 (89.2%)
  Anchor upgrade audit: upgraded 3 anchor(s): Marj AL Hamam CC -> Prince Hamzah Hospital, Eskan Abu-Nsseir Al-Shamel Al-Tadribi -> North Hashmi Comprehensive Center, Qafqafa Primary Center -> Jarash Comprehensive Center
  Saved anchor upgrade audit: INF_governorate_tau_coverage_anchor_upgrade_audit_v8.csv
  Major orphan audit: no additional anchors required
  Saved major-orphan anchor audit: INF_governorate_tau_coverage_major_orphan_anchor_audit_v8.csv

================================================================================
GOVERNORATE_TAU_COVERAGE OPTIMIZATION COMPLETE
================================================================================
Selected: 35 HSAs
Coverage: 89.2%

Saving results to GeoJSON...
  Satellite bubble geometry: added 17 bubble(s), 181.5 km2 before population clipping
  Saved satellite bubble audit: INF_governorate_tau_coverage_satellite_bubble_audit_v8.csv
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 13561 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 6629 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 4049 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 2013 populated cells (smoothed)
  [pop-clip] Maan Hospital: 837 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 2456 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 4711 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 6112 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1314 populated cells (smoothed)
  [pop-clip] Queen Rania Hospital: 889 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 2790 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 2373 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 8148 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 2824 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 2945 populated cells (smoothed)
  [pop-clip] Prince Hamzah Hospital: 12000 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2066 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 782 populated cells (smoothed)
  [pop-clip] North Hashmi Comprehensive Center: 11135 populated cells (smoothed)
  [pop-clip] Al-Razi Comprehensive Center: 2832 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 2412 populated cells (smoothed)
  [pop-clip] South Mazar Comprehensive Center: 1661 populated cells (smoothed)
  [pop-clip] Rehab Comprehensive Center: 1631 populated cells (smoothed)
  [pop-clip] Bsaira Comprehensive Center: 697 populated cells (smoothed)
  [pop-clip] Petra Comprehensive Center: 657 populated cells (smoothed)
  [pop-clip] Balaama Comprehensive Center: 1294 populated cells (smoothed)
  [pop-clip] Moaab Primary Center: 1356 populated cells (smoothed)
  [pop-clip] Muwaqqar Comprehensive Center: 2015 populated cells (smoothed)
  [pop-clip] That Ras Primary Center: 573 populated cells (smoothed)
  [pop-clip] Ader Primary Center: 1391 populated cells (smoothed)
  [pop-clip] Jarash Comprehensive Center: 1817 populated cells (smoothed)
  [pop-clip] Qatraneh Comprehansive Center: 188 populated cells (smoothed)
  [pop-clip] North Badiyah Hospital: 1913 populated cells (smoothed)
  [pop-clip] Shehabyyeh Primary Center: 1228 populated cells (smoothed)
  [pop-clip] Al-Iman Hospital: 1400 populated cells (smoothed)
  Saved: INF_governorate_tau_coverage_hsas_v8.geojson
  Columns in saved file: 51
  climate_k preserved: True
  satellite bubbles preserved: True
  Max service_radius_km: 13.0 km (should be <= 30.0)
  File verified successfully

================================================================================
Running GOVERNORATE_FEWEST optimization...
================================================================================

============================================================
Running GOVERNORATE_FEWEST optimization for INF
============================================================

Assigning radii for 188 INF facilities...
  Computing local density within 10.0km radius...
    Density range: 9.9 - 9531.5 people/km²
  Classification (density-based only):
    Urban (density > 1500.0): 78 facilities
    Rural: 110 facilities
  Applied patient volume scaling:
    Volume range: 2 - 3286 patients
    Radius multiplier range: 0.80x - 1.20x
  Applied INF network multiplier: 1.0x
  Final radius stats: mean=12.3 km, p10=8.2 km, p90=15.2 km
  Facilities CRS: EPSG:4326
  Using FULL Jordan bounds (not facility-cropped): [34.5, 29.0, 39.5, 33.5]
  Raster CRS: EPSG:4326
  Reprojected bounds (raster CRS): (34.5, 29.0, 39.5, 33.5)
  Dataset bounds (raster CRS): (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  Intersection bounds: (34.957083208, 29.186250085, 39.302083191, 33.367916735)
  FULL Jordan raster sum: 10,203,129
  Full raster shape: (1254, 1303), transform: | 0.00, 0.00, 34.96|
| 0.00,-0.00, 33.37|
| 0.00, 0.00, 1.00|

Population statistics:
  Total population: 10,203,129
  Target coverage (90%): 9,182,816

Running GOVERNORATE_FEWEST algorithm (1 per governorate + FEWEST optimization)...
  Governorate column: shapeName
  Unique governorates: 12
  Step 1: Pre-selecting highest volume facility per governorate...
    Amman: Al-Basheer Hospital (3286 patients)
    Karak: Al-Karak Hospital (656 patients)
    Balqa: AL-Shuneh Hospital (1663 patients)
    Ajloun: Al-Iman Hospital (102 patients)
    Irbid: Princess Rahma Hospital (2880 patients)
    Madaba: AL-Nadeem Hospital (1450 patients)
    Mafraq: Al-Mafraq Gynecology and Pediatrics Hospital (669 patients)
    Jerash: Jarash Hospital (849 patients)
    Zarqa: AL-Zarqa Hospital (1050 patients)
    Aqaba: Khazzan Primary Center (899 patients)
    Tafilah: Tafilah Governmental Hospital (564 patients)
    Ma'an: Maan Hospital (1480 patients)
  Pre-selected 12 facilities (1 per governorate)

  Step 2: Running FEWEST optimization to reach 95% national coverage...

Running FEWEST algorithm (unified implementation, adaptive radii)...
  TAU_COVERAGE=0.9, target=90%
  Mode weights: coverage=15.00, progress=0.00, overlap=0.10, patient_vol=0.00, climate=0.00, distance=0.00
  [1/4] Using pre-assigned initial radii as service radii...
    Radii assigned: 8.1 - 19.4 km
    Mean radius: 12.3 km
  [2/4] Building per-facility coverage masks...
    Built 188 coverage masks
  [3/4] Running greedy selection...
  Initializing with 12 pre-selected facilities...
  Target coverage for fewest: 90.0%
    Selected 15 so far; 85.6% coverage.
    [STOPPED] Reached 90% coverage with 18 HSAs
  [4/4] Finalizing selection...
  Final: 18 HSAs, 90.3% coverage

  GOVERNORATE_FEWEST complete: 18 HSAs
  Governorates represented: 12/12

Post-processing GOVERNORATE_FEWEST: Removing overlapping HSAs...
  Removing HSAs with >80% overlap with larger anchors...
  Kept 18/18 facilities (removed 0)

Optimization complete:
  Selected facilities: 18
  Population covered: 9,214,720 (90.3%)
  Anchor upgrade audit: upgraded 1 anchor(s): West Thhaibeh Primary Center -> Dr. Jamel Al-Totanji Hospital
  Saved anchor upgrade audit: INF_governorate_fewest_anchor_upgrade_audit_v8.csv
  Major orphan audit: no additional anchors required
  Saved major-orphan anchor audit: INF_governorate_fewest_major_orphan_anchor_audit_v8.csv

================================================================================
GOVERNORATE_FEWEST OPTIMIZATION COMPLETE
================================================================================
Selected: 18 HSAs
Coverage: 90.3%

Saving results to GeoJSON...
  Satellite bubble geometry: added 28 bubble(s), 499.0 km2 before population clipping
  Saved satellite bubble audit: INF_governorate_fewest_satellite_bubble_audit_v8.csv
  Clipping HSAs to populated WorldPop cells...
  [pop-clip] Al-Basheer Hospital: 12726 populated cells (smoothed)
  [pop-clip] Princess Rahma Hospital: 5848 populated cells (smoothed)
  [pop-clip] Princess Raya Hospital: 8799 populated cells (smoothed)
  [pop-clip] AL-Shuneh Hospital: 3207 populated cells (smoothed)
  [pop-clip] Maan Hospital: 862 populated cells (smoothed)
  [pop-clip] AL-Nadeem Hospital: 5166 populated cells (smoothed)
  [pop-clip] Al Hussain New Salt Hospital: 8437 populated cells (smoothed)
  [pop-clip] AL-Zarqa Hospital: 4518 populated cells (smoothed)
  [pop-clip] Khazzan Primary Center: 1518 populated cells (smoothed)
  [pop-clip] Jarash Hospital: 4506 populated cells (smoothed)
  [pop-clip] Al-Yarmouk Hospital: 3999 populated cells (smoothed)
  [pop-clip] AL-Ramtha Hospital: 5292 populated cells (smoothed)
  [pop-clip] Al-Mafraq Gynecology and Pediatrics Hospital: 5257 populated cells (smoothed)
  [pop-clip] Al-Karak Hospital: 2994 populated cells (smoothed)
  [pop-clip] Tafilah Governmental Hospital: 1093 populated cells (smoothed)
  [pop-clip] Mabroukeh Primary Center: 3400 populated cells (smoothed)
  [pop-clip] Dr. Jamel Al-Totanji Hospital: 11646 populated cells (smoothed)
  [pop-clip] Al-Iman Hospital: 3520 populated cells (smoothed)
  Saved: INF_governorate_fewest_hsas_v8.geojson
  Columns in saved file: 60
  climate_k preserved: True
  satellite bubbles preserved: True
  Max service_radius_km: 19.4 km (should be <= 30.0)
  File verified successfully


================================================================================
ALL OPTIMIZATIONS COMPLETE
================================================================================
  FEWEST                    :  17 HSAs, 90.2% coverage
  FOOTPRINT                 :  19 HSAs, 90.3% coverage
  DISTANCE                  :  21 HSAs, 90.9% coverage
  GOVERNORATE_TAU_COVERAGE  :  35 HSAs, 89.2% coverage
  GOVERNORATE_FEWEST        :  18 HSAs, 90.3% coverage


ALL ALGORITHM VARIANTS COMPLETE
Output files written to: out
  v6  distance                      :  21 HSAs, 90.9% coverage
  v6  fewest                        :  15 HSAs, 90.2% coverage
  v6  footprint                     :  17 HSAs, 90.3% coverage
  v6  governorate_fewest            :  18 HSAs, 90.3% coverage
  v6  governorate_tau_coverage      :  35 HSAs, 89.2% coverage
  v7  distance                      :  21 HSAs, 90.9% coverage
  v7  fewest                        :  17 HSAs, 90.2% coverage
  v7  footprint                     :  19 HSAs, 90.3% coverage
  v7  governorate_fewest            :  18 HSAs, 90.3% coverage
  v7  governorate_tau_coverage      :  35 HSAs, 89.2% coverage
  v8  distance                      :  21 HSAs, 90.9% coverage
  v8  fewest                        :  17 HSAs, 90.2% coverage
  v8  footprint                     :  19 HSAs, 90.3% coverage
  v8  governorate_fewest            :  18 HSAs, 90.3% coverage
  v8  governorate_tau_coverage      :  35 HSAs, 89.2% coverage
```

### Cell 8

```text


################################################################################
# ANALYZING MODE: FEWEST
################################################################################


================================================================================
FEWEST MODE - ALL SELECTED FACILITIES
================================================================================
Number of HSAs: 17
Coverage: 90.22%

Rank Facility                                       Volume       Score Radius_km
--------------------------------------------------------------------------------
1    Al-Basheer Hospital                              3286    4.20e+01      12.0
2    Princess Raya Hospital                           2282    1.54e+01      19.4
3    AL-Zarqa Hospital                                1050    1.05e+01       9.3
4    Al Hussain New Salt Hospital                     1134    8.46e+00      16.9
5    AL-Ramtha Hospital                                673    5.43e+00      15.9
6    Jarash Hospital                                   849    5.28e+00      16.3
7    Al-Mafraq Gynecology and Pediatrics Hospital      669    3.25e+00      15.9
8    Al-Karak Hospital                                 656    2.85e+00      15.8
9    Mabroukeh Primary Center                          443    2.39e+00      15.4
10   Prince Hashem Primary Center                       75    1.78e+00      14.6
11   Al-Yarmouk Hospital                               806    1.33e+00      16.2
12   AL-Nadeem Hospital                               1450         nan      15.2
13   Tafilah Governmental Hospital                     564         nan      15.1
14   Dr. Jamel Al-Totanji Hospital                     745         nan      14.6
15   Khazzan Primary Center                            899         nan      14.5
16   Maan Hospital                                    1480         nan      15.4
17   Queen Rania Hospital                              872         nan      15.4

Volume Statistics:
  Min: 75
  Median: 849
  Max: 3286
  Total: 17933
```

```text
<Figure size 1400x500 with 2 Axes>
```

```text

================================================================================
FEWEST - VOLUME QUARTILES
================================================================================
  Minimum:                 75
  25th Percentile:        669
  Median (50th):          849
  75th Percentile:       1134
  Maximum:               3286
  Mean:                  1055
  Std Dev:                732

================================================================================
FEWEST - SERVICE RADIUS ANALYSIS
================================================================================
  Minimum radius:     9.3 km
  Median radius:     15.4 km
  Maximum radius:    19.4 km
  Mean radius:       15.2 km
  Unique radii:        15
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text
<Figure size 1000x800 with 2 Axes>
```

```text

================================================================================
FEWEST - COMPOSITE SCORE ANALYSIS
================================================================================
  Score range: nan to nan
  Median score: nan
  Mean score: nan
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text

================================================================================
FEWEST - SELECTION ORDER ANALYSIS
================================================================================
```

```text
<Figure size 1200x600 with 1 Axes>
```

```text
Score range: nan to nan
Score decay ratio (last/first): nan

================================================================================
FEWEST - VOLUME vs RADIUS CORRELATION
================================================================================
  Correlation coefficient: -0.083
```

```text
<Figure size 1000x600 with 1 Axes>
```

```text

================================================================================
COMPLETED ANALYSIS FOR FEWEST
================================================================================



################################################################################
# ANALYZING MODE: FOOTPRINT
################################################################################


================================================================================
FOOTPRINT MODE - ALL SELECTED FACILITIES
================================================================================
Number of HSAs: 19
Coverage: 90.27%

Rank Facility                                       Volume       Score Radius_km
--------------------------------------------------------------------------------
1    Al-Basheer Hospital                              3286    3.44e+00      12.0
2    Princess Raya Hospital                           2282    2.02e+00      19.4
3    AL-Zarqa Hospital                                1050    1.76e+00       9.3
4    AL-Nadeem Hospital                               1450    1.45e+00      17.6
5    Al-Karak Hospital                                 656    1.35e+00      15.8
6    AL-Shuneh Hospital                               1663    1.32e+00      18.0
7    AL-Ramtha Hospital                                673    8.90e-01      15.9
8    Jarash Hospital                                   849    8.38e-01      16.3
9    Al-Mafraq Gynecology and Pediatrics Hospital      669    7.74e-01      15.9
10   Prince Hashem Primary Center                       75    6.95e-01      14.6
11   Jadaa Primary Center                                5    6.48e-01      14.4
12   Khazzan Primary Center                            899    6.04e-01      16.4
13   Mabroukeh Primary Center                          443    5.27e-01      15.4
14   Dr. Jamel Al-Totanji Hospital                     745    4.76e-01       8.9
15   Al-Yarmouk Hospital                               806    4.71e-01      16.2
16   Tafilah Governmental Hospital                     564         nan      15.1
17   Al Hussain New Salt Hospital                     1134         nan      14.7
18   Maan Hospital                                    1480         nan      15.8
19   Queen Rania Hospital                              872         nan      15.8

Volume Statistics:
  Min: 5
  Median: 849
  Max: 3286
  Total: 19601
```

```text
<Figure size 1400x500 with 2 Axes>
```

```text

================================================================================
FOOTPRINT - VOLUME QUARTILES
================================================================================
  Minimum:                  5
  25th Percentile:        662
  Median (50th):          849
  75th Percentile:       1292
  Maximum:               3286
  Mean:                  1032
  Std Dev:                746

================================================================================
FOOTPRINT - SERVICE RADIUS ANALYSIS
================================================================================
  Minimum radius:     8.9 km
  Median radius:     15.8 km
  Maximum radius:    19.4 km
  Mean radius:       15.1 km
  Unique radii:        17
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text
<Figure size 1000x800 with 2 Axes>
```

```text

================================================================================
FOOTPRINT - COMPOSITE SCORE ANALYSIS
================================================================================
  Score range: nan to nan
  Median score: nan
  Mean score: nan
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text

================================================================================
FOOTPRINT - SELECTION ORDER ANALYSIS
================================================================================
```

```text
<Figure size 1200x600 with 1 Axes>
```

```text
Score range: nan to nan
Score decay ratio (last/first): nan

================================================================================
FOOTPRINT - VOLUME vs RADIUS CORRELATION
================================================================================
  Correlation coefficient: 0.076
```

```text
<Figure size 1000x600 with 1 Axes>
```

```text

================================================================================
COMPLETED ANALYSIS FOR FOOTPRINT
================================================================================



################################################################################
# ANALYZING MODE: DISTANCE
################################################################################


================================================================================
DISTANCE MODE - ALL SELECTED FACILITIES
================================================================================
Number of HSAs: 21
Coverage: 90.87%

Rank Facility                                       Volume       Score Radius_km
--------------------------------------------------------------------------------
1    Al-Basheer Hospital                              3286    7.78e-01      12.0
2    Princess Rahma Hospital                          2880    2.56e-01      11.5
3    AL-Shuneh Hospital                               1663    6.96e-02      18.0
4    Mobes Primary Center                              155    5.74e-02       8.2
5    Princess Raya Hospital                           2282    5.64e-02      19.4
6    Mabroukeh Primary Center                          443    4.88e-02      15.4
7    Dr. Jamel Al-Totanji Hospital                     745    4.50e-02       8.9
8    Marj AL Hamam CC                                  659    3.89e-02       8.8
9    Jadaa Primary Center                                5    3.84e-02      14.4
10   Prince Hashem Primary Center                       75    3.40e-02      14.6
11   Al-Yarmouk Hospital                               806    2.38e-02      16.2
12   AL-Zarqa Hospital                                1050         nan       8.4
13   Tafilah Governmental Hospital                     564         nan      15.1
14   Queen Rania Hospital                              872         nan      15.1
15   AL-Mafraq Hospital                                473         nan      14.8
16   AL-Ramtha Hospital                                673         nan      14.8
17   Al-Karak Hospital                                 656         nan      14.7
18   Jarash Hospital                                   849         nan      14.7
19   AL-Nadeem Hospital                               1450         nan      14.6
20   Al Hussain New Salt Hospital                     1134         nan       8.1
21   Khazzan Primary Center                            899         nan      14.5

Volume Statistics:
  Min: 5
  Median: 806
  Max: 3286
  Total: 21619
```

```text
<Figure size 1400x500 with 2 Axes>
```

```text

================================================================================
DISTANCE - VOLUME QUARTILES
================================================================================
  Minimum:                  5
  25th Percentile:        564
  Median (50th):          806
  75th Percentile:       1134
  Maximum:               3286
  Mean:                  1029
  Std Dev:                842

================================================================================
DISTANCE - SERVICE RADIUS ANALYSIS
================================================================================
  Minimum radius:     8.1 km
  Median radius:     14.6 km
  Maximum radius:    19.4 km
  Mean radius:       13.4 km
  Unique radii:        21
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text
<Figure size 1000x800 with 2 Axes>
```

```text

================================================================================
DISTANCE - COMPOSITE SCORE ANALYSIS
================================================================================
  Score range: nan to nan
  Median score: nan
  Mean score: nan
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text

================================================================================
DISTANCE - SELECTION ORDER ANALYSIS
================================================================================
```

```text
<Figure size 1200x600 with 1 Axes>
```

```text
Score range: nan to nan
Score decay ratio (last/first): nan

================================================================================
DISTANCE - VOLUME vs RADIUS CORRELATION
================================================================================
  Correlation coefficient: 0.072
```

```text
<Figure size 1000x600 with 1 Axes>
```

```text

================================================================================
COMPLETED ANALYSIS FOR DISTANCE
================================================================================



################################################################################
# ANALYZING MODE: GOVERNORATE_TAU_COVERAGE
################################################################################


================================================================================
GOVERNORATE_TAU_COVERAGE MODE - ALL SELECTED FACILITIES
================================================================================
Number of HSAs: 35
Coverage: 89.24%

Rank Facility                                       Volume       Score Radius_km
--------------------------------------------------------------------------------
1    Al-Basheer Hospital                              3286    3.17e+07      13.0
2    Princess Rahma Hospital                          2880    2.73e+07      13.0
3    Princess Raya Hospital                           2282    2.34e+07      12.9
4    AL-Shuneh Hospital                               1663    1.69e+07      12.9
5    AL-Nadeem Hospital                               1450    1.46e+07      12.8
6    Maan Hospital                                    1480    1.41e+07      12.9
7    Al-Yarmouk Hospital                               806    8.26e+06      12.4
8    Dr. Jamel Al-Totanji Hospital                     745    7.68e+06      12.4
9    AL-Ramtha Hospital                                673    7.58e+06      12.2
10   AL-Zarqa Hospital                                1050    7.19e+06      12.7
11   Al-Mafraq Gynecology and Pediatrics Hospital      669    6.06e+06      12.2
12   Mabroukeh Primary Center                          443    5.07e+06      11.6
13   Al Hussain New Salt Hospital                     1134    4.67e+06      12.8
14   Al-Razi Comprehensive Center                      490    4.47e+06      11.7
15   South Mazar Comprehensive Center                  334    3.13e+06      10.8
16   Rehab Comprehensive Center                        324    3.10e+06      10.8
17   Bsaira Comprehensive Center                       306    2.60e+06      10.6
18   Al-Karak Hospital                                 656    2.58e+06      12.1
19   Jarash Hospital                                   849    2.26e+06      12.4
20   Khazzan Primary Center                            899    1.94e+06      12.5
21   Petra Comprehensive Center                        302    1.87e+06      10.6
22   Muwaqqar Comprehensive Center                     225    1.82e+06      10.2
23   Moaab Primary Center                              226    1.79e+06      10.2
24   Balaama Comprehensive Center                      255    1.68e+06      10.4
25   Qatraneh Comprehansive Center                     174    1.64e+06       9.6
26   Ader Primary Center                               182    1.46e+06       9.8
27   North Badiyah Hospital                            170    1.43e+06       9.6
28   That Ras Primary Center                           211    1.37e+06      10.1
29   Al-Iman Hospital                                  102    1.32e+06       8.4
30   Shehabyyeh Primary Center                         157    1.17e+06       9.4
31   Tafilah Governmental Hospital                     564    5.91e+05      11.9
32   Queen Rania Hospital                              872    4.30e+05      12.5
33   Prince Hamzah Hospital                           1014         nan      12.2
34   North Hashmi Comprehensive Center                1113         nan      11.8
35   Jarash Comprehensive Center                       397         nan       9.6

Volume Statistics:
  Min: 102
  Median: 656
  Max: 3286
  Total: 28383
```

```text
<Figure size 1400x500 with 2 Axes>
```

```text

================================================================================
GOVERNORATE_TAU_COVERAGE - VOLUME QUARTILES
================================================================================
  Minimum:                102
  25th Percentile:        278
  Median (50th):          656
  75th Percentile:       1032
  Maximum:               3286
  Mean:                   811
  Std Dev:                746

================================================================================
GOVERNORATE_TAU_COVERAGE - SERVICE RADIUS ANALYSIS
================================================================================
  Minimum radius:     8.4 km
  Median radius:     11.9 km
  Maximum radius:    13.0 km
  Mean radius:       11.5 km
  Unique radii:        35
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text
<Figure size 1000x800 with 2 Axes>
```

```text

================================================================================
GOVERNORATE_TAU_COVERAGE - COMPOSITE SCORE ANALYSIS
================================================================================
  Score range: nan to nan
  Median score: nan
  Mean score: nan
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text

================================================================================
GOVERNORATE_TAU_COVERAGE - SELECTION ORDER ANALYSIS
================================================================================
```

```text
<Figure size 1200x600 with 1 Axes>
```

```text
Score range: nan to nan
Score decay ratio (last/first): nan

================================================================================
GOVERNORATE_TAU_COVERAGE - VOLUME vs RADIUS CORRELATION
================================================================================
  Correlation coefficient: 0.735
```

```text
<Figure size 1000x600 with 1 Axes>
```

```text

================================================================================
COMPLETED ANALYSIS FOR GOVERNORATE_TAU_COVERAGE
================================================================================



################################################################################
# ANALYZING MODE: GOVERNORATE_FEWEST
################################################################################


================================================================================
GOVERNORATE_FEWEST MODE - ALL SELECTED FACILITIES
================================================================================
Number of HSAs: 18
Coverage: 90.31%

Rank Facility                                       Volume       Score Radius_km
--------------------------------------------------------------------------------
1    Al Hussain New Salt Hospital                     1134    6.95e+00      16.9
2    Princess Raya Hospital                           2282    4.22e+00      19.4
3    AL-Ramtha Hospital                                673    3.33e+00      15.9
4    Mabroukeh Primary Center                          443    2.39e+00      15.4
5    Al-Yarmouk Hospital                               806    1.22e+00      16.2
6    Al-Basheer Hospital                              3286    0.00e+00      12.0
7    Tafilah Governmental Hospital                     564    0.00e+00      15.6
8    Al-Karak Hospital                                 656    0.00e+00      15.8
9    Al-Mafraq Gynecology and Pediatrics Hospital      669    0.00e+00      15.9
10   Khazzan Primary Center                            899    0.00e+00      16.4
11   Jarash Hospital                                   849    0.00e+00      16.3
12   Princess Rahma Hospital                          2880    0.00e+00      11.5
13   AL-Zarqa Hospital                                1050    0.00e+00       9.3
14   AL-Nadeem Hospital                               1450    0.00e+00      17.6
15   Maan Hospital                                    1480    0.00e+00      17.6
16   AL-Shuneh Hospital                               1663    0.00e+00      18.0
17   Al-Iman Hospital                                  102    0.00e+00      14.6
18   Dr. Jamel Al-Totanji Hospital                     745         nan      14.6

Volume Statistics:
  Min: 102
  Median: 874
  Max: 3286
  Total: 21631
```

```text
<Figure size 1400x500 with 2 Axes>
```

```text

================================================================================
GOVERNORATE_FEWEST - VOLUME QUARTILES
================================================================================
  Minimum:                102
  25th Percentile:        670
  Median (50th):          874
  75th Percentile:       1472
  Maximum:               3286
  Mean:                  1202
  Std Dev:                828

================================================================================
GOVERNORATE_FEWEST - SERVICE RADIUS ANALYSIS
================================================================================
  Minimum radius:     9.3 km
  Median radius:     15.9 km
  Maximum radius:    19.4 km
  Mean radius:       15.5 km
  Unique radii:        18
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text
<Figure size 1000x800 with 2 Axes>
```

```text

================================================================================
GOVERNORATE_FEWEST - COMPOSITE SCORE ANALYSIS
================================================================================
  Score range: nan to nan
  Median score: nan
  Mean score: nan
```

```text
<Figure size 1000x500 with 1 Axes>
```

```text

================================================================================
GOVERNORATE_FEWEST - SELECTION ORDER ANALYSIS
================================================================================
```

```text
<Figure size 1200x600 with 1 Axes>
```

```text
Score range: nan to nan
Score decay ratio (last/first): nan

================================================================================
GOVERNORATE_FEWEST - VOLUME vs RADIUS CORRELATION
================================================================================
  Correlation coefficient: -0.187
```

```text
<Figure size 1000x600 with 1 Axes>
```

```text

================================================================================
COMPLETED ANALYSIS FOR GOVERNORATE_FEWEST
================================================================================


################################################################################
# ALL MODES ANALYZED
################################################################################
```

### Cell 9

```text
                       mode            min        median          mean  \
2                  distance       0.023838  4.878572e-02  1.314863e-01   
0                    fewest       1.326396  5.284767e+00  8.966012e+00   
1                 footprint       0.470696  8.380298e-01  1.150446e+00   
4        governorate_fewest       0.000000  0.000000e+00  1.065114e+00   
3  governorate_tau_coverage  430276.382702  2.847531e+06  6.597635e+06   

            max  mean_norm  median_norm  
2  7.783983e-01   0.142663          NaN  
0  4.202700e+01   0.187703          NaN  
1  3.441440e+00   0.228815          NaN  
4  6.950814e+00   0.153236          NaN  
3  3.173775e+07   0.196993          NaN
```

```text
Normalized scores added per mode: composite_score_norm (0-1) and composite_score_z (z-score).
```

### Cell 10

```text

================================================================================
FEWEST - DETAILED HSA ANALYSIS (17 HSAs)
================================================================================
                                  HSA_Anchor  Anchor_Patient_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital                   3286                     38             22620    3.530466e+06          12.000000                  5              59.711143        42.026998
                      Princess Raya Hospital                   2282                     12              8996    9.127198e+05          19.400122                  3              12.282810        15.357354
                Al Hussain New Salt Hospital                   1134                     16              6071    9.274983e+05          16.884723                  3              72.016231         8.464826
                           AL-Zarqa Hospital                   1050                     12              5465    1.141328e+06           9.278150                  2              10.498300        10.464660
                             Jarash Hospital                    849                     13              3262    2.573661e+05          16.260256                  2              60.281009         5.284767
                         Al-Yarmouk Hospital                    806                      7              2187    5.045873e+05          16.166038                  2              20.840294         1.326396
                          AL-Ramtha Hospital                    673                     17              8250    7.755750e+05          15.874620                  6              67.677834         5.430187
Al-Mafraq Gynecology and Pediatrics Hospital                    669                     10              2740    1.622853e+05          15.865855                  4              71.576811         3.253618
                           Al-Karak Hospital                    656                     20              2997    1.375721e+05          15.837371                  7             132.722571         2.851138
                   Mabroukeh Primary Center                     443                      2               647    1.630721e+05          15.370663                  0               0.000000         2.385954
                          AL-Nadeem Hospital                   1450                      6              1671    1.577938e+05          15.215094                  3              51.524984              NaN
               Tafilah Governmental Hospital                    564                      3              1218    3.627707e+04          15.070481                  1              12.681548              NaN
               Dr. Jamel Al-Totanji Hospital                    745                     36             19105    1.908418e+06          14.566525                  2              53.737297              NaN
               Prince Hashem Primary Center                      75                      4               700    1.588297e+05          14.564334                  0               0.000000         1.780236
                      Khazzan Primary Center                    899                      4               983    6.873602e+04          14.478880                  0               0.000000              NaN
                               Maan Hospital                   1480                      2              1678    2.094498e+04          15.370663                  0               0.000000              NaN
                        Queen Rania Hospital                    872                      1               302    2.456779e+04          15.370663                  0               0.000000              NaN

Summary Statistics for FEWEST:
  Total HSAs: 17
  Avg facilities per HSA: 11.9
  Total facilities covered: 203
  Avg HSA volume: 5,229
  Total HSA volume: 88,892
  Satellite bubbles: 40

================================================================================
FOOTPRINT - DETAILED HSA ANALYSIS (19 HSAs)
================================================================================
                                  HSA_Anchor  Anchor_Patient_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital                   3286                     38             22620    3.530466e+06          12.000000                  5              59.711143         3.441440
                      Princess Raya Hospital                   2282                     12              8996    9.127198e+05          19.400122                  3              12.282810         2.019059
                          AL-Shuneh Hospital                   1663                      3              2016    8.306338e+04          18.043822                  0               0.000000         1.316506
                          AL-Nadeem Hospital                   1450                      8              1968    2.358563e+05          17.577115                  2              29.638981         1.447768
                           AL-Zarqa Hospital                   1050                     12              5465    1.141328e+06           9.278150                  2              10.498300         1.758114
                      Khazzan Primary Center                    899                      4               983    7.132890e+04          16.369811                  0               0.000000         0.604036
                             Jarash Hospital                    849                     13              3262    2.573661e+05          16.260256                  2              60.281009         0.838030
                         Al-Yarmouk Hospital                    806                      7              2187    5.045873e+05          16.166038                  2              20.840294         0.470696
               Dr. Jamel Al-Totanji Hospital                    745                      8              2340    4.687913e+05           8.906878                  3               8.365428         0.475638
                          AL-Ramtha Hospital                    673                     17              8250    7.755750e+05          15.874620                  6              67.677834         0.889605
Al-Mafraq Gynecology and Pediatrics Hospital                    669                     10              2740    1.622853e+05          15.865855                  4              71.576811         0.773525
                           Al-Karak Hospital                    656                     19              2817    1.353127e+05          15.837371                  6             122.109570         1.352061
                   Mabroukeh Primary Center                     443                      2               647    1.630721e+05          15.370663                  0               0.000000         0.527176
               Tafilah Governmental Hospital                    564                      3              1218    3.627707e+04          15.070481                  1              12.681548              NaN
                Al Hussain New Salt Hospital                   1134                     12              4405    6.644209e+05          14.682654                  2              31.101625              NaN
               Prince Hashem Primary Center                      75                      4               700    1.588297e+05          14.564334                  0               0.000000         0.694946
                        Jadaa Primary Center                      5                      9               112    2.457504e+04          14.410956                  4              55.067882         0.648098
                               Maan Hospital                   1480                      2              1678    2.049536e+04          15.837371                  0               0.000000              NaN
                        Queen Rania Hospital                    872                      1               302    2.447545e+04          15.837371                  0               0.000000              NaN

Summary Statistics for FOOTPRINT:
  Total HSAs: 19
  Avg facilities per HSA: 9.7
  Total facilities covered: 184
  Avg HSA volume: 3,827
  Total HSA volume: 72,706
  Satellite bubbles: 42

================================================================================
DISTANCE - DETAILED HSA ANALYSIS (21 HSAs)
================================================================================
                   HSA_Anchor  Anchor_Patient_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
          Al-Basheer Hospital                   3286                     38             22620    3.442779e+06          12.000000                  1               1.906573         0.778398
      Princess Rahma Hospital                   2880                     12              6851    7.701532e+05          11.505782                  0               0.000000         0.255546
       Princess Raya Hospital                   2282                     11              8875    8.573211e+05          19.400122                  0               0.000000         0.056427
           AL-Shuneh Hospital                   1663                      3              2016    8.306338e+04          18.043822                  0               0.000000         0.069602
          Al-Yarmouk Hospital                    806                      3               429    3.497387e+05          16.166038                  0               0.000000         0.023838
Dr. Jamel Al-Totanji Hospital                    745                      8              2340    4.687913e+05           8.906878                  3               8.365428         0.044999
             Marj AL Hamam CC                    659                     11              5130    1.083475e+06           8.802191                  2               9.238754         0.038897
    Mabroukeh Primary Center                     443                      2               647    1.630721e+05          15.370663                  0               0.000000         0.048786
            AL-Zarqa Hospital                   1050                     12              5465    1.063092e+06           8.377358                  6              17.383153              NaN
Tafilah Governmental Hospital                    564                      3              1218    3.627707e+04          15.070481                  1              12.681548              NaN
         Queen Rania Hospital                    872                      1               302    2.376029e+04          15.061716                  0               0.000000              NaN
           AL-Mafraq Hospital                    473                     10              2740    1.593541e+05          14.836032                  2              23.408169              NaN
           AL-Ramtha Hospital                    673                      8              1995    4.285744e+05          14.807547                  0               0.000000              NaN
         Mobes Primary Center                    155                      6              1344    3.074420e+05           8.188679                  2              10.006359         0.057422
            Al-Karak Hospital                    656                     17              2802    1.331294e+05          14.724285                  8             102.346873              NaN
              Jarash Hospital                    849                      9              2744    2.104026e+05          14.669507                  1              21.118896              NaN
           AL-Nadeem Hospital                   1450                      6              1671    1.483721e+05          14.645405                  2              23.168038              NaN
 Al Hussain New Salt Hospital                   1134                      6              2335    1.405771e+05           8.125380                  3              14.545675              NaN
Prince Hashem Primary Center                      75                      4               700    1.588297e+05          14.564334                  0               0.000000         0.034050
       Khazzan Primary Center                    899                      4               983    6.873602e+04          14.478880                  0               0.000000              NaN
         Jadaa Primary Center                      5                      9               112    2.457504e+04          14.410956                  4              55.067882         0.038385

Summary Statistics for DISTANCE:
  Total HSAs: 21
  Avg facilities per HSA: 8.7
  Total facilities covered: 183
  Avg HSA volume: 3,491
  Total HSA volume: 73,319
  Satellite bubbles: 35

================================================================================
GOVERNORATE_TAU_COVERAGE - DETAILED HSA ANALYSIS (35 HSAs)
================================================================================
                                  HSA_Anchor  Anchor_Patient_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital                   3286                     43             25551    3.700702e+06          13.000000                  1              18.488720     3.173775e+07
                     Princess Rahma Hospital                   2880                     12              6851    8.228028e+05          12.968085                  0               0.000000     2.729122e+07
                      Princess Raya Hospital                   2282                      2              2740    3.130413e+05          12.936170                  0               0.000000     2.335610e+07
                          AL-Shuneh Hospital                   1663                      2              1873    4.088302e+04          12.904255                  0               0.000000     1.694168e+07
                               Maan Hospital                   1480                      2              1678    2.103659e+04          12.872340                  0               0.000000     1.411758e+07
                          AL-Nadeem Hospital                   1450                      6              1671    1.397206e+05          12.840426                  2              35.454846     1.455345e+07
                Al Hussain New Salt Hospital                   1134                      8              3049    4.643302e+05          12.776596                  1               9.840293     4.665552e+06
                           AL-Zarqa Hospital                   1050                     13              5640    1.479482e+06          12.664894                  0               0.000000     7.191833e+06
                      Khazzan Primary Center                    899                      4               983    6.599352e+04          12.489362                  0               0.000000     1.936694e+06
                        Queen Rania Hospital                    872                      1               302    2.420879e+04          12.457447                  0               0.000000     4.302764e+05
                             Jarash Hospital                    849                      7              2600    1.720863e+05          12.425532                  3              32.107022     2.257201e+06
                         Al-Yarmouk Hospital                    806                      0                 0    1.356528e+05          12.393617                  0               0.000000     8.255382e+06
               Dr. Jamel Al-Totanji Hospital                    745                     23             10134    1.165403e+06          12.361702                  0               0.000000     7.676044e+06
                          AL-Ramtha Hospital                    673                      7              1657    2.146582e+05          12.234043                  0               0.000000     7.582652e+06
Al-Mafraq Gynecology and Pediatrics Hospital                    669                      6              1933    1.076867e+05          12.202128                  1               2.311745     6.059553e+06
                      Prince Hamzah Hospital                   1014                     38             23148    3.527398e+06          12.170213                  2              27.410955              NaN
                           Al-Karak Hospital                    656                     14              2662    1.105617e+05          12.106383                  1               7.119668     2.576277e+06
               Tafilah Governmental Hospital                    564                      3              1218    3.207673e+04          11.946809                  0               0.000000     5.910240e+05
           North Hashmi Comprehensive Center                   1113                     38             23012    3.403862e+06          11.819149                  0               0.000000              NaN
                Al-Razi Comprehensive Center                    490                      8              2496    1.772650e+05          11.723404                  0               0.000000     4.465316e+06
                   Mabroukeh Primary Center                     443                      2               647    1.086245e+05          11.563830                  0               0.000000     5.070601e+06
            South Mazar Comprehensive Center                    334                     10              2027    8.179848e+04          10.797872                  0               0.000000     3.132161e+06
                  Rehab Comprehensive Center                    324                      5              1140    4.956217e+04          10.765957                  0               0.000000     3.097713e+06
                 Bsaira Comprehensive Center                    306                      1               306    1.840320e+04          10.606383                  0               0.000000     2.597349e+06
                  Petra Comprehensive Center                    302                      1               302    2.319512e+04          10.574468                  0               0.000000     1.866841e+06
                Balaama Comprehensive Center                    255                      2               579    2.903147e+04          10.446809                  0               0.000000     1.680749e+06
                        Moaab Primary Center                    226                      8              1322    6.940902e+04          10.223404                  0               0.000000     1.789103e+06
               Muwaqqar Comprehensive Center                    225                      3               415    4.747200e+04          10.191489                  0               0.000000     1.816246e+06
                    That Ras  Primary Center                    211                      3               410    1.946708e+04          10.127660                  1               8.750613     1.372521e+06
                         Ader Primary Center                    182                      9              1579    5.986070e+04           9.776596                  2              20.247801     1.461138e+06
                 Jarash Comprehensive Center                    397                      6              2461    1.293219e+05           9.632979                  0               0.000000              NaN
               Qatraneh Comprehansive Center                    174                      0                 0    5.087593e+02           9.585106                  0               0.000000     1.643525e+06
                      North Badiyah Hospital                    170                      5              1399    1.121289e+05           9.553191                  0               0.000000     1.428035e+06
                   Shehabyyeh Primary Center                    157                      9              1684    5.648280e+04           9.425532                  2              12.527818     1.166283e+06
                            Al-Iman Hospital                    102                      3               210    7.705508e+04           8.388298                  1               7.193859     1.316473e+06

Summary Statistics for GOVERNORATE_TAU_COVERAGE:
  Total HSAs: 35
  Avg facilities per HSA: 8.7
  Total facilities covered: 304
  Avg HSA volume: 3,819
  Total HSA volume: 133,679
  Satellite bubbles: 17

================================================================================
GOVERNORATE_FEWEST - DETAILED HSA ANALYSIS (18 HSAs)
================================================================================
                                  HSA_Anchor  Anchor_Patient_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital                   3286                     38             22620    3.530466e+06          12.000000                  5              59.711143         0.000000
                     Princess Rahma Hospital                   2880                     12              6851    7.701532e+05          11.505782                  0               0.000000         0.000000
                      Princess Raya Hospital                   2282                     11              8875    8.573211e+05          19.400122                  0               0.000000         4.219535
                          AL-Shuneh Hospital                   1663                      3              2016    8.306338e+04          18.043822                  0               0.000000         0.000000
                               Maan Hospital                   1480                      2              1678    2.103659e+04          17.642848                  0               0.000000         0.000000
                          AL-Nadeem Hospital                   1450                      8              1968    2.358563e+05          17.577115                  2              29.638981         0.000000
                Al Hussain New Salt Hospital                   1134                     16              6071    9.274983e+05          16.884723                  3              72.016231         6.950814
                           AL-Zarqa Hospital                   1050                     12              5465    1.141328e+06           9.278150                  2              10.498300         0.000000
                      Khazzan Primary Center                    899                      4               983    7.132890e+04          16.369811                  0               0.000000         0.000000
                             Jarash Hospital                    849                     13              3262    2.573661e+05          16.260256                  2              60.281009         0.000000
                         Al-Yarmouk Hospital                    806                      3               429    3.497387e+05          16.166038                  0               0.000000         1.222491
                          AL-Ramtha Hospital                    673                     12              2970    5.479126e+05          15.874620                  0               0.000000         3.328145
Al-Mafraq Gynecology and Pediatrics Hospital                    669                     10              2740    1.622853e+05          15.865855                  4              71.576811         0.000000
                           Al-Karak Hospital                    656                     20              2997    1.375721e+05          15.837371                  7             132.722571         0.000000
               Tafilah Governmental Hospital                    564                      3              1218    3.651823e+04          15.635788                  1               9.643646         0.000000
                   Mabroukeh Primary Center                     443                      2               647    1.630721e+05          15.370663                  0               0.000000         2.385954
               Dr. Jamel Al-Totanji Hospital                    745                     35             19058    1.936208e+06          14.649787                  2              52.933554              NaN
                            Al-Iman Hospital                    102                      7              2012    2.037329e+05          14.623494                  0               0.000000         0.000000

Summary Statistics for GOVERNORATE_FEWEST:
  Total HSAs: 18
  Avg facilities per HSA: 11.7
  Total facilities covered: 211
  Avg HSA volume: 5,103
  Total HSA volume: 91,860
  Satellite bubbles: 28


================================================================================
CROSS-MODE COMPARISON SUMMARY
================================================================================
                    Mode  Num_HSAs  Avg_Facilities_per_HSA  Total_Facilities_Covered  Avg_HSA_Volume  Total_HSA_Volume  Satellite_Bubbles
                  FEWEST        17               11.941176                       203     5228.941176             88892                 40
               FOOTPRINT        19                9.684211                       184     3826.631579             72706                 42
                DISTANCE        21                8.714286                       183     3491.380952             73319                 35
GOVERNORATE_TAU_COVERAGE        35                8.685714                       304     3819.400000            133679                 17
      GOVERNORATE_FEWEST        18               11.722222                       211     5103.333333             91860                 28
```

### Cell 12

```text
Country boundary loaded from: jordan_boundary.gpkg
  CRS: EPSG:4326
```

### Cell 13

```text

============================================================
Creating maps for v6 (5 modes)...
============================================================
Loading base layers...
Loaded base layers (CRS: EPSG:4326)

Creating map for FEWEST HSAs...
  Using population-clipped polygons from INF_fewest_hsas_v6.geojson
Saved: INF_fewest_map_v6.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for FOOTPRINT HSAs...
  Using population-clipped polygons from INF_footprint_hsas_v6.geojson
Saved: INF_footprint_map_v6.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for DISTANCE HSAs...
  Using population-clipped polygons from INF_distance_hsas_v6.geojson
Saved: INF_distance_map_v6.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for GOVERNORATE TAU COVERAGE HSAs...
  Using population-clipped polygons from INF_governorate_tau_coverage_hsas_v6.geojson
Saved: INF_governorate_tau_coverage_map_v6.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for GOVERNORATE FEWEST HSAs...
  Using population-clipped polygons from INF_governorate_fewest_hsas_v6.geojson
Saved: INF_governorate_fewest_map_v6.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

================================================================================
ALL MAPS CREATED SUCCESSFULLY
================================================================================

Saving GeoPackage: INF_fewest_map_v6.gpkg
  hsa_boundaries: population-clipped (INF_fewest_hsas_v6.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_fewest_map_v6.gpkg

Saving GeoPackage: INF_footprint_map_v6.gpkg
  hsa_boundaries: population-clipped (INF_footprint_hsas_v6.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_footprint_map_v6.gpkg

Saving GeoPackage: INF_distance_map_v6.gpkg
  hsa_boundaries: population-clipped (INF_distance_hsas_v6.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_distance_map_v6.gpkg

Saving GeoPackage: INF_governorate_tau_coverage_map_v6.gpkg
  hsa_boundaries: population-clipped (INF_governorate_tau_coverage_hsas_v6.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_governorate_tau_coverage_map_v6.gpkg

Saving GeoPackage: INF_governorate_fewest_map_v6.gpkg
  hsa_boundaries: population-clipped (INF_governorate_fewest_hsas_v6.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_governorate_fewest_map_v6.gpkg

================================================================================
GEOPACKAGES SAVED: 5
================================================================================

============================================================
Creating maps for v7 (5 modes)...
============================================================
Loading base layers...
Loaded base layers (CRS: EPSG:4326)

Creating map for FEWEST HSAs...
  Using population-clipped polygons from INF_fewest_hsas_v7.geojson
Saved: INF_fewest_map_v7.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for FOOTPRINT HSAs...
  Using population-clipped polygons from INF_footprint_hsas_v7.geojson
Saved: INF_footprint_map_v7.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for DISTANCE HSAs...
  Using population-clipped polygons from INF_distance_hsas_v7.geojson
Saved: INF_distance_map_v7.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for GOVERNORATE TAU COVERAGE HSAs...
  Using population-clipped polygons from INF_governorate_tau_coverage_hsas_v7.geojson
Saved: INF_governorate_tau_coverage_map_v7.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for GOVERNORATE FEWEST HSAs...
  Using population-clipped polygons from INF_governorate_fewest_hsas_v7.geojson
Saved: INF_governorate_fewest_map_v7.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

================================================================================
ALL MAPS CREATED SUCCESSFULLY
================================================================================

Saving GeoPackage: INF_fewest_map_v7.gpkg
  hsa_boundaries: population-clipped (INF_fewest_hsas_v7.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_fewest_map_v7.gpkg

Saving GeoPackage: INF_footprint_map_v7.gpkg
  hsa_boundaries: population-clipped (INF_footprint_hsas_v7.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_footprint_map_v7.gpkg

Saving GeoPackage: INF_distance_map_v7.gpkg
  hsa_boundaries: population-clipped (INF_distance_hsas_v7.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_distance_map_v7.gpkg

Saving GeoPackage: INF_governorate_tau_coverage_map_v7.gpkg
  hsa_boundaries: population-clipped (INF_governorate_tau_coverage_hsas_v7.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_governorate_tau_coverage_map_v7.gpkg

Saving GeoPackage: INF_governorate_fewest_map_v7.gpkg
  hsa_boundaries: population-clipped (INF_governorate_fewest_hsas_v7.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_governorate_fewest_map_v7.gpkg

================================================================================
GEOPACKAGES SAVED: 5
================================================================================

============================================================
Creating maps for v8 (5 modes)...
============================================================
Loading base layers...
Loaded base layers (CRS: EPSG:4326)

Creating map for FEWEST HSAs...
  Using population-clipped polygons from INF_fewest_hsas_v8.geojson
Saved: INF_fewest_map_v8.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for FOOTPRINT HSAs...
  Using population-clipped polygons from INF_footprint_hsas_v8.geojson
Saved: INF_footprint_map_v8.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for DISTANCE HSAs...
  Using population-clipped polygons from INF_distance_hsas_v8.geojson
Saved: INF_distance_map_v8.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for GOVERNORATE TAU COVERAGE HSAs...
  Using population-clipped polygons from INF_governorate_tau_coverage_hsas_v8.geojson
Saved: INF_governorate_tau_coverage_map_v8.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

Creating map for GOVERNORATE FEWEST HSAs...
  Using population-clipped polygons from INF_governorate_fewest_hsas_v8.geojson
Saved: INF_governorate_fewest_map_v8.png
```

```text
<Figure size 1600x1200 with 1 Axes>
```

```text

================================================================================
ALL MAPS CREATED SUCCESSFULLY
================================================================================

Saving GeoPackage: INF_fewest_map_v8.gpkg
  hsa_boundaries: population-clipped (INF_fewest_hsas_v8.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_fewest_map_v8.gpkg

Saving GeoPackage: INF_footprint_map_v8.gpkg
  hsa_boundaries: population-clipped (INF_footprint_hsas_v8.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_footprint_map_v8.gpkg

Saving GeoPackage: INF_distance_map_v8.gpkg
  hsa_boundaries: population-clipped (INF_distance_hsas_v8.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_distance_map_v8.gpkg

Saving GeoPackage: INF_governorate_tau_coverage_map_v8.gpkg
  hsa_boundaries: population-clipped (INF_governorate_tau_coverage_hsas_v8.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_governorate_tau_coverage_map_v8.gpkg

Saving GeoPackage: INF_governorate_fewest_map_v8.gpkg
  hsa_boundaries: population-clipped (INF_governorate_fewest_hsas_v8.geojson)
  Layers: hsa_circles, hsa_boundaries, hsa_anchors, all_facilities, country_boundary, governorates
  Saved: out/INF_governorate_fewest_map_v8.gpkg

================================================================================
GEOPACKAGES SAVED: 5
================================================================================

Done — 15 maps and 15 GeoPackages written to out
```

### Cell 15

```text

================================================================================
FEWEST - ALL 17 HSAs
================================================================================
                                  HSA_Anchor  Anchor_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital           3286                     38             22620    3.530466e+06          12.000000                  5              59.711143        42.026998
                      Princess Raya Hospital           2282                     12              8996    9.127198e+05          19.400122                  3              12.282810        15.357354
                Al Hussain New Salt Hospital           1134                     16              6071    9.274983e+05          16.884723                  3              72.016231         8.464826
                           AL-Zarqa Hospital           1050                     12              5465    1.141328e+06           9.278150                  2              10.498300        10.464660
                             Jarash Hospital            849                     13              3262    2.573661e+05          16.260256                  2              60.281009         5.284767
                         Al-Yarmouk Hospital            806                      7              2187    5.045873e+05          16.166038                  2              20.840294         1.326396
                          AL-Ramtha Hospital            673                     17              8250    7.755750e+05          15.874620                  6              67.677834         5.430187
Al-Mafraq Gynecology and Pediatrics Hospital            669                     10              2740    1.622853e+05          15.865855                  4              71.576811         3.253618
                           Al-Karak Hospital            656                     20              2997    1.375721e+05          15.837371                  7             132.722571         2.851138
                   Mabroukeh Primary Center             443                      2               647    1.630721e+05          15.370663                  0               0.000000         2.385954
                          AL-Nadeem Hospital           1450                      6              1671    1.577938e+05          15.215094                  3              51.524984              NaN
               Tafilah Governmental Hospital            564                      3              1218    3.627707e+04          15.070481                  1              12.681548              NaN
               Dr. Jamel Al-Totanji Hospital            745                     36             19105    1.908418e+06          14.566525                  2              53.737297              NaN
               Prince Hashem Primary Center              75                      4               700    1.588297e+05          14.564334                  0               0.000000         1.780236
                      Khazzan Primary Center            899                      4               983    6.873602e+04          14.478880                  0               0.000000              NaN
                               Maan Hospital           1480                      2              1678    2.094498e+04          15.370663                  0               0.000000              NaN
                        Queen Rania Hospital            872                      1               302    2.456779e+04          15.370663                  0               0.000000              NaN

Summary Statistics:
  Total HSAs: 17
  Total facilities across all HSAs: 203
  Total HSA volume: 88,892
  Total population covered: 10,888,038
  Satellite bubbles: 40

================================================================================
FOOTPRINT - ALL 19 HSAs
================================================================================
                                  HSA_Anchor  Anchor_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital           3286                     38             22620    3.530466e+06          12.000000                  5              59.711143         3.441440
                      Princess Raya Hospital           2282                     12              8996    9.127198e+05          19.400122                  3              12.282810         2.019059
                          AL-Shuneh Hospital           1663                      3              2016    8.306338e+04          18.043822                  0               0.000000         1.316506
                          AL-Nadeem Hospital           1450                      8              1968    2.358563e+05          17.577115                  2              29.638981         1.447768
                           AL-Zarqa Hospital           1050                     12              5465    1.141328e+06           9.278150                  2              10.498300         1.758114
                      Khazzan Primary Center            899                      4               983    7.132890e+04          16.369811                  0               0.000000         0.604036
                             Jarash Hospital            849                     13              3262    2.573661e+05          16.260256                  2              60.281009         0.838030
                         Al-Yarmouk Hospital            806                      7              2187    5.045873e+05          16.166038                  2              20.840294         0.470696
               Dr. Jamel Al-Totanji Hospital            745                      8              2340    4.687913e+05           8.906878                  3               8.365428         0.475638
                          AL-Ramtha Hospital            673                     17              8250    7.755750e+05          15.874620                  6              67.677834         0.889605
Al-Mafraq Gynecology and Pediatrics Hospital            669                     10              2740    1.622853e+05          15.865855                  4              71.576811         0.773525
                           Al-Karak Hospital            656                     19              2817    1.353127e+05          15.837371                  6             122.109570         1.352061
                   Mabroukeh Primary Center             443                      2               647    1.630721e+05          15.370663                  0               0.000000         0.527176
               Tafilah Governmental Hospital            564                      3              1218    3.627707e+04          15.070481                  1              12.681548              NaN
                Al Hussain New Salt Hospital           1134                     12              4405    6.644209e+05          14.682654                  2              31.101625              NaN
               Prince Hashem Primary Center              75                      4               700    1.588297e+05          14.564334                  0               0.000000         0.694946
                        Jadaa Primary Center              5                      9               112    2.457504e+04          14.410956                  4              55.067882         0.648098
                               Maan Hospital           1480                      2              1678    2.049536e+04          15.837371                  0               0.000000              NaN
                        Queen Rania Hospital            872                      1               302    2.447545e+04          15.837371                  0               0.000000              NaN

Summary Statistics:
  Total HSAs: 19
  Total facilities across all HSAs: 184
  Total HSA volume: 72,706
  Total population covered: 9,370,826
  Satellite bubbles: 42

================================================================================
DISTANCE - ALL 21 HSAs
================================================================================
                   HSA_Anchor  Anchor_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
          Al-Basheer Hospital           3286                     38             22620    3.442779e+06          12.000000                  1               1.906573         0.778398
      Princess Rahma Hospital           2880                     12              6851    7.701532e+05          11.505782                  0               0.000000         0.255546
       Princess Raya Hospital           2282                     11              8875    8.573211e+05          19.400122                  0               0.000000         0.056427
           AL-Shuneh Hospital           1663                      3              2016    8.306338e+04          18.043822                  0               0.000000         0.069602
          Al-Yarmouk Hospital            806                      3               429    3.497387e+05          16.166038                  0               0.000000         0.023838
Dr. Jamel Al-Totanji Hospital            745                      8              2340    4.687913e+05           8.906878                  3               8.365428         0.044999
             Marj AL Hamam CC            659                     11              5130    1.083475e+06           8.802191                  2               9.238754         0.038897
    Mabroukeh Primary Center             443                      2               647    1.630721e+05          15.370663                  0               0.000000         0.048786
            AL-Zarqa Hospital           1050                     12              5465    1.063092e+06           8.377358                  6              17.383153              NaN
Tafilah Governmental Hospital            564                      3              1218    3.627707e+04          15.070481                  1              12.681548              NaN
         Queen Rania Hospital            872                      1               302    2.376029e+04          15.061716                  0               0.000000              NaN
           AL-Mafraq Hospital            473                     10              2740    1.593541e+05          14.836032                  2              23.408169              NaN
           AL-Ramtha Hospital            673                      8              1995    4.285744e+05          14.807547                  0               0.000000              NaN
         Mobes Primary Center            155                      6              1344    3.074420e+05           8.188679                  2              10.006359         0.057422
            Al-Karak Hospital            656                     17              2802    1.331294e+05          14.724285                  8             102.346873              NaN
              Jarash Hospital            849                      9              2744    2.104026e+05          14.669507                  1              21.118896              NaN
           AL-Nadeem Hospital           1450                      6              1671    1.483721e+05          14.645405                  2              23.168038              NaN
 Al Hussain New Salt Hospital           1134                      6              2335    1.405771e+05           8.125380                  3              14.545675              NaN
Prince Hashem Primary Center              75                      4               700    1.588297e+05          14.564334                  0               0.000000         0.034050
       Khazzan Primary Center            899                      4               983    6.873602e+04          14.478880                  0               0.000000              NaN
         Jadaa Primary Center              5                      9               112    2.457504e+04          14.410956                  4              55.067882         0.038385

Summary Statistics:
  Total HSAs: 21
  Total facilities across all HSAs: 183
  Total HSA volume: 73,319
  Total population covered: 10,121,515
  Satellite bubbles: 35

================================================================================
GOVERNORATE TAU COVERAGE - ALL 35 HSAs
================================================================================
                                  HSA_Anchor  Anchor_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital           3286                     43             25551    3.700702e+06          13.000000                  1              18.488720     3.173775e+07
                     Princess Rahma Hospital           2880                     12              6851    8.228028e+05          12.968085                  0               0.000000     2.729122e+07
                      Princess Raya Hospital           2282                      2              2740    3.130413e+05          12.936170                  0               0.000000     2.335610e+07
                          AL-Shuneh Hospital           1663                      2              1873    4.088302e+04          12.904255                  0               0.000000     1.694168e+07
                               Maan Hospital           1480                      2              1678    2.103659e+04          12.872340                  0               0.000000     1.411758e+07
                          AL-Nadeem Hospital           1450                      6              1671    1.397206e+05          12.840426                  2              35.454846     1.455345e+07
                Al Hussain New Salt Hospital           1134                      8              3049    4.643302e+05          12.776596                  1               9.840293     4.665552e+06
                           AL-Zarqa Hospital           1050                     13              5640    1.479482e+06          12.664894                  0               0.000000     7.191833e+06
                      Khazzan Primary Center            899                      4               983    6.599352e+04          12.489362                  0               0.000000     1.936694e+06
                        Queen Rania Hospital            872                      1               302    2.420879e+04          12.457447                  0               0.000000     4.302764e+05
                             Jarash Hospital            849                      7              2600    1.720863e+05          12.425532                  3              32.107022     2.257201e+06
                         Al-Yarmouk Hospital            806                      0                 0    1.356528e+05          12.393617                  0               0.000000     8.255382e+06
               Dr. Jamel Al-Totanji Hospital            745                     23             10134    1.165403e+06          12.361702                  0               0.000000     7.676044e+06
                          AL-Ramtha Hospital            673                      7              1657    2.146582e+05          12.234043                  0               0.000000     7.582652e+06
Al-Mafraq Gynecology and Pediatrics Hospital            669                      6              1933    1.076867e+05          12.202128                  1               2.311745     6.059553e+06
                      Prince Hamzah Hospital           1014                     38             23148    3.527398e+06          12.170213                  2              27.410955              NaN
                           Al-Karak Hospital            656                     14              2662    1.105617e+05          12.106383                  1               7.119668     2.576277e+06
               Tafilah Governmental Hospital            564                      3              1218    3.207673e+04          11.946809                  0               0.000000     5.910240e+05
           North Hashmi Comprehensive Center           1113                     38             23012    3.403862e+06          11.819149                  0               0.000000              NaN
                Al-Razi Comprehensive Center            490                      8              2496    1.772650e+05          11.723404                  0               0.000000     4.465316e+06
                   Mabroukeh Primary Center             443                      2               647    1.086245e+05          11.563830                  0               0.000000     5.070601e+06
            South Mazar Comprehensive Center            334                     10              2027    8.179848e+04          10.797872                  0               0.000000     3.132161e+06
                  Rehab Comprehensive Center            324                      5              1140    4.956217e+04          10.765957                  0               0.000000     3.097713e+06
                 Bsaira Comprehensive Center            306                      1               306    1.840320e+04          10.606383                  0               0.000000     2.597349e+06
                  Petra Comprehensive Center            302                      1               302    2.319512e+04          10.574468                  0               0.000000     1.866841e+06
                Balaama Comprehensive Center            255                      2               579    2.903147e+04          10.446809                  0               0.000000     1.680749e+06
                        Moaab Primary Center            226                      8              1322    6.940902e+04          10.223404                  0               0.000000     1.789103e+06
               Muwaqqar Comprehensive Center            225                      3               415    4.747200e+04          10.191489                  0               0.000000     1.816246e+06
                    That Ras  Primary Center            211                      3               410    1.946708e+04          10.127660                  1               8.750613     1.372521e+06
                         Ader Primary Center            182                      9              1579    5.986070e+04           9.776596                  2              20.247801     1.461138e+06
                 Jarash Comprehensive Center            397                      6              2461    1.293219e+05           9.632979                  0               0.000000              NaN
               Qatraneh Comprehansive Center            174                      0                 0    5.087593e+02           9.585106                  0               0.000000     1.643525e+06
                      North Badiyah Hospital            170                      5              1399    1.121289e+05           9.553191                  0               0.000000     1.428035e+06
                   Shehabyyeh Primary Center            157                      9              1684    5.648280e+04           9.425532                  2              12.527818     1.166283e+06
                            Al-Iman Hospital            102                      3               210    7.705508e+04           8.388298                  1               7.193859     1.316473e+06

Summary Statistics:
  Total HSAs: 35
  Total facilities across all HSAs: 304
  Total HSA volume: 133,679
  Total population covered: 17,001,172
  Satellite bubbles: 17

================================================================================
GOVERNORATE FEWEST - ALL 18 HSAs
================================================================================
                                  HSA_Anchor  Anchor_Volume  Num_Facilities_in_HSA  Total_HSA_Volume  HSA_Population  Service_Radius_km  Satellite_Bubbles  Bubble_Area_Added_km2  Composite_Score
                         Al-Basheer Hospital           3286                     38             22620    3.530466e+06          12.000000                  5              59.711143         0.000000
                     Princess Rahma Hospital           2880                     12              6851    7.701532e+05          11.505782                  0               0.000000         0.000000
                      Princess Raya Hospital           2282                     11              8875    8.573211e+05          19.400122                  0               0.000000         4.219535
                          AL-Shuneh Hospital           1663                      3              2016    8.306338e+04          18.043822                  0               0.000000         0.000000
                               Maan Hospital           1480                      2              1678    2.103659e+04          17.642848                  0               0.000000         0.000000
                          AL-Nadeem Hospital           1450                      8              1968    2.358563e+05          17.577115                  2              29.638981         0.000000
                Al Hussain New Salt Hospital           1134                     16              6071    9.274983e+05          16.884723                  3              72.016231         6.950814
                           AL-Zarqa Hospital           1050                     12              5465    1.141328e+06           9.278150                  2              10.498300         0.000000
                      Khazzan Primary Center            899                      4               983    7.132890e+04          16.369811                  0               0.000000         0.000000
                             Jarash Hospital            849                     13              3262    2.573661e+05          16.260256                  2              60.281009         0.000000
                         Al-Yarmouk Hospital            806                      3               429    3.497387e+05          16.166038                  0               0.000000         1.222491
                          AL-Ramtha Hospital            673                     12              2970    5.479126e+05          15.874620                  0               0.000000         3.328145
Al-Mafraq Gynecology and Pediatrics Hospital            669                     10              2740    1.622853e+05          15.865855                  4              71.576811         0.000000
                           Al-Karak Hospital            656                     20              2997    1.375721e+05          15.837371                  7             132.722571         0.000000
               Tafilah Governmental Hospital            564                      3              1218    3.651823e+04          15.635788                  1               9.643646         0.000000
                   Mabroukeh Primary Center             443                      2               647    1.630721e+05          15.370663                  0               0.000000         2.385954
               Dr. Jamel Al-Totanji Hospital            745                     35             19058    1.936208e+06          14.649787                  2              52.933554              NaN
                            Al-Iman Hospital            102                      7              2012    2.037329e+05          14.623494                  0               0.000000         0.000000

Summary Statistics:
  Total HSAs: 18
  Total facilities across all HSAs: 211
  Total HSA volume: 91,860
  Total population covered: 11,432,458
  Satellite bubbles: 28

================================================================================
HSA DETAIL TABLES COMPLETE
================================================================================
```

### Cell 19

```text
Saved notebook summary: out/textresults/HSA_v8_FINAL_INF_results.md
```
