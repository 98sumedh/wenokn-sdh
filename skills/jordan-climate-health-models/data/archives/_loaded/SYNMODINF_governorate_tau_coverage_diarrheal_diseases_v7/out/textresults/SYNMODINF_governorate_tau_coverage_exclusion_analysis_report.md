# Phase 1A: Excluded Population Analysis

## Overview

- **Total pixels analyzed**: 7,530,641
- **Total population**: 10,179,256

## Probability Distribution

| Statistic | Value |
|-----------|-------|
| Mean | 0.181 |
| Median | 0.120 |
| Std Dev | 0.182 |
| P10 | 0.024 |
| P90 | 0.500 |

## Distance Distribution (km)

| Statistic | Value |
|-----------|-------|
| Mean | 41.0 |
| Median | 35.7 |
| Std Dev | 30.2 |
| P10 | 5.0 |
| P90 | 87.0 |

## Population by Probability Class

| Class | Population | % Total | Mean Distance (km) |
|-------|------------|---------|-------------------|
| strong | 729,506 | 7.2% | 82.1 |
| moderate | 2,752,848 | 27.0% | 37.6 |
| weak | 3,286,160 | 32.3% | 37.9 |
| very_weak | 3,410,741 | 33.5% | 34.4 |

## Population by Distance Class

| Class | Population | % Total | Mean Probability |
|-------|------------|---------|-----------------|
| urban | 7,898,198 | 77.6% | 0.243 |
| peri_urban | 1,872,059 | 18.4% | 0.121 |
| rural | 272,180 | 2.7% | 0.120 |
| remote | 85,077 | 0.8% | 0.111 |
| very_remote | 51,743 | 0.5% | 0.253 |

## Comparison: Connected vs Poorly Connected

           Group   Population  Pixels  Mean Probability  Mean Distance (km)  Median Distance (km)  P90 Distance (km)  Population %
  Well Connected 9.831865e+06 4062792          0.272881           35.390117             14.274209          92.752749      96.58727
Poorly Connected 3.473906e+05 3467849          0.073832           47.611642             45.848358          77.228955       3.41273
  All Population 1.017926e+07 7530641          0.181220           41.018111             35.707908          86.966379     100.00000

## Key Findings

1. **65.8%** of population has weak/very weak probability allocation
2. **1.3%** of population is in remote/very remote areas
3. Only **34.2%** of population is strongly or moderately connected
4. Mean allocation probability is only **18.1%**
5. Mean distance to nearest facility is **41.0 km**

## Implications for Climate-Health Modeling

The weak allocation probabilities suggest that the gravity model assigns most populations
to facilities with low confidence. This has several implications:

1. **Disease case assignment uncertainty**: Most cases are allocated with <50% confidence
2. **Spatial averaging of climate**: If assignment is uncertain, climate signals get diluted
3. **Need for alternative approaches**: Consider testing climate effects in remote areas
   where disease surveillance might use different methods (community health workers, etc.)
