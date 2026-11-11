# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.3799 | 0.62°C | 17.0% |
| Between HSA | 1.8558 | 1.36°C | 83.0% |
| **ICC** | | | **0.830** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 8632.5 | 93m | 6.5% |
| Between HSA | 124617.8 | 353m | 93.5% |
| **ICC** | | | **0.935** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.93°C
- Correlation (simple vs weighted): 0.9933

## Interpretation

- **Temperature ICC = 0.830**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
