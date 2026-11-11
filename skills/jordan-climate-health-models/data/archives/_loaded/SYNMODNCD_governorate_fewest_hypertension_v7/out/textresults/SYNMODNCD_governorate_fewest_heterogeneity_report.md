# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.6318 | 0.79°C | 31.9% |
| Between HSA | 1.3513 | 1.16°C | 68.1% |
| **ICC** | | | **0.681** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 12526.6 | 112m | 11.5% |
| Between HSA | 96657.3 | 311m | 88.5% |
| **ICC** | | | **0.885** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.93°C
- Correlation (simple vs weighted): 0.9938

## Interpretation

- **Temperature ICC = 0.681**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
