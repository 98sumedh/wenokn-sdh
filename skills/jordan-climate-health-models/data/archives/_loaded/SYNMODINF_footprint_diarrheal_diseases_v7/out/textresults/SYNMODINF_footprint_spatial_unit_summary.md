# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model            ElasticNet  RandomForest   Ridge
Spatial Unit                                     
Country-level       -0.2528       -1.2758 -0.1363
Governorate         -0.0049       -0.0061 -0.0050
HSA (FOOTPRINT)      0.7301        0.7551  0.7297
Per-HSA (Panel)      0.7301        0.7551  0.7297

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
