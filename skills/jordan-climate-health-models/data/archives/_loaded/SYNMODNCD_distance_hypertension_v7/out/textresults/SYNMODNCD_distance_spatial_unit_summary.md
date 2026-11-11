# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model            ElasticNet  RandomForest   Ridge
Spatial Unit                                     
Country-level       -0.0964       -0.0956 -0.1107
Governorate         -0.2181       -0.0683 -0.2237
HSA (DISTANCE)       0.5939        0.5341  0.5913
Per-HSA (Panel)      0.5939        0.5341  0.5913

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
