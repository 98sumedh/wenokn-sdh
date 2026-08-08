# Benchmark query set — before/after skill evaluation

Purpose: run the **same** questions against the agent with and without the new
skills, and (separately) across models, so we can attribute any difference. Hold
one variable at a time: skills on/off with the model fixed, or models swapped
with skills fixed — never both at once.

How to use:
- **Baseline ("before")** = the `main` branch (no groundwater-ML / Jordan-models
  / rivers skills).
- **Treatment ("after")** = the branch with the new skills.
- Record, per query: did it route to the intended skill? is the answer correct?
  latency. Keep the model constant across a before/after pair.
- Provenance of each query is tagged: **[V]** from Vytautas, **[I]** from Ilya,
  **[D]** derived here.

Status legend: ✅ answerable on data already bundled · 🟡 answerable once that
skill's data is wired · 🔴 blocked (data not in repo yet).

---

## 1. Transboundary groundwater — descriptive (bundled data) ✅

These run on `transboundary-monitoring-points` + `-groundwater-timeseries` +
`groundwater-regional-comparison`, all already on `main`.

1. **[V]** In Lithuania, how does unconfined groundwater depth vary spatially?
   → LT wells, `confinement == False`, map `gw_level_from_ground`.
   *Caveat:* `confinement` is nullable, so "unconfined" = known-False, excluding
   blanks. Expect the answer to state that.
2. **[V]** Compare the groundwater fluctuation magnitude in the LT-LV karst region
   to the rest of the transboundary countries.
   → per-well `dtw_std` of `gw_level_from_ground`, `aquifer_karst == True` in
   LT/LV vs. others. The comparison skill's helper already does this join.
3. **[D]** Which transboundary region has the deepest water table on average?
   → mean depth-to-water per region; expect the "common currency" comparison.
4. **[D]** Which region's water table is most variable, and which is depleting
   fastest in recent years?
   → per-region std + trend; default to all eight regions (comparison skill).
5. **[D]** Show wells in the PL-UA border area tapping a karst aquifer.
   → `aquifer_karst == True`, PL/UA, mapped.
6. **[D]** Are there wells where the water table sits below the borehole bottom,
   or a screen deeper than the borehole?
   → routes to `groundwater-anomaly-checks`; expect flags-for-investigation.

## 2. Transboundary groundwater — "why" / drivers ✅

7. **[I]** Explain why the PL-UA border area differs from the LV-LT area in
   groundwater dynamics.
   → comparison skill with climate + GRACE layer; expect aridity/recharge/aquifer
   reasoning, not just numbers.
8. **[I]** Which transboundary area is most unique in groundwater dynamics,
   especially in the last years?
   → cross-region comparison; expect a named region + justification.

## 3. Transboundary groundwater — imputation 🔴

9. **[I]** For a PL-UA well with missing GRACE values, impute them.
   → BLOCKED until Vytautas's imputation code lands and the imputation skill is
   built. Keep here so the "after" run can show it becoming answerable.

## 4. Rivers / surface water 🟡

10. **[D]** Show the river network in the LT-LV border area.
    → `transboundary-rivers`; 🟡 until EU-Hydro is downloaded and built.
11. **[D]** Which LT-LV wells are within 1 km of a river?
    → cross-dataset: rivers × monitoring points; 🟡 same dependency.

## 5. Jordan climate-health models ✅ (new skill, curated outputs bundled)

Run on `jordan-climate-health-models`. **All answers must carry the
synthetic-data caveat.** Expanded for Ilya's demo (~Aug 21); grouped by theme,
each grounded in a bundled file with the finding it should surface. All results
are for the **INF (infectious/diarrheal)** network, footprint mode, v7.

### 5a · Model selection & forecasting skill

12. **[I]** Which model provides the best forecasting skill for the diarrheal
    disease target?
    → `results_comprehensive_v7/INF_footprint_model_summary.json`. Expect
    **XGBoost on the `ar_climate_temporal` feature set (test R² ≈ 0.78)**, beating
    the last-week baseline (R² ≈ 0.69).
13. **[D]** How much better is the best model than just predicting last week's
    cases?
    → same file, `improvement_over_baseline` (≈ 0.086 R²). Tests that the agent
    anchors "skill" to the naive baseline, not the raw R².
