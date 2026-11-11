# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model            ElasticNet  RandomForest   Ridge
Spatial Unit                                     
Country-level       -0.1439       -0.1756 -0.1532
Governorate         -0.1024       -0.0777 -0.1009
HSA (FEWEST)         0.6132        0.5639  0.6097
Per-HSA (Panel)      0.6132        0.5639  0.6097

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
