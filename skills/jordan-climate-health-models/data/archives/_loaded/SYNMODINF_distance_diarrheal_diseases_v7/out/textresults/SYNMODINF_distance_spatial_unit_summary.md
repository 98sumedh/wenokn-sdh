# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model            ElasticNet  RandomForest   Ridge
Spatial Unit                                     
Country-level       -0.2405       -1.3101 -0.1408
Governorate          0.0055        0.0000  0.0027
HSA (DISTANCE)       0.6030        0.5221  0.6024
Per-HSA (Panel)      0.6030        0.5221  0.6024

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
