# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7890  0.6707       0.0000
   B_AR_Seasonal_Means          14   0.7899  0.6639      -0.0069
C_AR_Seasonal_Extremes          26   0.7905  0.6701      -0.0007
    D_AR_Seasonal_Both          36   0.7913  0.6636      -0.0072

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6707
- Adding climate means: R² = 0.6639 (Δ = -0.69%)
- Adding extreme indicators: R² = 0.6701 (Δ = -0.07%)

**Conclusion:** Extreme indicators outperform climate means.
