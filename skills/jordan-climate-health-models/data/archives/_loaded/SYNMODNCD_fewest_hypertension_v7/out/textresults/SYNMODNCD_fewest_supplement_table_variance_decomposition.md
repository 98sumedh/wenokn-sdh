# Table S_X: Variance Decomposition Across Model Specifications

    Model Specification  N Features Train R² Test R² Overfit Gap
           Climate only           8   0.0205 -0.0826      0.1032
    Autoregressive only           2   0.7452  0.6037      0.1415
          Seasonal only           4   0.0076 -0.0167      0.0243
          AR + Seasonal           6   0.7453  0.6028      0.1425
     Climate + Seasonal          12   0.0236 -0.0696      0.0932
           AR + Climate          10   0.7472  0.5829      0.1642
AR + Climate + Seasonal          14   0.7477  0.5844      0.1633

## Key Findings

- AR-only model explains 60.4% of variance
- Climate-only model explains -8.3% of variance
- Climate adds -1.8% beyond AR + Seasonal
- AR-Climate overlap: -6.2%
