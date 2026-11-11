# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7443  0.6110       0.0000
   B_AR_Seasonal_Means          14   0.7469  0.5940      -0.0169
C_AR_Seasonal_Extremes          26   0.7479  0.6166       0.0056
    D_AR_Seasonal_Both          36   0.7498  0.6058      -0.0052

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6110
- Adding climate means: R² = 0.5940 (Δ = -1.69%)
- Adding extreme indicators: R² = 0.6166 (Δ = +0.56%)

**Conclusion:** Extreme indicators outperform climate means.
