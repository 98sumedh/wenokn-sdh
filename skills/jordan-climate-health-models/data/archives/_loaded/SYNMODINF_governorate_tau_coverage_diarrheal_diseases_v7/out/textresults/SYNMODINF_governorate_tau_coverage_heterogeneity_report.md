# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.3556 | 0.60°C | 16.2% |
| Between HSA | 1.8356 | 1.35°C | 83.8% |
| **ICC** | | | **0.838** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 8903.2 | 94m | 9.2% |
| Between HSA | 88301.0 | 297m | 90.8% |
| **ICC** | | | **0.908** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.94°C
- Correlation (simple vs weighted): 0.9926

## Interpretation

- **Temperature ICC = 0.838**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
