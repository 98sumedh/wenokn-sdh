# Phase 1A: Excluded Population Analysis

## Overview

- **Total pixels analyzed**: 7,716,531
- **Total population**: 10,181,121

## Probability Distribution

| Statistic | Value |
|-----------|-------|
| Mean | 0.260 |
| Median | 0.172 |
| Std Dev | 0.247 |
| P10 | 0.051 |
| P90 | 0.700 |

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
| strong | 698,250 | 6.9% | 80.5 |
| moderate | 2,699,400 | 26.5% | 40.8 |
| weak | 3,480,752 | 34.2% | 32.4 |
| very_weak | 3,302,719 | 32.4% | 29.0 |

## Population by Distance Class

| Class | Population | % Total | Mean Probability |
|-------|------------|---------|-----------------|
| urban | 7,943,850 | 78.0% | 0.202 |
| peri_urban | 1,872,712 | 18.4% | 0.147 |
| rural | 258,862 | 2.5% | 0.168 |
| remote | 61,503 | 0.6% | 0.162 |
| very_remote | 44,193 | 0.4% | 0.412 |

## Comparison: Connected vs Poorly Connected

           Group   Population  Pixels  Mean Probability  Mean Distance (km)  Median Distance (km)  P90 Distance (km)  Population %
  Well Connected 9.906779e+06 5048947          0.348032           40.242246             27.122751          91.655072     97.305381
Poorly Connected 2.743424e+05 2667584          0.092568           43.183197             41.874836          68.692788      2.694619
  All Population 1.018112e+07 7716531          0.259719           41.258925             36.209093          87.142477    100.000000

## Key Findings

1. **66.6%** of population has weak/very weak probability allocation
2. **1.0%** of population is in remote/very remote areas
3. Only **33.4%** of population is strongly or moderately connected
4. Mean allocation probability is only **26.0%**
5. Mean distance to nearest facility is **41.3 km**

## Implications for Climate-Health Modeling

The weak allocation probabilities suggest that the gravity model assigns most populations
to facilities with low confidence. This has several implications:

1. **Disease case assignment uncertainty**: Most cases are allocated with <50% confidence
2. **Spatial averaging of climate**: If assignment is uncertain, climate signals get diluted
3. **Need for alternative approaches**: Consider testing climate effects in remote areas
   where disease surveillance might use different methods (community health workers, etc.)
