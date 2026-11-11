# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.5728 | 0.76°C | 27.1% |
| Between HSA | 1.5371 | 1.24°C | 72.9% |
| **ICC** | | | **0.729** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 20622.7 | 144m | 17.1% |
| Between HSA | 99842.1 | 316m | 82.9% |
| **ICC** | | | **0.829** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.93°C
- Correlation (simple vs weighted): 0.9938

## Interpretation

- **Temperature ICC = 0.729**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
