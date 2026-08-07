# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model            ElasticNet  RandomForest   Ridge
Spatial Unit                                     
Country-level       -0.1999       -1.1408 -0.1032
Governorate         -0.1384       -1.1017 -0.1032
HSA (FOOTPRINT)      0.7263        0.7528  0.7259
Per-HSA (Panel)      0.7263        0.7528  0.7259

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
