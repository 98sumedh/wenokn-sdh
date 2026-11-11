# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7676  0.6449       0.0000
   B_AR_Seasonal_Means          14   0.7690  0.6357      -0.0091
C_AR_Seasonal_Extremes          26   0.7699  0.6412      -0.0037
    D_AR_Seasonal_Both          36   0.7710  0.6373      -0.0076

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6449
- Adding climate means: R² = 0.6357 (Δ = -0.91%)
- Adding extreme indicators: R² = 0.6412 (Δ = -0.37%)

**Conclusion:** Extreme indicators outperform climate means.
