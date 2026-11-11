# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.6638  0.6303       0.0000
   B_AR_Seasonal_Means          14   0.6668  0.6268      -0.0035
C_AR_Seasonal_Extremes          26   0.6690  0.6327       0.0024
    D_AR_Seasonal_Both          36   0.6714  0.6256      -0.0047

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6303
- Adding climate means: R² = 0.6268 (Δ = -0.35%)
- Adding extreme indicators: R² = 0.6327 (Δ = +0.24%)

**Conclusion:** Extreme indicators outperform climate means.
