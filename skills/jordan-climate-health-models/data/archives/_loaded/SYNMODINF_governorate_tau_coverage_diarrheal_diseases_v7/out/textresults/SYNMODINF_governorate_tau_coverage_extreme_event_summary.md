# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7283  0.7092       0.0000
   B_AR_Seasonal_Means          14   0.7293  0.7088      -0.0003
C_AR_Seasonal_Extremes          26   0.7304  0.7087      -0.0005
    D_AR_Seasonal_Both          36   0.7308  0.7073      -0.0018

## Key Findings

- Baseline (AR+Seasonal): R² = 0.7092
- Adding climate means: R² = 0.7088 (Δ = -0.03%)
- Adding extreme indicators: R² = 0.7087 (Δ = -0.05%)

**Conclusion:** Climate means outperform extreme indicators.
