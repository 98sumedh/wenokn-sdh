# Table S_X: Variance Decomposition Across Model Specifications

    Model Specification  N Features Train R² Test R² Overfit Gap
           Climate only           8   0.0299  0.0226      0.0073
    Autoregressive only           2   0.7382  0.7084      0.0298
          Seasonal only           4   0.0098  0.0009      0.0088
          AR + Seasonal           6   0.7385  0.7086      0.0300
     Climate + Seasonal          12   0.0347  0.0260      0.0086
           AR + Climate          10   0.7392  0.7087      0.0305
AR + Climate + Seasonal          14   0.7396  0.7079      0.0317

## Key Findings

- AR-only model explains 70.8% of variance
- Climate-only model explains 2.3% of variance
- Climate adds -0.1% beyond AR + Seasonal
- AR-Climate overlap: 2.2%
