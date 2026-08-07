# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.2173 | 0.47°C | 38.6% |
| Between HSA | 0.3452 | 0.59°C | 61.4% |
| **ICC** | | | **0.614** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 4701.2 | 69m | 38.3% |
| Between HSA | 7557.6 | 87m | 61.7% |
| **ICC** | | | **0.617** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 1.12°C
- Correlation (simple vs weighted): 0.9268

## Interpretation

- **Temperature ICC = 0.614**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
