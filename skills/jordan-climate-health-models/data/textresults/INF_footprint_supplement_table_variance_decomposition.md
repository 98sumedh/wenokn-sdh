# Table S_X: Variance Decomposition Across Model Specifications

    Model Specification  N Features Train R² Test R² Overfit Gap
           Climate only           8   0.0211 -0.0015      0.0226
    Autoregressive only           2   0.7709  0.7269      0.0441
          Seasonal only           4   0.0169  0.0015      0.0154
          AR + Seasonal           6   0.7714  0.7272      0.0442
     Climate + Seasonal          12   0.0255  0.0126      0.0130
           AR + Climate          10   0.7721  0.7266      0.0455
AR + Climate + Seasonal          14   0.7725  0.7257      0.0467

## Key Findings

- AR-only model explains 72.7% of variance
- Climate-only model explains -0.2% of variance
- Climate adds -0.1% beyond AR + Seasonal
- AR-Climate overlap: -0.1%