14. **[D]** Compare the models on the AR-plus-climate feature set — which wins and
    by how much?
    → `INF_footprint_model_comparison_pivot.csv` (rows = feature sets, cols =
    models). Expect a like-for-like comparison row.
15. **[D]** Do the tuned/"improved" models beat the comprehensive ones?
    → `results_improved_v7/` vs `results_comprehensive_v7/`. Cross-set comparison.

### 5b · Do climate signals actually help? (the honest-negative story)

16. **[D]** How much does adding climate features improve the forecast, per model?
    → `INF_footprint_climate_contribution_analysis.csv`. Expect **model-dependent:
    XGBoost gains, but ridge/RF/GBM lose** — climate is not uniformly helpful.
17. **[D]** In a variance decomposition, how much of disease variance does climate
    explain on its own versus the autoregressive signal?
    → `textresults/INF_footprint_supplement_table_variance_decomposition.md`.
    Expect **AR alone ≈ 73%, climate alone ≈ 0%** — a clean "past cases dominate"
    result worth showing.
18. **[D]** Do extreme-weather indicators predict disease better than climate
    means?
    → `textresults/INF_footprint_extreme_event_summary.md`. Expect **extremes
    marginally edge means, but both add ~0 over AR+seasonal.**
19. **[D]** Are climate–disease relationships stronger in well-connected HSAs than
    poorly-connected ones?
    → `textresults/INF_footprint_climate_connectivity_report.md`. Expect the
    **counter-intuitive result** (low-connectivity group shows higher R²) — good
    discussion point about allocation uncertainty.

### 5c · Spatial design (why HSAs at all)

20. **[D]** Does modeling at the HSA level beat governorate- or country-level?
    → `textresults/INF_footprint_spatial_unit_summary.md`. Expect **HSA R² ≈ 0.75
    while governorate/country collapse to negative R²** — the headline argument
    for HSAs.
21. **[D]** Are HSAs climatically coherent units, or is there large climate
    variation within them?
    → `textresults/INF_footprint_heterogeneity_report.md`. Expect the temperature
    **ICC ≈ 0.61** (most variance is between HSAs, so they're reasonably coherent).

### 5d · Allocation, intervention targeting & robustness

22. **[I]** Which health service areas would need targeted interventions to offset
    climate influence, and where would interventions be useless?
    → exclusion/connectivity analysis
    (`textresults/INF_footprint_exclusion_analysis_report.md`,
    `sensitivity/analysis_exclusion_v7/`). Expect: intervene where allocation is
    confident and a climate signal exists; useless where allocation is very weak
    and the signal is diluted (61.6% of population is weak/very-weak). Map hotspots
    to HSAs.
23. **[D]** Which features does the ML model rely on most?
    → `results_ml_v7/INF_footprint_feature_importance_rankings.csv`.
24. **[D]** How sensitive is patient allocation to the gravity-model parameters
    (population weight α and distance decay β)?
    → `sensitivity/analysis_gravity_sensitivity_v7/`. Expect a table showing higher
    β spreads patients across more facilities / lowers concentration.
25. **[D]** If we perturb the allocation weights ±20%, does the HSA solution change?
    → `sensitivity/analysis_weight_sensitivity_v7/`. Expect **near-invariance**
    (mean allocation prob ~0.35 across perturbations) — a robustness selling point.

### 5e · Known gap (surface for the demo)

26. **[D]** Show the same analysis for the non-communicable (NCD) disease network.
    → **Not answerable** — only INF outputs are bundled. Expect the agent to say
    the NCD run isn't available. Flags whether we need to bundle NCD before the demo.

## 6. Routing traps (should NOT cross datasets) ✅

Included to catch the failure mode fixed in `2abe0b0`.

27. **[D]** Rivers near El Paso. → USA `rivers`/`stream-gauges`, NOT
    `transboundary-rivers`.
28. **[D]** Wells in Lombardy. → Italian Po skills, NOT the transboundary skills.
29. **[D]** Hospitals in Amman. → `jordan-health-geography`, NOT
    `jordan-climate-health-models`.
30. **[D]** Which model best predicts disease in Amman? →
    `jordan-climate-health-models`, NOT the geography skill.

---

_Seeded from Vytautas's two queries, Ilya's four (two groundwater "why", two
Jordan), plus derived coverage and routing traps. Replace/extend with Vytautas's
official list when it arrives, and with the questions Ilya collects in Jordan._
