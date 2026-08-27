# Data provenance — LT–LV karst daily groundwater input

## File
`processed_daily_groundwater.parquet` — the **input** table for the karst
imputation skill: one row per (well, day), 2003-01-01 → 2023-12-31, for the seven
configured wells (LT_35994, LT_35995, LT_35996, LV_12225, LV_22606, LV_22610,
LT_220).

Columns (the six-column input contract in `INPUTS.md`):
`well_no`, `date`, `gw_level_m_asl` (observed groundwater elevation, m a.s.l. —
**with gaps**, which is what the skill imputes), plus the four hydroclimatic
predictors `precipitation_mm_eobs`, `temperature_C_eobs`,
`actual_evapotranspiration_mm_gleam`, `gws_mm_tavg_gldas`.

## Source
Provided by Vytautas Samalavičius (`input_data_lt_lv_karst.zip`, Aug 2026),
derived from the LT/LV karst monitoring network joined to E-OBS climate, GLEAM
evapotranspiration, and GLDAS/GRACE groundwater storage.

Extracted from the source `imputed_gw_level.csv` by taking the **observed** target
column (`gw_level_m_asl_original`) — not the pre-imputed or pre-feature-engineered
columns — plus the four raw predictors. The skill computes its own lags, rolling
features, and imputation from this raw input.

## Cleaning applied when building this file
- **Duplicate well-date rows collapsed.** The source table (a spatial join) had 32
  duplicate (well, date) rows on a few 2019 dates. Predictor values were identical
  within every duplicate group; only `gw_level_m_asl` differed trivially in ~24
  rows. These were collapsed by mean per (well, date), yielding 53,690 unique rows.
  The skill's `config.yaml` keeps `domain.duplicate_strategy: error` so any *future*
  un-reviewed data with duplicates still fails safe.

## Regenerating
Re-extract from `input_data_lt_lv_karst.zip` → `imputed_gw_level.csv`, select
`well_no, date, gw_level_m_asl_original(→gw_level_m_asl)` and the four predictors,
collapse duplicate (well, date) rows by mean, write Parquet.
