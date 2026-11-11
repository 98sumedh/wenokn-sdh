# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.5241 | 0.72°C | 25.0% |
| Between HSA | 1.5692 | 1.25°C | 75.0% |
| **ICC** | | | **0.750** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 22427.8 | 150m | 18.8% |
| Between HSA | 96814.7 | 311m | 81.2% |
| **ICC** | | | **0.812** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.94°C
- Correlation (simple vs weighted): 0.9931

## Interpretation

- **Temperature ICC = 0.750**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
