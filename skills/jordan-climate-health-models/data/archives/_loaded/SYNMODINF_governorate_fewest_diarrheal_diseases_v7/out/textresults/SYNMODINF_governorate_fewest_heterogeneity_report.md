# Within-HSA Climate Heterogeneity Analysis

## Summary

This analysis examines climate variance within vs between Hospital Service Areas (HSAs)
to validate that HSAs are climatically coherent units for modeling.

## Variance Decomposition

### Temperature

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 0.5788 | 0.76°C | 29.8% |
| Between HSA | 1.3652 | 1.17°C | 70.2% |
| **ICC** | | | **0.702** |

### Elevation

| Component | Variance | Std Dev | % of Total |
|-----------|----------|---------|------------|
| Within HSA | 16550.8 | 129m | 15.1% |
| Between HSA | 93381.1 | 306m | 84.9% |
| **ICC** | | | **0.849** |

## Population Weighting Impact

- Mean absolute temperature difference: 0.06°C
- Max absolute temperature difference: 0.94°C
- Correlation (simple vs weighted): 0.9931

## Interpretation

- **Temperature ICC = 0.702**: HSAs are climatically DISTINCT
  - More than half the temperature variance is between HSAs
  - HSAs capture real climate differences

- **Finding**: Population weighting has minimal impact
  - Simple averaging is sufficient for this spatial resolution
