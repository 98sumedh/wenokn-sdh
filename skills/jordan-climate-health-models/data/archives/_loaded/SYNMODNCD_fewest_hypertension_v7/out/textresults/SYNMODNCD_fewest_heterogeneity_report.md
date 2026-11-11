# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.5012 | 0.71°C | 26.1% |
| Between HSA | 1.4166 | 1.19°C | 73.9% |
| **ICC** | | | **0.739** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 13921.0 | 118m | 14.2% |
| Between HSA | 83944.8 | 290m | 85.8% |
| **ICC** | | | **0.858** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.93°C
- Correlation (simple vs weighted): 0.9938

## Interpretation

- **Temperature ICC = 0.739**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
