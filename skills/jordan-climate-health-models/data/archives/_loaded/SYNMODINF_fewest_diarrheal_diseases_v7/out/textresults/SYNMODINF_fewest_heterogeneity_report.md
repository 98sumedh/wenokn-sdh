# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.5003 | 0.71°C | 29.5% |
| Between HSA | 1.1934 | 1.09°C | 70.5% |
| **ICC** | | | **0.705** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 17249.6 | 131m | 14.9% |
| Between HSA | 98582.1 | 314m | 85.1% |
| **ICC** | | | **0.851** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.94°C
- Correlation (simple vs weighted): 0.9931

## Interpretation

- **Temperature ICC = 0.705**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
