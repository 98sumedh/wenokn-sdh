# Table S_X: Variance Decomposition Across Model Specifications

    Model Specification  N Features Train R² Test R² Overfit Gap
           Climate only           8   0.0467  0.0050      0.0417
    Autoregressive only           2   0.6776  0.6227      0.0549
          Seasonal only           4   0.0329  0.0032      0.0297
          AR + Seasonal           6   0.6789  0.6237      0.0552
     Climate + Seasonal          12   0.0475  0.0163      0.0312
           AR + Climate          10   0.6804  0.6226      0.0578
AR + Climate + Seasonal          14   0.6813  0.6206      0.0608

## Key Findings

- AR-only model explains 62.3% of variance
- Climate-only model explains 0.5% of variance
- Climate adds -0.3% beyond AR + Seasonal
- AR-Climate overlap: 0.5%
