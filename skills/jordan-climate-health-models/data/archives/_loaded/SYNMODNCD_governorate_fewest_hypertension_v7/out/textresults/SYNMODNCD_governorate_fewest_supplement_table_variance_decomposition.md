# Table S_X: Variance Decomposition Across Model Specifications

    Model Specification  N Features Train R² Test R² Overfit Gap
           Climate only           8   0.0152 -0.0795      0.0947
    Autoregressive only           2   0.7456  0.6031      0.1425
          Seasonal only           4   0.0079 -0.0172      0.0252
          AR + Seasonal           6   0.7457  0.6022      0.1435
     Climate + Seasonal          12   0.0261 -0.0553      0.0813
           AR + Climate          10   0.7473  0.5821      0.1652
AR + Climate + Seasonal          14   0.7483  0.5844      0.1639

## Key Findings

- AR-only model explains 60.3% of variance
- Climate-only model explains -8.0% of variance
- Climate adds -1.8% beyond AR + Seasonal
- AR-Climate overlap: -5.9%
