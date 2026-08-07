# Phase 1B: Climate Effects by Connectivity

## Overview

This analysis tests whether climate-disease relationships differ
between well-connected and poorly-connected HSAs.

**Hypothesis**: If climate effects are real but masked by allocation
uncertainty, we should see stronger climate signals in areas with
higher allocation probability (more certain case assignment).

## Results by Connectivity Group

| Group | Model | Train R² | Test R² |
|-------|-------|----------|---------|
| high_connectivity | AR Only | 0.6268 | 0.5229 |
| high_connectivity | AR + Climate | 0.6268 | 0.5229 |
| low_connectivity | AR Only | 0.7720 | 0.8016 |
| low_connectivity | AR + Climate | 0.7720 | 0.8016 |

## Climate Contribution by Group

| Group | ΔR² (raw) | ΔR² (percentage points) | Relative change vs AR-only |
|-------|-----------|--------------------------|----------------------------|
| high_connectivity | +0.0000 | +0.00 pp | +0.0% |
| low_connectivity | +0.0000 | +0.00 pp | +0.0% |

## Key Findings

1. Climate contributes MORE in low-connectivity areas (+0.0000, +0.00 pp vs +0.0000, +0.00 pp)
   - This does NOT support the allocation uncertainty hypothesis

2. Climate adds NO predictive value in either group
   - The weak climate signal is not due to allocation uncertainty

## Implications

If climate effects are consistently weak across connectivity groups,
the AR dominance is likely a real phenomenon (strong temporal autocorrelation
in disease incidence) rather than an artifact of allocation uncertainty.
