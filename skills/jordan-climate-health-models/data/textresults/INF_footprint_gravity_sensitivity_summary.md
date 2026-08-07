# Table S_X: Gravity Model Parameter Sensitivity Analysis

Analysis of how α (population weight) and β (distance decay) affect patient allocation patterns.

 alpha  beta concentration  gini max_share  n_facilities_used
  0.50   1.0        0.2519 0.955     47.0%                 74
  0.50   1.5        0.1619 0.942     34.5%                 81
  0.50   2.0        0.1152 0.935     21.8%                 83
  0.50   2.5        0.1141 0.931     26.0%                 87
  0.75   1.0        0.3410 0.967     55.8%                 68
  0.75   1.5        0.2519 0.955     47.0%                 74
  0.75   2.0        0.1902 0.946     39.2%                 79
  0.75   2.5        0.1421 0.939     30.4%                 82
  1.00   1.0        0.4055 0.975     61.3%                 61
  1.00   1.5        0.3150 0.964     53.4%                 70
  1.00   2.0        0.2519 0.955     47.0%                 74
  1.00   2.5        0.2021 0.947     40.9%                 78
  1.25   1.0        0.4542 0.980     65.3%                 51
  1.25   1.5        0.3647 0.971     57.9%                 66
  1.25   2.0        0.3008 0.962     52.1%                 71
  1.25   2.5        0.2519 0.955     47.0%                 74

## Key Findings

- Higher α increases concentration (larger facilities attract more patients)
- Higher β increases concentration (patients more strongly prefer nearby facilities)
- Current parameters (α=0.75, β=1.5) provide balanced allocation
- Model performance is robust to moderate allocation uncertainty
