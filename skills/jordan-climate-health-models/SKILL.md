---
name: jordan-climate-health-models
description: >-
  Jordan climate-health MODELING results for 10 synthetic pipeline runs
  (SYNMODINF diarrheal and SYNMODNCD hypertension networks x 5 HSA modes:
  footprint, distance, fewest, governorate_fewest, governorate_tau_coverage;
  boundary v7). Use for Jordan questions about model performance ("which model
  best predicts diarrheal disease"), WHICH COMBINATION / HSA MODE / NETWORK
  GIVES THE BEST RESULTS ("compare the runs", "best HSA mode for
  hypertension"), whether climate improves the forecast, top drivers,
  sensitivity/robustness, or WHERE targeted interventions would help vs. be
  wasted. Reads the loaded run archives (model comparisons, sensitivity
  analyses, written summaries). Jordan-only, MODEL RESULTS only; for facility
  locations, boundaries, and population use jordan-health-geography. Not
  groundwater, rivers, or US data.
---

# Jordan Climate-Health Models & Forecasting Skill

This skill exposes the **results of the Jordan climate-health modeling pipeline**
for every run that has been packaged and loaded: which models predict disease
incidence per Health Service Area (HSA), how much climate adds over a naive
baseline, which drivers matter, how robust the findings are, where the
population is poorly connected to care, and **which run (network x HSA mode)
gives the best results**.

> **Synthetic-data caveat — state this in every answer.** Every run here uses
> a **synthetic** network (SYNMODINF or SYNMODNCD): sparse simulated disease
> data used to validate the machinery, **not** real epidemiology. Report *how
> the modeling behaves*, never clinical or public-health fact about Jordan.

## The runs

Each run is one zip archive with `manifest.json` at its root, in
`skills/jordan-climate-health-models/data/archives/`. A run is identified by
network, HSA mode, boundary version and disease:

| Network | Disease | HSA modes (all boundary v7) |
|---|---|---|
| SYNMODINF (infectious) | Diarrheal diseases | footprint, distance, fewest, governorate_fewest, governorate_tau_coverage |
| SYNMODNCD (non-communicable) | Hypertension | footprint, distance, fewest, governorate_fewest, governorate_tau_coverage |

The number of HSAs differs by run (17 to 45); it is in `b.manifest["meta"]["n_hsas"]`.

## Step 1 — always load the runs first

Run code from the **repository root** (the agent's working directory). Never
build file names by hand from the network/mode labels; ask the loaded bundle
for them through the manifest.

```python
import sys, json, pandas as pd
sys.path.insert(0, ".")
from scripts.zip_loader import load_archives

runs = load_archives("skills/jordan-climate-health-models/data/archives")
# runs: {"SYNMODINF_footprint_diarrheal_diseases_v7": Bundle, ...}

def pick(network=None, hsa_mode=None):
    """Runs matching the question. hsa_mode must match exactly
    ('fewest' is not 'governorate_fewest')."""
    out = {}
    for key, b in runs.items():
        i = b.identity()
        if network and i["network"] != network:
            continue
        if hsa_mode and i["hsa_mode"] != hsa_mode:
            continue
        out[key] = b
    return out

def one(b, key, pattern):
    """The single file matching pattern under a manifest folder entry."""
    hits = b.glob(key, pattern)
    if len(hits) != 1:
        raise FileNotFoundError(f"{b.run_key}: {len(hits)} files match {key}/{pattern}")
    return hits[0]
```

Manifest entries you will use (all in the `model` section):

| Entry | Kind | Holds |
|---|---|---|
| `model_results` | folder | weekly model results (`results_comprehensive_v7/`, `results_ml_v7/`, `results_improved_v7/`, `results_parsimonious_v7/`, `results_anomalies_v7/`) and daily DLNM results (`daily_models_v7/`) |
| `sensitivity` | folder | 9 robustness analyses, one sub-folder each |
| `textresults` | folder | written `*.md` summaries of every stage — read these for the narrative |
| `hsa_boundaries` | file | the run's HSA polygons (GeoJSON), for mapping answers |

Which runs to use: if the user names a network ("diarrheal" = SYNMODINF,
"hypertension" = SYNMODNCD) or an HSA mode, use `pick(...)`. If they ask a
single-run question without naming one, use **SYNMODINF / footprint** and say
so, then offer to compare the other runs.

## Query type 0 — "Which combination gives the best results?"

**Metric (fixed — do not switch it):** the run's best model **test R²**, read
from `best_overall` in `*_model_summary.json`. Always also report
`improvement_over_baseline` (gain in R² over the last-week naive predictor):
a high R² that barely beats the baseline is a weak result, and say so.

**Rank each network separately.** SYNMODINF and SYNMODNCD model different
diseases with different count scales, so their R² values are not comparable.
Never name one winner across both networks; give one per network. Mention
that the HSA count differs by mode, so runs are not on identical spatial units.

```python
rows = []
for key, b in runs.items():
    s = json.load(open(one(b, "model_results", "*_model_summary.json")))
    bo, i = s["best_overall"], b.identity()
    rows.append({"network": i["network"], "hsa_mode": i["hsa_mode"],
                 "disease": b.manifest["model"]["disease_focus_input"],
                 "n_hsas": b.manifest["meta"].get("n_hsas"),
                 "best_model": bo["model"], "feature_set": bo["feature_set"],
                 "test_r2": bo["test_r2"], "test_rmse": bo["test_rmse"],
                 "gain_over_baseline": bo["improvement_over_baseline"]})
table = pd.DataFrame(rows).sort_values(["network", "test_r2"], ascending=[True, False])
print(table.to_string(index=False))
for net, g in table.groupby("network"):
    w = g.iloc[0]
    print(f"{net}: best = {w.hsa_mode} ({w.best_model} on '{w.feature_set}', "
          f"test R²={w.test_r2:.3f}, +{w.gain_over_baseline:.3f} over last-week baseline)")
```

If the user asks for a different metric (RMSE, gain over baseline), rank by it
but say that test R² is the default metric. If the user asks "which HSA mode is
best overall", give each network's ranking and note whether the same mode wins
in both.

## Query type 1 — "Which model best forecasts disease X?" (within a run)

Authoritative source for a run's best model: `best_overall` in
`model_results / *_model_summary.json` (as above). Do **not** pick a different
winner from `results_improved_v7/` or `results_ml_v7/`, or by switching the
metric; that gives inconsistent answers. Rank by **test R²** unless asked.

Supporting files, for comparing beyond the single winner:

- `*_model_comparison_pivot.csv` — rows = feature sets, columns = models,
  cells = test R². Baseline columns (`last_week`, `seasonal_mean`,
  `mean_baseline`) are filled only on their own rows.
- `*_model_comparison_summary.csv` (in `results_ml_v7/`) — RMSE, MAE, R², MAPE,
  Poisson deviance for the ML models.
- `*_feature_importance_rankings.csv` (in `results_ml_v7/`) — top drivers.

```python
b = runs["SYNMODINF_footprint_diarrheal_diseases_v7"]
pivot = pd.read_csv(one(b, "model_results", "*_model_comparison_pivot.csv"))
```

A model is only "skillful" if it beats the naive baselines.

## Query type 2 — "How much does climate actually contribute?"

`*_climate_contribution_analysis.csv` (in `results_comprehensive_v7/`) gives, per
model, `ar_only_r2` vs `ar_climate_r2` and the absolute / relative gain. The
signal is model-dependent (some models gain from climate, others lose), so
report per model. Cross-check with the `analysis_climate_exclusion_v7/` folder
under `sensitivity`. Across runs, note that in several SYNMODNCD runs the best
feature set is `ar_only` — climate adds nothing there.

```python
cc = pd.read_csv(one(b, "model_results", "*_climate_contribution_analysis.csv"))
```

### Query type 2b — daily / lagged climate effects (DLNM)

Under `model_results`, `daily_models_v7/`:

- `trackA_screening.csv` — which daily climate variables matter (`F_main` /
  `p_main` main effect, `F_int` / `p_int` interaction). Lower p = stronger signal.
- `trackB_horizon_results.csv` — forecast R² by horizon (1–28 days) across
  Seasonal / AR+Seasonal / +Climate specs, with `ΔR² (climate)`.

```python
hz = pd.read_csv(one(b, "model_results", "trackB_horizon_results.csv"))
```

## Query type 3 — "Where would targeted intervention help vs. be useless?"

Use the exclusion / connectivity analysis, not the models. Under `textresults`
and `sensitivity`:

- `*_exclusion_analysis_report.md` (textresults) — share of population by
  allocation-probability class and by distance class, and a Well-Connected vs
  Poorly-Connected split.
- `*_exclusion_hotspots.csv` (`analysis_exclusion_v7/`) — lat/lon hotspots of
  excluded population (candidates for intervention).
- `*_connectivity_comparison.csv` (`analysis_exclusion_v7/`).

```python
report = one(b, "textresults", "*_exclusion_analysis_report.md").read_text()
hot = pd.read_csv(one(b, "sensitivity", "*_exclusion_hotspots.csv"))
import geopandas as gpd
hsas = gpd.read_file(b.path("hsa_boundaries"))
```

**Interpretation the report makes:** where allocation probability is very weak
and distance to care is large, the disease-to-facility assignment is uncertain
and the climate signal is *diluted*, so a climate-targeted intervention keyed
to modeled incidence there is on shaky ground ("useless"). Well-connected HSAs
with a clear climate contribution are where it can bite.

## Written summaries

Every stage wrote a markdown summary under `textresults`. Read the relevant one
first for the narrative, then open the CSV/JSON for exact numbers. List them
with `b.glob("textresults", "*.md")`; names include the network and mode, e.g.
`run_climate_health_modeling_<network>_<mode>_v7_results.md`.

## Scope / routing

- **This skill:** Jordan model performance, forecasting skill, comparison of
  runs / HSA modes / networks, climate drivers, sensitivity, intervention
  targeting.
- **Not this skill:** facility locations, admin boundaries, raw population →
  `jordan-health-geography`. Groundwater / rivers / US energy → their own skills.

## Checking the archives

To check that every archive loads and matches its manifest:

```bash
python scripts/zip_loader.py skills/jordan-climate-health-models/data/archives
```
