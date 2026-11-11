# Table S_X: Cross-Spatial-Unit Model Comparison

Test R² across different spatial aggregation units and model types.

Model                     ElasticNet  RandomForest   Ridge
Spatial Unit                                              
Country-level                -0.3094       -1.2738 -0.1944
Governorate                   0.0126        0.0263  0.0135
HSA (GOVERNORATE_FEWEST)      0.6273        0.6392  0.6267
Per-HSA (Panel)               0.6273        0.6392  0.6267

## Key Findings

- HSA-level aggregation preserves within-unit heterogeneity
- Country-level aggregation loses spatial resolution
- Panel structure (per-HSA) allows cross-sectional learning
