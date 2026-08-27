# Integration with the Complete Groundwater Analysis Skill

## Role in the wider workflow

This package is a specialized downstream skill. It complements, rather than replaces, `groundwater_analysis_skill`.

```text
Raw groundwater, climate, static and spatial data
                         │
                         ▼
       complete-groundwater-analysis preprocessing
                         │
                         ▼
      model-ready table with validated identifiers,
      dates, units and hydroclimatic predictors
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
 broader monthly network ML   LT-LV daily well imputation
 and transboundary analytics  for the seven karst wells
```

## Recommended handoff

The upstream preprocessing stage should export or derive a daily table containing:

- `well_no`;
- `date`;
- `gw_level_m_asl`;
- `precipitation_mm_eobs`;
- `temperature_C_eobs`;
- `actual_evapotranspiration_mm_gleam`;
- `gws_mm_tavg_gldas`.

If the broader prepared table uses different names, map them in this skill's YAML. Do not rename a groundwater-depth-below-ground variable as groundwater elevation without performing the required elevation conversion.

## When to use each pipeline

Use the complete skill for:

- joining raw source datasets;
- geographic and transboundary-area assignment;
- monthly availability analytics and maps;
- comparison across large monitoring networks;
- reference-well augmentation and clustering.

Use this specialized skill for:

- daily reconstruction of the seven LT-LV karst wells;
- domain-specific LT_35996 quality masking;
- gap-oriented Extra Trees validation;
- detailed well-level imputation diagnostics.

## Combining results

When joining the imputed values back to a broader database, join on `well_no` and `date` and retain all provenance fields. Recommended final fields are:

- original target;
- cleaned target;
- final imputed target;
- `is_imputed`;
- `target_quality_flag`;
- `prediction_scope`;
- prediction standard deviation;
- model feature set and run identifier.

Never replace the network-wide target column without an accompanying imputation flag.
