# Notebook Results: Population_Allocation_Probabilistic_v2

- Generated: 2026-07-13T10:59:05
- Network: INF
- HSA mode: footprint

## Important Output Files

- `out/INF_footprint_allocation_details_v7.csv`
- `out/pixel_allocations_INF_footprint_v7.csv`
- `out/INF_footprint_facility_hsa_assignments_v7.csv`
- `out/INF_footprint_facility_allocations_probabilistic_v7.csv`
- `out/INF_footprint_hsa_populations_probabilistic_v7.csv`
- `out/textresults/HSA_FINAL_INF_footprint_v7_results.md`
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

### Cell 3

```text
================================================================================
PROBABILISTIC PATIENT ALLOCATION CONFIGURATION
================================================================================
Network: INF
HSA Mode: footprint
Population Raster: jor_ppp_2020_UNadj.tif

Gravity Model Parameters:
  alpha: 0.75
  beta: 1.5
  max_distance_km: 100
  sample_rate: 1

Fallback Guard Parameters:
  fallback_radius_multiplier: 1.5
  fallback_min_distance_km: 30.0
  major_facility_pop_threshold: 25000.0
  major_facility_volume_threshold: None
  major_facility_volume_quantile: 0.8
  require_same_governorate_for_major: True

Allocation Mode: PROBABILISTIC (two-step)
================================================================================
```

### Cell 5

```text
Loaded 19 HSA anchors from INF_footprint_hsas_v8.geojson

HSA Anchor Facilities:
  1. Al-Basheer Hospital (radius: 12.0 km)
  2. Princess Raya Hospital (radius: 19.4 km)
  3. AL-Shuneh Hospital (radius: 18.0 km)
  4. AL-Nadeem Hospital (radius: 17.6 km)
  5. AL-Zarqa Hospital (radius: 9.3 km)
  6. Khazzan Primary Center (radius: 16.4 km)
  7. Jarash Hospital (radius: 16.3 km)
  8. Al-Yarmouk Hospital (radius: 16.2 km)
  9. Dr. Jamel Al-Totanji Hospital (radius: 8.9 km)
  10. AL-Ramtha Hospital (radius: 15.9 km)
  11. Al-Mafraq Gynecology and Pediatrics Hospital (radius: 15.9 km)
  12. Al-Karak Hospital (radius: 15.8 km)
  13. Mabroukeh Primary Center (radius: 15.4 km)
  14. Tafilah Governmental Hospital (radius: 15.1 km)
  15. Al Hussain New Salt Hospital (radius: 14.7 km)
  16. Prince Hashem Primary Center (radius: 14.6 km)
  17. Jadaa Primary Center (radius: 14.4 km)
  18. Maan Hospital (radius: 15.8 km)
  19. Queen Rania Hospital (radius: 15.8 km)
```

### Cell 6

```text

Loaded 188 total facilities
  Facilities with volume > 0: 188
  Total patient volume: 66,876
```

### Cell 8

```text
Initializing PopulationAllocator with ALL facilities...
PopulationAllocator initialized:
  Facilities: 188
  Parameters: alpha=0.75, beta=1.5, max_dist=100km
  Spatial index: KD-Tree built for fast lookups
  Facility lon range: [35.00, 36.31]
  Facility lat range: [29.52, 32.71]

  Allocating to 188 facilities (not just 19 HSA anchors)
```

### Cell 9

