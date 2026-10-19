---
name: jordan-climate-health-models
description: >-
  Jordan climate-health MODELING and FORECASTING results: how well models
  predict disease incidence across Health Service Areas (HSAs), which climate
  and temporal drivers matter, and which areas are weakly connected to care.
  Use for Jordan questions about model performance or forecasting skill ("which
  model best predicts diarrheal disease", "does climate improve the forecast"),
  climate-health drivers ("how much does climate contribute", "top features"),
  sensitivity/robustness of the results, or WHERE targeted health interventions
  would help vs. be wasted ("which HSAs need intervention to offset climate",
  "where are interventions useless"). Reads bundled model-comparison tables,
  sensitivity analyses, and written summaries from the SYNMODINF v7 run.
  Jordan-only, MODEL RESULTS only; for facility locations, boundaries, and
  population use jordan-health-geography. Not groundwater, rivers, or US data.
---

# Jordan Climate-Health Models & Forecasting Skill

This skill exposes the **results of the Jordan climate-health modeling pipeline**:
the models that predict disease incidence per Health Service Area (HSA), how much
climate adds over a naive baseline, which drivers matter, the robustness of the
findings under sensitivity tests, and where the population is poorly connected to
care. It answers the "which model is best" and "where should we intervene"
questions that the geography skill cannot.

> **Synthetic-data caveat — state this in every answer.** These results come from
> the **SYNMODINF** network: *synthetic, sparse* disease data used to validate the
> machinery, **not** real epidemiology. Report *how the modeling behaves*, never
> as clinical or public-health fact about Jordan.

## What is bundled

Curated summary outputs from the `INF / footprint / v7` run (the multi-MB
train/val/test splits and the raw climate rasters are intentionally **not**
bundled — see `data/DATA_NOTES.md`). Everything here is small and queryable.

```
data/
  modeling/                          weekly climate-health model results
    results_comprehensive_v7/        main comparison across models × feature sets
    results_ml_v7/                   ML model comparison + feature-importance rankings
    results_improved_v7/             tuned models
    results_parsimonious_v7/         minimal-feature models
    results_anomalies_v7/            anomaly-feature-set models
    daily_models_v7/                 DLNM daily models: distributed-lag climate-disease effects
  sensitivity/                       9 robustness analyses (each in its own dir)
    analysis_climate_exclusion_v7/   effect of removing climate features
    analysis_exclusion_v7/           excluded / poorly-connected population
    analysis_gravity_sensitivity_v7/ sensitivity to the gravity-model parameters
    analysis_weight_sensitivity_v7/  sensitivity to allocation weights
    analysis_extreme_events_v7/      extreme-event (heat/rain) analysis
    analysis_spatial_autocorrelation_v7/
    analysis_spatial_comparison_v7/  HSA vs governorate spatial unit
    analysis_variance_decomposition_v7/
    analysis_climate_heterogeneity_v7/
  textresults/                       *.md written summaries of every stage — READ THESE FIRST
  INF_footprint_hsas_v7.geojson      the 19 HSA boundaries, for mapping answers
```

## Data location — IMPORTANT

All files for this skill live under **`skills/jordan-climate-health-models/data/`**,
resolved **from the repository root** (the agent's working directory). Every path
in this document is written relative to that folder, so **prepend the base**:

```python
BASE = "skills/jordan-climate-health-models/data"   # from the repo root
```

Do **not** use a bare `data/...` path — there is no top-level `data/` directory,
and it will raise FileNotFoundError. Always build paths as
`os.path.join(BASE, ...)` (e.g. `f"{BASE}/modeling/results_comprehensive_v7/..."`).

## How to answer — read the summary, then query the table

Every stage wrote a human-readable markdown summary in `textresults/`. **Read the
relevant one first** for the narrative, then open the underlying CSV/JSON for exact
numbers. This is faster and more reliable than re-deriving from raw tables.

### Query type 1 — "Which model best forecasts disease X?"

**Authoritative source for "the best model" — always use this first.** For the
single best model overall, read
`modeling/results_comprehensive_v7/INF_footprint_model_summary.json` and report
its `best_overall` (model + feature set + `test_r2`/`test_rmse`). Do **not** pick
a different winner from the `results_improved_v7/` or `results_ml_v7/` files or by
switching the ranking metric — those exist for deeper comparison, and mixing them
gives inconsistent "best model" answers. Rank by **test R²** unless the user asks
for another metric. (Current headline: XGBoost on `ar_climate_temporal`.)

Supporting files, for when the user wants to compare beyond the single winner:

- `INF_footprint_model_comparison_pivot.csv` — full matrix, **rows = feature sets,
  columns = models**, cells = test R². Use to compare any model/feature-set.
- `results_ml_v7/INF_footprint_model_comparison_summary.csv` — richer metrics
  (RMSE, MAE, R², MAPE, Poisson deviance) for the ML models.
- `results_improved_v7/` — tuned variants; report only if asked to compare tuning.

```python
import json, pandas as pd, os
BASE = "skills/jordan-climate-health-models/data"   # from the repo root
base = os.path.join(BASE, "modeling/results_comprehensive_v7")
s = json.load(open(os.path.join(base, "INF_footprint_model_summary.json")))
bo = s["best_overall"]
print(f"Best: {bo['model']} on '{bo['feature_set']}' "
      f"(test R²={bo['test_r2']:.3f}, RMSE={bo['test_rmse']:.2f}); "
      f"beats last-week baseline by {bo['improvement_over_baseline']:.3f} R².")
# Full matrix if the user wants to compare specific models:
pivot = pd.read_csv(os.path.join(base, "INF_footprint_model_comparison_pivot.csv"))
```

Always compare against the **baseline** rows (`last_week`, `seasonal_mean`,
`mean_baseline`): a model is only "skillful" if it beats the naive predictor.

### Query type 2 — "How much does climate actually contribute?"

`modeling/results_comprehensive_v7/INF_footprint_climate_contribution_analysis.csv`
gives, per model, `ar_only_r2` vs `ar_climate_r2` and the absolute/relative gain.
The signal is model-dependent — some models gain from climate, others lose — so
report per model, and cross-check with
`sensitivity/analysis_climate_exclusion_v7/` which re-tests by removing climate.

### Query type 2b — "Daily / lagged climate effects (DLNM)"

For *daily* distributed-lag effects (how climate on a given day affects disease
over the following days), use `modeling/daily_models_v7/`:

- `trackA_screening.csv` — which daily climate variables matter (main effect
  `F_main`/`p_main` and interaction `F_int`/`p_int`). Lower p = stronger signal;
  e.g. dewpoint, max/mean temperature, and surface soil moisture screen in.
- `trackB_horizon_results.csv` — forecast R² by horizon (1–28 days) across
  Seasonal / AR+Seasonal / +Climate specs, with `ΔR² (climate)` — the daily
  analogue of the weekly climate-contribution story.

### Query type 3 — "Where would targeted intervention help vs. be useless?"

Use the exclusion / connectivity analysis, not the models:

- `textresults/INF_footprint_exclusion_analysis_report.md` — narrative: share of
  population by allocation-probability class and by distance class, and a
  Well-Connected vs Poorly-Connected split.
- `sensitivity/analysis_exclusion_v7/INF_footprint_exclusion_hotspots.csv` —
  lat/lon hotspots of excluded population (candidates for intervention).
- `sensitivity/analysis_exclusion_v7/INF_footprint_connectivity_comparison.csv`.

**Interpretation the report itself makes:** where allocation probability is very
weak and distance to care is large, the disease-to-facility assignment is
uncertain and the climate signal is *diluted* — so a climate-targeted intervention
keyed to modeled incidence there is on shaky ground ("useless"), whereas
well-connected HSAs with a clear climate contribution are where it can bite. Map
hotspots by joining to `INF_footprint_hsas_v7.geojson`.

## Scope / routing

- **This skill:** Jordan model performance, forecasting skill, climate drivers,
  sensitivity, intervention targeting. Network = INF (infectious/diarrheal),
  mode = footprint, boundary = v7.
- **Not this skill:** facility locations, admin boundaries, raw population →
  `jordan-health-geography`. Groundwater / rivers / US energy → their own skills.
- The **19 HSAs** here are the same footprint-v7 boundaries the geography skill
  maps; you can join model results to them by HSA id.

## Archive loader (verification only)

The Jordan results also ship as one archive. **Do not answer questions from it yet**
— answers still come from the files described above. Run this only when asked to
load or check the archive. Run it from the repository root:

```python
import sys; sys.path.insert(0, ".")
from scripts.zip_loader import load_archive
bundle = load_archive("skills/jordan-climate-health-models/data/archives")
print(bundle.describe())
```