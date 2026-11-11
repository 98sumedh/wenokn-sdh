# Phase 1A: Excluded Population Analysis

## Overview

- **Total pixels analyzed**: 7,716,531
- **Total population**: 10,181,121

## Probability Distribution

| Statistic | Value |
|-----------|-------|
| Mean | 0.195 |
| Median | 0.127 |
| Std Dev | 0.213 |
| P10 | 0.027 |
| P90 | 0.501 |

## Distance Distribution (km)

| Statistic | Value |
|-----------|-------|
| Mean | 41.3 |
| Median | 36.2 |
| Std Dev | 30.3 |
| P10 | 5.0 |
| P90 | 87.1 |

## Population by Probability Class

| Class | Population | % Total | Mean Distance (km) |
|-------|------------|---------|-------------------|
| strong | 688,813 | 6.8% | 83.4 |
| moderate | 2,695,811 | 26.5% | 39.0 |
| weak | 3,305,381 | 32.5% | 37.3 |
| very_weak | 3,491,116 | 34.3% | 32.9 |

## Population by Distance Class

| Class | Population | % Total | Mean Probability |
|-------|------------|---------|-----------------|
| urban | 7,943,850 | 78.0% | 0.238 |
| peri_urban | 1,872,712 | 18.4% | 0.118 |
| rural | 258,862 | 2.5% | 0.114 |
| remote | 61,503 | 0.6% | 0.103 |
| very_remote | 44,193 | 0.4% | 0.296 |

## Comparison: Connected vs Poorly Connected

           Group   Population  Pixels  Mean Probability  Mean Distance (km)  Median Distance (km)  P90 Distance (km)  Population %
  Well Connected 9.865278e+06 4096649          0.297437           37.167737             13.992878          92.864503     96.897763
Poorly Connected 3.158425e+05 3619882          0.078287           45.888954             44.021483          73.433824      3.102237
  All Population 1.018112e+07 7716531          0.194632           41.258925             36.209093          87.142477    100.000000

## Key Findings

1. **66.8%** of population has weak/very weak probability allocation
2. **1.0%** of population is in remote/very remote areas
3. Only **33.2%** of population is strongly or moderately connected
4. Mean allocation probability is only **19.5%**
5. Mean distance to nearest facility is **41.3 km**

## Implications for Climate-Health Modeling

The weak allocation probabilities suggest that the gravity model assigns most populations
to facilities with low confidence. This has several implications:

1. **Disease case assignment uncertainty**: Most cases are allocated with <50% confidence
2. **Spatial averaging of climate**: If assignment is uncertain, climate signals get diluted
3. **Need for alternative approaches**: Consider testing climate effects in remote areas
   where disease surveillance might use different methods (community health workers, etc.)