```text

Running probabilistic allocation...
  (This allocates each pixel's population to ALL reachable facilities)

Allocating population pixels to facilities (VECTORIZED)...
  Raster size: 5018 x 5214 = 26,163,852 pixels
  Populated sampled pixels: 12,091,883
  Total sampled population: 10,203,140
  Batches: 242 (batch_size=50,000)
    Progress:   1.7% | 200,000 pixels | 0.0% population allocated
    Progress:   3.3% | 400,000 pixels | 0.0% population allocated
    Progress:   5.0% | 600,000 pixels | 0.0% population allocated
    Progress:   6.6% | 800,000 pixels | 0.8% population allocated
    Progress:   8.3% | 1,000,000 pixels | 3.5% population allocated
    Progress:   9.9% | 1,200,000 pixels | 9.9% population allocated
    Progress:  11.6% | 1,400,000 pixels | 14.7% population allocated
    Progress:  13.2% | 1,600,000 pixels | 17.2% population allocated
    Progress:  14.9% | 1,800,000 pixels | 19.2% population allocated
    Progress:  16.5% | 2,000,000 pixels | 21.6% population allocated
    Progress:  18.2% | 2,200,000 pixels | 24.1% population allocated
    Progress:  19.8% | 2,400,000 pixels | 26.3% population allocated
    Progress:  21.5% | 2,600,000 pixels | 27.6% population allocated
    Progress:  23.2% | 2,800,000 pixels | 28.6% population allocated
    Progress:  24.8% | 3,000,000 pixels | 29.8% population allocated
    Progress:  26.5% | 3,200,000 pixels | 31.6% population allocated
    Progress:  28.1% | 3,400,000 pixels | 36.4% population allocated
    Progress:  29.8% | 3,600,000 pixels | 43.5% population allocated
    Progress:  31.4% | 3,800,000 pixels | 55.1% population allocated
    Progress:  33.1% | 4,000,000 pixels | 69.1% population allocated
    Progress:  34.7% | 4,200,000 pixels | 78.9% population allocated
    Progress:  36.4% | 4,400,000 pixels | 84.1% population allocated
    Progress:  38.0% | 4,600,000 pixels | 86.6% population allocated
    Progress:  39.7% | 4,800,000 pixels | 87.6% population allocated
    Progress:  41.4% | 5,000,000 pixels | 89.3% population allocated
    Progress:  43.0% | 5,200,000 pixels | 89.9% population allocated
    Progress:  44.7% | 5,400,000 pixels | 90.2% population allocated
    Progress:  46.3% | 5,600,000 pixels | 90.6% population allocated
    Progress:  48.0% | 5,800,000 pixels | 90.8% population allocated
    Progress:  49.6% | 6,000,000 pixels | 91.3% population allocated
    Progress:  51.3% | 6,200,000 pixels | 91.7% population allocated
    Progress:  52.9% | 6,400,000 pixels | 92.6% population allocated
    Progress:  54.6% | 6,600,000 pixels | 93.6% population allocated
    Progress:  56.2% | 6,800,000 pixels | 94.3% population allocated
    Progress:  57.9% | 7,000,000 pixels | 94.6% population allocated
    Progress:  59.5% | 7,200,000 pixels | 94.7% population allocated
    Progress:  61.2% | 7,400,000 pixels | 95.3% population allocated
    Progress:  62.9% | 7,600,000 pixels | 95.5% population allocated
    Progress:  64.5% | 7,800,000 pixels | 95.7% population allocated
    Progress:  66.2% | 8,000,000 pixels | 95.9% population allocated
    Progress:  67.8% | 8,200,000 pixels | 96.0% population allocated
    Progress:  69.5% | 8,400,000 pixels | 96.1% population allocated
    Progress:  71.1% | 8,600,000 pixels | 96.2% population allocated
    Progress:  72.8% | 8,800,000 pixels | 96.3% population allocated
    Progress:  74.4% | 9,000,000 pixels | 96.4% population allocated
    Progress:  76.1% | 9,200,000 pixels | 96.5% population allocated
    Progress:  77.7% | 9,400,000 pixels | 96.8% population allocated
    Progress:  79.4% | 9,600,000 pixels | 97.0% population allocated
    Progress:  81.0% | 9,800,000 pixels | 97.4% population allocated
    Progress:  82.7% | 10,000,000 pixels | 97.5% population allocated
    Progress:  84.4% | 10,200,000 pixels | 97.6% population allocated
    Progress:  86.0% | 10,400,000 pixels | 97.6% population allocated
    Progress:  87.7% | 10,600,000 pixels | 97.7% population allocated
    Progress:  89.3% | 10,800,000 pixels | 97.7% population allocated
    Progress:  91.0% | 11,000,000 pixels | 97.8% population allocated
    Progress:  92.6% | 11,200,000 pixels | 97.9% population allocated
    Progress:  94.3% | 11,400,000 pixels | 98.1% population allocated
    Progress:  95.9% | 11,600,000 pixels | 99.1% population allocated
    Progress:  97.6% | 11,800,000 pixels | 99.4% population allocated
    Progress:  99.2% | 12,000,000 pixels | 99.8% population allocated
    Progress: 100.0% | 12,091,883 pixels | 99.8% population allocated

  Vectorized allocation complete:
    Total population: 10,203,140
    Allocated population: 10,179,256 (99.8%)
    Unallocated population: 23,884 (0.2%)
    Pixels processed: 12,091,883
    Facilities receiving allocation: 188
    Sum of facility allocations: 10,179,256
    Pixel allocations tracked: 7,530,641

Facility allocation summary:
  Facilities with allocated population: 188
  Total allocated population: 10,179,256

Top 15 facilities by allocated population:
                          facility_id  allocated_population
                  Al-Basheer Hospital         396742.157848
              Princess Rahma Hospital         313426.565748
               Princess Raya Hospital         231499.719475
Prince Faisal Bin Al-Hussein Hospital         215654.433464
  Princess Basma Comprehensive Center         209829.588257
    North Hashmi Comprehensive Center         190190.030987
               Prince Hamzah Hospital         189876.847054
   Dhaheyat Al-Hussein Primary Center         185325.964350
             Al-Theraa Primary Center         173946.450135
              Princess Basma Hospital         173236.646651
                    AL-Zarqa Hospital         166412.115485
           Amman Comprehensive Center         149996.439703
       Tabarbour Comprehensive Center         142863.158002
               Khazzan Primary Center         142006.777288
        Luaibdeh Comprehensive Center         135134.983792

Pixel allocations tracked: 7,530,641
```

