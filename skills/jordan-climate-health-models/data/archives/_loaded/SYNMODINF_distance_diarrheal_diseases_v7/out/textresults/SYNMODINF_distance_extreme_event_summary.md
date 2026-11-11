# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.6938  0.6048       0.0000
   B_AR_Seasonal_Means          14   0.6957  0.6032      -0.0017
C_AR_Seasonal_Extremes          26   0.6975  0.6052       0.0003
    D_AR_Seasonal_Both          36   0.6988  0.5994      -0.0054

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6048
- Adding climate means: R² = 0.6032 (Δ = -0.17%)
- Adding extreme indicators: R² = 0.6052 (Δ = +0.03%)

**Conclusion:** Extreme indicators outperform climate means.
