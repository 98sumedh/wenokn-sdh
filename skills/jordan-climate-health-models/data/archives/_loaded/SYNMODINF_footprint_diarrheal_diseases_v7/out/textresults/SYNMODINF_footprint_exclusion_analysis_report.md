# Phase 1A: Excluded Population Analysis

## Overview

- **Total pixels analyzed**: 7,530,641
- **Total population**: 10,179,256

## Probability Distribution

| Statistic | Value |
|-----------|-------|
| Mean | 0.300 |
| Median | 0.189 |
| Std Dev | 0.268 |
| P10 | 0.047 |
| P90 | 0.795 |

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
| strong | 935,718 | 9.2% | 62.0 |
| moderate | 2,972,598 | 29.2% | 42.4 |
| weak | 3,502,458 | 34.4% | 31.0 |
| very_weak | 2,768,481 | 27.2% | 30.5 |

## Population by Distance Class

| Class | Population | % Total | Mean Probability |
|-------|------------|---------|-----------------|
| urban | 7,898,198 | 77.6% | 0.232 |
| peri_urban | 1,872,059 | 18.4% | 0.184 |
| rural | 272,180 | 2.7% | 0.236 |
| remote | 85,077 | 0.8% | 0.241 |
| very_remote | 51,743 | 0.5% | 0.430 |

## Comparison: Connected vs Poorly Connected

           Group   Population  Pixels  Mean Probability  Mean Distance (km)  Median Distance (km)  P90 Distance (km)  Population %
  Well Connected 9.883865e+06 5125604          0.402194           39.265570             28.677254          91.179133     97.098112
Poorly Connected 2.953906e+05 2405037          0.083422           44.753119             43.001418          73.544823      2.901888
  All Population 1.017926e+07 7530641          0.300389           41.018111             35.707908          86.966379    100.000000

## Key Findings

1. **61.6%** of population has weak/very weak probability allocation
2. **1.3%** of population is in remote/very remote areas
3. Only **38.4%** of population is strongly or moderately connected
4. Mean allocation probability is only **30.0%**
5. Mean distance to nearest facility is **41.0 km**

## Implications for Climate-Health Modeling

The weak allocation probabilities suggest that the gravity model assigns most populations
to facilities with low confidence. This has several implications:

1. **Disease case assignment uncertainty**: Most cases are allocated with <50% confidence
2. **Spatial averaging of climate**: If assignment is uncertain, climate signals get diluted
3. **Need for alternative approaches**: Consider testing climate effects in remote areas
   where disease surveillance might use different methods (community health workers, etc.)