### Cell 11

```text

================================================================================
AGGREGATING FACILITIES TO HSAs (THREE-CASE LOGIC)
================================================================================
  Gravity model parameters: alpha=0.75, beta=1.5
  Case 2 fallback guard: max=100.0km, radius_multiplier=1.50, min_allowance=30.0km, major_pop_threshold=25,000
  Major facility volume threshold: 513

Facility Assignment Summary:
  Case 1 (Inside 1 HSA):            155 facilities
  Case 2 (Outside, assigned):         9 facilities
  Case 3 (Overlapping, proportional):   23 facilities
  EXCLUDED (no admissible fallback):    1 facilities
  Total:                            188 facilities

Excluded Facilities (no admissible fallback; anchor promotion needed):
  Count: 1
  Total excluded population: 702
    - Swaqa Correctional Primary: 702 people (nearest: Jadaa Primary Center, 30.8km)

HSA Population Summary:
HSA Anchor                                         Population   Facilities
---------------------------------------------------------------------------
  Al-Basheer Hospital                               4,085,364           36
  AL-Zarqa Hospital                                 1,229,143           14
  Princess Raya Hospital                            1,140,072            5
  Al Hussain New Salt Hospital                        690,864           15
  Jarash Hospital                                     468,590           10
  AL-Ramtha Hospital                                  405,381           12
  Al-Karak Hospital                                   393,082           30
  Al-Mafraq Gynecology and Pediatrics Hospital         369,366           12
  Dr. Jamel Al-Totanji Hospital                       276,345            8
  AL-Nadeem Hospital                                  258,821           12
  Khazzan Primary Center                              182,642            4
  AL-Shuneh Hospital                                  133,795            2
  Tafilah Governmental Hospital                       113,330            3
  Al-Yarmouk Hospital                                 104,602            3
  Maan Hospital                                        93,962            2
  Queen Rania Hospital                                 90,279            2
  Mabroukeh Primary Center                             82,015            2
  Prince Hashem Primary Center                         35,722            4
  Jadaa Primary Center                                 25,179           11
---------------------------------------------------------------------------
  TOTAL                                            10,178,554          187

================================================================================
```

### Cell 12

```text

Facility Assignment Breakdown by Case:
                      assignment_case  count  total_population  pct_facilities  pct_population
                 Case 1: Inside 1 HSA    155      8.928356e+06            82.4            87.7
   Case 2: Outside all HSAs (nearest)      9      1.828006e+05             4.8             1.8
Case 3: Inside 2+ HSAs (proportional)     23      1.067397e+06            12.2            10.5
  EXCLUDED: Requires anchor promotion      1      7.017931e+02             0.5             0.0
```

### Cell 14

```text
Saved HSA population summary: out/INF_footprint_hsa_populations_probabilistic_v8.csv
Saved facility allocations: out/INF_footprint_facility_allocations_probabilistic_v8.csv
Saved facility-to-HSA assignments: out/INF_footprint_facility_hsa_assignments_v8.csv
Saved pixel allocations: out/pixel_allocations_INF_footprint_v8.csv
Saved allocation details: out/INF_footprint_allocation_details_v8.csv
  File size: 744.3 MB
```

### Cell 16

```text

================================================================================
TABLE 1: HSA Population Summary (Probabilistic Allocation)
================================================================================
Network: INF | HSA Mode: footprint
--------------------------------------------------------------------------------
 Rank                                   HSA Anchor Allocated Population  Facilities
    1                          Al-Basheer Hospital            4,085,364          36
    2                            AL-Zarqa Hospital            1,229,143          14
    3                       Princess Raya Hospital            1,140,072           5
    4                 Al Hussain New Salt Hospital              690,864          15
    5                              Jarash Hospital              468,590          10
    6                           AL-Ramtha Hospital              405,381          12
    7                            Al-Karak Hospital              393,082          30
    8 Al-Mafraq Gynecology and Pediatrics Hospital              369,366          12
    9                Dr. Jamel Al-Totanji Hospital              276,345           8
   10                           AL-Nadeem Hospital              258,821          12
   11                       Khazzan Primary Center              182,642           4
   12                           AL-Shuneh Hospital              133,795           2
   13                Tafilah Governmental Hospital              113,330           3
   14                          Al-Yarmouk Hospital              104,602           3
   15                                Maan Hospital               93,962           2
   16                         Queen Rania Hospital               90,279           2
   17                     Mabroukeh Primary Center               82,015           2
   18                 Prince Hashem Primary Center               35,722           4
   19                         Jadaa Primary Center               25,179          11
--------------------------------------------------------------------------------
TOTAL                                                          10,178,554          187
================================================================================
```

