# Input Contract

## Primary input table

The pipeline accepts CSV, zipped CSV, Parquet, Feather, Pickle, or Excel. It expects one row per well and date before optional daily-grid completion.

### Required columns

| Default column | Meaning | Expected type/unit |
|---|---|---|
| `well_no` | Monitoring-well identifier | String |
| `date` | Observation date | Date or parseable datetime |
| `gw_level_m_asl` | Groundwater elevation | Numeric, metres above sea level |
| `precipitation_mm_eobs` | Daily precipitation | Numeric, mm/day |
| `temperature_C_eobs` | Daily air temperature | Numeric, °C |
| `actual_evapotranspiration_mm_gleam` | Daily actual evapotranspiration | Numeric, mm/day |
| `gws_mm_tavg_gldas` | Groundwater-storage indicator | Numeric, mm or source-consistent anomaly |

Column names can be changed in `config.example.yaml`. The names listed in `features.predictor_columns` and feature-set definitions must remain mutually consistent.

## Well scope

The default well list is fixed to:

```text
LT_35994
LT_35995
LT_35996
LV_12225
LV_22606
LV_22610
LT_220
```

Rows for other wells are ignored. A requested well with no rows is listed in the validation report and `skipped_wells` output.

## Temporal requirements

The source workflow uses daily lags as long as 360 days. Daily regularization is therefore enabled by default. A minimum of 365 accepted target values is required by default, although a substantially longer record is preferable.

Predictor values may contain gaps. A prediction date must contain at least the configured fraction of available features. Remaining missing predictor values are filled using medians calculated from the relevant training sample only.

## Data-quality requirements

Before running, verify:

- a consistent vertical datum across each well record;
- no undocumented sensor or datum shift;
- no duplicate well-date rows;
- hydroclimatic units are consistent across the study interval;
- groundwater-storage values use a stable product and processing version;
- the configured LT_35996 corruption interval remains valid;
- any proposed LT_220 exclusion has been independently confirmed.

## Configuration input

Use `config.example.yaml` as the complete contract. High-impact sections are:

- `domain.wells` and date range;
- `domain.known_bad_intervals`;
- `cleaning.spike_detection`;
- `features.feature_sets`;
- `model` masking fractions and parameter grid;
- `diagnostics` for SHAP, VIF, and figures.
