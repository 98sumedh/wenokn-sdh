# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model                           ElasticNet  RandomForest   Ridge
Spatial Unit                                                    
Country-level                      -0.2485       -1.2435 -0.1535
Governorate                         0.0376        0.0110  0.0389
HSA (GOVERNORATE_TAU_COVERAGE)      0.7088        0.6937  0.7084
Per-HSA (Panel)                     0.7088        0.6937  0.7084

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
