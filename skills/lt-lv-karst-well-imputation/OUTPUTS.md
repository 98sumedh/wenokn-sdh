# Output Contract

A run creates `run_manifest.json` and four subdirectories:

```text
results/
├── run_manifest.json
├── tables/
├── figures/
├── shap/
└── models/
```

CSV is always supported when enabled. Parquet is written when `pyarrow` or another compatible engine is installed.

## Core series

### `tables/imputed_groundwater_levels`

One row per configured well and daily grid date. Important fields include:

| Field | Meaning |
|---|---|
| `gw_level_m_asl_original` | Original source groundwater level |
| `gw_level_m_asl_cleaned` | Value retained after quality control |
| `gw_level_m_asl_model_prediction` | Model prediction, including dates that are observed |
| `gw_level_m_asl_prediction_std` | Standard deviation across Extra Trees members |
| `gw_level_m_asl_imputed` | Cleaned observation where available, otherwise prediction |
| `target_quality_flag` | Original, missing, spike, known corruption, or synthetic anchor status |
| `is_imputed` | True only where the final value comes from the model |
| `value_source` | `observed_cleaned`, `model_imputed`, `synthetic_anchor`, or `unresolved` |
| `prediction_scope` | Internal gap, leading/trailing extrapolation, unresolved, or not imputed |
| `imputation_feature_set` | Winning feature-set name |
| `imputation_params` | Winning Extra Trees parameters |

Do not discard the provenance and scope fields when using the final series.

## Model evaluation

### `tables/well_model_summary`

One row per successfully modeled well. It includes counts, winning specification, repeated inner-CV metrics, and independent outer masked-gap metrics.

Use `outer_r2`, `outer_mae`, and `outer_rmse` for final performance reporting. `cv_*` metrics describe model-selection results.

### `tables/candidate_model_metrics`

All evaluated feature-set and hyperparameter combinations for each well.

### `tables/outer_holdout_predictions`

Observed and predicted values for the untouched outer masked intervals. This table supports residual analysis and independent plotting.

### `tables/cv_masked_intervals`

Date boundaries and observed-value counts for each repeated inner validation interval.

## Quality-control outputs

### `tables/signal_cleaning_events`

Every source target value removed as a spike or by a configured domain interval, plus any optional synthetic anchor.

### `tables/skipped_wells`

Wells not modeled and the reason, such as missing input, insufficient accepted observations, or no valid candidate.

## Interpretation outputs

### Feature importance

- `feature_importance_per_well`
- `figures/feature_importance_comparison.png`

### Multicollinearity

- `vif_per_well`
- `vif_aggregate`

VIF is diagnostic. High VIF does not invalidate tree predictions, but it complicates interpretation of individual predictors.

### SHAP

- `shap_importance_per_well`
- `shap_importance_aggregate`
- `shap_values_sample`
- `shap/shap_beeswarm_<feature_set>.png`
- `shap/shap_beeswarm_stacked.png`

SHAP files are omitted if SHAP is disabled or fails to run.

### Signal noise

- `noise_metrics`
- `noise_vs_performance`
- `figures/groundwater_noise_vs_performance.png`

The preferred noise indicator is the standard deviation of first differences after within-well standardization.

### Time series

- `figures/stacked_imputation_timeseries.png`

The figure distinguishes accepted observations, model-imputed values, and removed original values.

## Saved models

When enabled, `models/<well>_extra_trees.joblib` contains:

- trained Extra Trees model;
- selected feature list;
- training medians;
- selected parameters;
- target name and well identifier.

A saved model should be applied only with identically generated features and matching input units.
