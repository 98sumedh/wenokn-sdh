# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model            ElasticNet  RandomForest  Ridge
Spatial Unit                                    
Country-level       -0.1137       -0.1519 -0.128
Governorate         -0.1751       -0.1750 -0.200
HSA (FOOTPRINT)      0.6359        0.5797  0.635
Per-HSA (Panel)      0.6359        0.5797  0.635

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
