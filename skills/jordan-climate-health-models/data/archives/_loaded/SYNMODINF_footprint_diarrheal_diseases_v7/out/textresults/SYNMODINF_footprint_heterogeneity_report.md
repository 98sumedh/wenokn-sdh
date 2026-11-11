# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.6009 | 0.78°C | 27.7% |
| Between HSA | 1.5652 | 1.25°C | 72.3% |
| **ICC** | | | **0.723** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 18208.9 | 135m | 13.4% |
| Between HSA | 117388.6 | 343m | 86.6% |
| **ICC** | | | **0.866** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.08°C
- Max absolute temperature difference: 1.62°C
- Correlation (simple vs weighted): 0.9789

## Interpretation

- **Temperature ICC = 0.723**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
