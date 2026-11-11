# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model                           ElasticNet  RandomForest   Ridge
Spatial Unit                                                    
Country-level                      -0.0086       -0.1223 -0.0052
Governorate                        -0.0635       -0.0106 -0.0656
HSA (GOVERNORATE_TAU_COVERAGE)      0.6636        0.6499  0.6626
Per-HSA (Panel)                     0.6636        0.6499  0.6626

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
