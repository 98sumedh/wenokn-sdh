# Extreme Event Analysis: Means vs Extremes

## Model Comparison

                 Model  N Features Train R² Test R² Contribution
    A_AR_Seasonal_Only           4   0.7556  0.6302       0.0000
   B_AR_Seasonal_Means          14   0.7579  0.6123      -0.0179
C_AR_Seasonal_Extremes          26   0.7584  0.6254      -0.0048
    D_AR_Seasonal_Both          36   0.7608  0.6065      -0.0236

## Key Findings

- Baseline (AR+Seasonal): R² = 0.6302
- Adding climate means: R² = 0.6123 (Δ = -1.79%)
- Adding extreme indicators: R² = 0.6254 (Δ = -0.48%)

**Conclusion:** Extreme indicators outperform climate means.
