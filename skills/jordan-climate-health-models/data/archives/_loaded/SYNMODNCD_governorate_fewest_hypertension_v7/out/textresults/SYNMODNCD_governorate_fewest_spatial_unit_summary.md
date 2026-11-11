# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model                     ElasticNet  RandomForest   Ridge
Spatial Unit                                              
Country-level                -0.1219       -0.1561 -0.1436
Governorate                  -0.1814        0.0081 -0.1849
HSA (GOVERNORATE_FEWEST)      0.6135        0.5941  0.6109
Per-HSA (Panel)               0.6135        0.5941  0.6109

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