### Cell 17

```text

================================================================================
TABLE 2: Facility Assignment Case Distribution
================================================================================
                      assignment_case  facilities population  pct_facilities  pct_population
                 Case 1: Inside 1 HSA         155  8,928,356            82.4            87.7
   Case 2: Outside all HSAs (nearest)           9    182,801             4.8             1.8
Case 3: Inside 2+ HSAs (proportional)          23  1,067,397            12.2            10.5
  EXCLUDED: Requires anchor promotion           1        702             0.5             0.0
================================================================================
```

### Cell 18

```text

================================================================================
TABLE 3: Top 20 Facilities by Allocated Population
================================================================================
                             Facility Population      Assignment Case            Primary HSA
                  Al-Basheer Hospital    396,742 Case 1: Inside 1 HSA    Al-Basheer Hospital
              Princess Rahma Hospital    313,427 Case 1: Inside 1 HSA Princess Raya Hospital
               Princess Raya Hospital    231,500 Case 1: Inside 1 HSA Princess Raya Hospital
Prince Faisal Bin Al-Hussein Hospital    215,654 Case 1: Inside 1 HSA      AL-Zarqa Hospital
  Princess Basma Comprehensive Center    209,830 Case 1: Inside 1 HSA    Al-Basheer Hospital
    North Hashmi Comprehensive Center    190,190 Case 1: Inside 1 HSA    Al-Basheer Hospital
               Prince Hamzah Hospital    189,877 Case 1: Inside 1 HSA    Al-Basheer Hospital
   Dhaheyat Al-Hussein Primary Center    185,326 Case 1: Inside 1 HSA    Al-Basheer Hospital
             Al-Theraa Primary Center    173,946 Case 1: Inside 1 HSA    Al-Basheer Hospital
              Princess Basma Hospital    173,237 Case 1: Inside 1 HSA Princess Raya Hospital
                    AL-Zarqa Hospital    166,412 Case 1: Inside 1 HSA      AL-Zarqa Hospital
           Amman Comprehensive Center    149,996 Case 1: Inside 1 HSA    Al-Basheer Hospital
       Tabarbour Comprehensive Center    142,863 Case 1: Inside 1 HSA    Al-Basheer Hospital
               Khazzan Primary Center    142,007 Case 1: Inside 1 HSA Khazzan Primary Center
        Luaibdeh Comprehensive Center    135,135 Case 1: Inside 1 HSA    Al-Basheer Hospital
           Naser Comprehensive Center    130,595 Case 1: Inside 1 HSA    Al-Basheer Hospital
                   AL-Nadeem Hospital    128,332 Case 1: Inside 1 HSA     AL-Nadeem Hospital
              Istiqlal Primary Center    125,140 Case 1: Inside 1 HSA    Al-Basheer Hospital
               Natheef Primary Center    124,838 Case 1: Inside 1 HSA    Al-Basheer Hospital
           Jufeh Comprehensive Center    121,401 Case 1: Inside 1 HSA    Al-Basheer Hospital
================================================================================
```

### Cell 19

```text

================================================================================
VALIDATION: Population Coverage
================================================================================
Total population in raster:          10,203,140
Total allocated to facilities:       10,179,256 (99.8%)
Total assigned to HSAs:              10,178,554 (99.8%)
Excluded (beyond max dist):                 702 (0.01%)
================================================================================
```

### Cell 20

```text

================================================================================
PROBABILISTIC ALLOCATION COMPLETE
================================================================================

Output files saved to out:
  - INF_footprint_hsa_populations_probabilistic_v8.csv
  - INF_footprint_facility_allocations_probabilistic_v8.csv
  - INF_footprint_facility_hsa_assignments_v8.csv
  - pixel_allocations_INF_footprint_v8.csv (for downstream compatibility)
```

### Cell 21

```text
Saved notebook summary: out/textresults/Population_Allocation_Probabilistic_v2_INF_footprint_v8_results.md
```
