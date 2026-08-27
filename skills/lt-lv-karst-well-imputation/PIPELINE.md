# Pipeline

## Data flow

```text
Processed daily hydroclimatic and groundwater table
                         │
                         ▼
             Select seven LT-LV wells
             and 2003-2023 interval
                         │
                         ▼
              Validate schema, dates,
              numeric values and duplicates
                         │
                         ▼
              Regularize each well to a
                 complete daily grid
                         │
                         ▼
         Preserve original groundwater level
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     isolated-spike review    configured bad intervals
              └──────────┬──────────┘
                         ▼
                cleaned target series
                         │
                         ▼
       hydroclimatic lags, rolling values,
        seasonality, anomalies and flags
                         │
                         ▼
       outer contiguous masked-gap holdout
                         │
                         ▼
 repeated inner contiguous-gap model selection
    seasonal vs non-seasonal + Extra Trees grid
                         │
                         ▼
             outer holdout evaluation
                         │
                         ▼
     final per-well fit on accepted observations
                         │
                         ▼
     daily prediction + tree-dispersion estimate
                         │
                         ▼
 original / cleaned / prediction / final imputed
                         │
                         ▼
 VIF, feature importance, SHAP, noise diagnostics
```

## Stage 1 — scope and validation

The pipeline selects only configured well IDs and dates. Required variables are converted to numeric values. Invalid dates are removed and reported. Duplicate well-date rows cause an error by default because silent aggregation can change groundwater signals.

When daily regularization is enabled, a complete calendar grid is created for each configured well. Missing dates are added. Time-varying predictors are not automatically interpolated; later median filling is fitted only on each model-training sample.

## Stage 2 — signal quality control

Three target representations are maintained:

- `gw_level_m_asl_original` — untouched source value;
- `gw_level_m_asl_cleaned` — accepted value after quality masks;
- `gw_level_m_asl_imputed` — cleaned observation where available, otherwise model reconstruction.

The default spike detector identifies an isolated point that differs sharply from both neighboring values. The jump threshold is calculated separately for each well. This avoids the source notebook's cross-well threshold contamination and reduces removal of valid sustained groundwater changes.

Configured bad intervals are applied after generic spike detection and take precedence. The default domain rule masks `LT_35996` beginning on 1 June 2022.

## Stage 3 — features

After daily regularization, row shifts correspond to calendar-day lags. The default lags are 30, 60, 90, 180, 270, and 360 days. Rolling windows are 60 and 90 days.

Precipitation and actual evapotranspiration receive rolling sums. Temperature and groundwater storage receive rolling means. The manually selected model feature sets use 90-day accumulated precipitation, lagged temperature, current and lagged groundwater storage, and optional seasonal terms.

Auxiliary diagnostic features include:

- sine and cosine day-of-year and month encodings;
- seasonal phase;
- precipitation anomaly and drought flag;
- groundwater-storage monthly anomaly;
- 30-day storage change and recharge-event flag;
- 30-day below-freezing fraction;
- per-well monthly climatologies.

## Stage 4 — model selection

Each well is modeled independently. The default estimator is `ExtraTreesRegressor`.

A contiguous outer mask is created before model selection. The remaining observed values form the selection pool. Repeated inner masks then evaluate each combination of:

- feature set;
- number of trees;
- tree depth;
- minimum split size;
- minimum leaf size;
- feature fraction.

The best candidate maximizes mean inner-CV R² and uses lower RMSE as a tie-breaker.

## Stage 5 — outer evaluation and reconstruction

The selected model is fitted without the outer observations and evaluated on them. These metrics are independent of feature-set and hyperparameter selection.

The final model is then fitted to every accepted target observation. It predicts all dates with sufficient predictor coverage. The final output retains cleaned observations and fills only missing or quality-rejected target values.

`prediction_scope` distinguishes:

- `internal_gap`;
- `leading_extrapolation`;
- `trailing_extrapolation`;
- `unresolved`;
- `not_imputed`.

## Stage 6 — diagnostics

The pipeline exports:

- native tree feature importance;
- VIF per well and aggregate VIF by feature set;
- SHAP importance and sampled SHAP values;
- groundwater-signal first-difference noise metrics;
- a noise-versus-outer-performance comparison;
- stacked imputation time series and explanatory figures.
