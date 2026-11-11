# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7581  0.7317       0.0000
   B_AR_Seasonal_Means          14   0.7593  0.7296      -0.0021
C_AR_Seasonal_Extremes          26   0.7610  0.7291      -0.0026
    D_AR_Seasonal_Both          36   0.7615  0.7249      -0.0067

## Key Findings

- Baseline (AR+Seasonal): R² = 0.7317
- Adding climate means: R² = 0.7296 (Δ = -0.21%)
- Adding extreme indicators: R² = 0.7291 (Δ = -0.26%)

**Conclusion:** Climate means outperform extreme indicators.
