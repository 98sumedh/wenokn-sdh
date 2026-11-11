# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7559  0.6300       0.0000
   B_AR_Seasonal_Means          14   0.7584  0.6129      -0.0172
C_AR_Seasonal_Extremes          26   0.7597  0.6217      -0.0083
    D_AR_Seasonal_Both          36   0.7620  0.6127      -0.0173

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6300
- Adding climate means: R² = 0.6129 (Δ = -1.72%)
- Adding extreme indicators: R² = 0.6217 (Δ = -0.83%)

**Conclusion:** Extreme indicators outperform climate means.
