# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model            ElasticNet  RandomForest   Ridge
Spatial Unit                                     
Country-level       -0.3025       -1.3815 -0.1760
Governorate          0.0129        0.0193  0.0152
HSA (FEWEST)         0.6227        0.6315  0.6215
Per-HSA (Panel)      0.6227        0.6315  0.6215

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
