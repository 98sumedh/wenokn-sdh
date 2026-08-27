---
name: lt-lv-karst-well-imputation
description: Reconstruct missing daily groundwater levels for seven specified wells in the Lithuania-Latvia gypsum-karst transboundary area using hydroclimatic predictors, repeated contiguous-gap validation, Extra Trees, uncertainty estimates, VIF, SHAP, signal-noise diagnostics, and explicit domain-quality masks.
---

# LT-LV Karst Well Imputation Skill

## Use this skill when

Use this skill only for daily groundwater-level reconstruction focused on the following LT-LV karst monitoring wells:

- `LT_35994`
- `LT_35995`
- `LT_35996`
- `LV_12225`
- `LV_22606`
- `LV_22610`
- `LT_220`

Typical tasks include:

- reconstruct internal gaps in daily groundwater-level records;
- replace values removed as isolated spikes or known corrupted intervals;
- compare the notebook's seasonal and non-seasonal predictor sets;
- evaluate imputation under masked contiguous intervals;
- quantify Extra Trees prediction dispersion;
- explain groundwater-level reconstruction using feature importance, VIF, and SHAP;
- test whether noisier well signals correspond to weaker masked-gap performance.

Do not use this specialized skill as a general groundwater-network model. Use the broader complete groundwater-analysis skill for raw-data assembly, spatial joins, area-wide analytics, monthly modeling, or reference-well analysis.

## Required agent procedure

1. Confirm that the input represents daily or near-daily records and contains the required six columns listed in `INPUTS.md`.
2. Confirm groundwater-level units and vertical datum. The expected target is groundwater elevation in metres above sea level.
3. Review the seven configured well IDs. Remove a well from the YAML rather than silently substituting another identifier.
4. Review every `known_bad_intervals` rule against the current data revision.
5. Do not activate the optional LT_220 correction without resolving the contradictory comment and commented code in the source notebook.
6. Keep `regularize_daily_grid: true` when using day-based lags.
7. Run it. The input data and `config.yaml` are **bundled in this skill** — the
   config already points at the bundled daily table, so no `--input` is needed.
   All paths resolve **from the repository root** (the agent's working directory):

```bash
python skills/lt-lv-karst-well-imputation/src/lt_lv_karst_imputation.py \
  --config skills/lt-lv-karst-well-imputation/config.yaml \
  --output-dir <your_temp_dir>
```

   Bundled data: `skills/lt-lv-karst-well-imputation/data/processed_daily_groundwater.parquet`
   — the seven wells' observed daily groundwater elevation (`gw_level_m_asl`) with
   the four hydroclimatic predictors, 2003–2023. Do **not** use a bare `data/...`
   path; there is no top-level `data/` directory on the server.

8. Read `run_manifest.json` first.
9. Inspect `signal_cleaning_events.csv` before accepting removed target values.
10. Use `outer_r2`, `outer_mae`, and `outer_rmse` for the strongest performance statement. Inner CV is for model selection.
11. Inspect `prediction_scope` in the final series. Treat `leading_extrapolation` and `trailing_extrapolation` more cautiously than `internal_gap`.
12. Preserve the original, cleaned, model-predicted, and final imputed columns in all downstream work.
13. Report unresolved dates and predictor-coverage limitations explicitly.

## Methodological boundaries

The final model is fitted to all accepted historical observations and then applied across the historical daily grid. Therefore, the result is a retrospective reconstruction, not a strict operational forecast.

The tree-to-tree standard deviation is a model-dispersion diagnostic. It is not a calibrated prediction interval and does not include input, structural, or measurement uncertainty.

SHAP explains the fitted model, not physical causality. Lagged temperature, groundwater storage, precipitation accumulation, and seasonal features can be strongly correlated.

## Domain assumptions

The default configuration reproduces the source notebook's study interval of 1 January 2003 through 31 December 2023 and masks `LT_35996` from 1 June 2022 onward as known corruption.

The notebook's synthetic 31 December endpoint is retained only as a disabled legacy option. It should remain disabled unless a transparent sensitivity experiment specifically requires it.

## Package files

- `PIPELINE.md` — complete algorithm and data flow;
- `DESCRIPTION.md` — scientific purpose and interpretation;
- `INPUTS.md` — data and configuration contract;
- `OUTPUTS.md` — output tables, fields, and interpretation;
- `METHODOLOGY_NOTES.md` — changes made while refactoring the notebook;
- `INTEGRATION.md` — connection to the broader groundwater-analysis skill;
- `VALIDATION.md` — synthetic end-to-end and SHAP/figure validation;
- `PACKAGE_CONTENTS.md` — package inventory;
- `config.example.yaml` — complete well-specific configuration;
- `src/lt_lv_karst_imputation.py` — executable pipeline and CLI;
- `tests/smoke_test.py` — synthetic end-to-end test;
- `notebooks/5_imputation.ipynb` — original source notebook.
