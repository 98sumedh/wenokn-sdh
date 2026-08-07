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
synthetic-data caveat.**

12. **[I]** Which model provides the best forecasting skill for the infectious
    (diarrheal) disease target?
    → `results_comprehensive_v7/INF_footprint_model_summary.json` →
    `best_overall`; expect it compared against the naive baseline.
13. **[I]** Which health service areas would need targeted interventions to
    offset climate influence, and where would interventions be useless?
    → exclusion/connectivity analysis; expect well-connected-with-climate-signal
    (intervene) vs. weak-allocation/diluted-signal (useless), mapped to HSAs.
14. **[D]** How much does adding climate features improve the forecast, per model?
    → `INF_footprint_climate_contribution_analysis.csv`; expect per-model answer
    (some gain, some lose).
15. **[D]** Which features are most important in the ML models?
    → `results_ml_v7/INF_footprint_feature_importance_rankings.csv`.
16. **[D]** How robust are the results to the gravity-model / allocation-weight
    choices?
    → `sensitivity/analysis_gravity_sensitivity_v7`, `analysis_weight_sensitivity_v7`.

## 6. Routing traps (should NOT cross datasets) ✅

Included to catch the failure mode fixed in `2abe0b0`.

17. **[D]** Rivers near El Paso. → USA `rivers`/`stream-gauges`, NOT
    `transboundary-rivers`.
18. **[D]** Wells in Lombardy. → Italian Po skills, NOT the transboundary skills.
19. **[D]** Hospitals in Amman. → `jordan-health-geography`, NOT
    `jordan-climate-health-models`.
20. **[D]** Which model best predicts disease in Amman? →
    `jordan-climate-health-models`, NOT the geography skill.

---

_Seeded from Vytautas's two queries, Ilya's four (two groundwater "why", two
Jordan), plus derived coverage and routing traps. Replace/extend with Vytautas's
official list when it arrives, and with the questions Ilya collects in Jordan._
