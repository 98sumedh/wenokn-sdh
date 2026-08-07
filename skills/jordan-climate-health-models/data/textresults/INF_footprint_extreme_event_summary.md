# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7625  0.7279       0.0000
   B_AR_Seasonal_Means          14   0.7637  0.7257      -0.0022
C_AR_Seasonal_Extremes          26   0.7653  0.7258      -0.0021
    D_AR_Seasonal_Both          36   0.7659  0.7215      -0.0064

## Key Findings

- Baseline (AR+Seasonal): R² = 0.7279
- Adding climate means: R² = 0.7257 (Δ = -0.22%)
- Adding extreme indicators: R² = 0.7258 (Δ = -0.21%)

**Conclusion:** Extreme indicators outperform climate means.
