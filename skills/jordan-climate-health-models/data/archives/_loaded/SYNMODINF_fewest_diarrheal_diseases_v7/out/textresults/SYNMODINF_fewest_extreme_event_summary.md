# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.6653  0.6262       0.0000
   B_AR_Seasonal_Means          14   0.6690  0.6208      -0.0054
C_AR_Seasonal_Extremes          26   0.6706  0.6260      -0.0002
    D_AR_Seasonal_Both          36   0.6733  0.6201      -0.0061

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6262
- Adding climate means: R² = 0.6208 (Δ = -0.54%)
- Adding extreme indicators: R² = 0.6260 (Δ = -0.02%)

**Conclusion:** Extreme indicators outperform climate means.
