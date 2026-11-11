# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.5805 | 0.76°C | 24.8% |
| Between HSA | 1.7557 | 1.33°C | 75.2% |
| **ICC** | | | **0.752** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 15251.0 | 123m | 9.8% |
| Between HSA | 139735.7 | 374m | 90.2% |
| **ICC** | | | **0.902** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.12°C
- Max absolute temperature difference: 1.79°C
- Correlation (simple vs weighted): 0.9618

## Interpretation

- **Temperature ICC = 0.752**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
