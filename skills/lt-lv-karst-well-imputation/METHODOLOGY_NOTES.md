# Methodology Notes and Notebook Refactor

## Preserved from the notebook

The skill preserves the following study-specific design choices:

- the seven named LT-LV karst wells;
- the default 2003-2023 analysis interval;
- precipitation, temperature, actual evapotranspiration, and GLDAS groundwater storage as predictors;
- 30-, 60-, 90-, 180-, 270-, and 360-day lag concepts;
- 60- and 90-day rolling windows;
- seasonal and non-seasonal manually selected feature sets;
- per-well Extra Trees models;
- contiguous masked intervals to imitate monitoring gaps;
- VIF, feature importance, SHAP, noise diagnostics, and stacked time-series visualization;
- the known `LT_35996` exclusion beginning on 1 June 2022.

## Corrections and safeguards

### Calendar-day lags

The notebook used `groupby().shift(30)` and described it as a 30-day lag. That is correct only when every calendar day is represented. The skill first creates a complete daily grid, making the lag meaning explicit.

### Per-well signal cleaning

The notebook calculated a global jump threshold and included a difference across well boundaries. The skill calculates the threshold separately for each well.

The notebook's forward-or-backward rule can remove a spike and its neighboring valid values. The default skill mode removes only an isolated point that differs sharply from both neighbors. The original broader behavior remains available as `adjacent_jump`.

### Known corruption

Hard-coded data deletion is replaced by a configuration list. Every removed source value is exported to `signal_cleaning_events`.

### LT_220 ambiguity

The notebook comment referred to data from 2014 onward, while the commented code used the opposite inequality. No LT_220 interval is activated in the skill. It must be specified after independent review.

### Synthetic 31 December anchor

The notebook inserted the historical mean of 31 December groundwater levels at the 2023 endpoint. This creates a synthetic target and can influence training. The skill reconstructs trailing dates directly and leaves the anchor disabled by default.

### Grouped climate calculations

The notebook's freezing persistence and some climatologies were calculated across the combined dataframe. The skill calculates them separately for each well.

### Dimensionally clearer precipitation anomaly

The notebook subtracted a daily precipitation mean from a 90-day precipitation sum. The skill compares the 90-day sum with its own long-window mean.

### Model selection

The notebook placed `GridSearchCV(cv=3)` inside repeated random interval masking. The inner GridSearchCV folds were not time-aware and were repeated for each mask. The skill evaluates the complete hyperparameter grid directly under the same contiguous-gap validation design.

### Independent evaluation

The notebook created an `eval_fraction` mask but did not calculate a final score on it. The skill reserves an outer masked-gap set before model selection and reports its metrics separately.

### Preprocessing leakage

Predictor medians are fitted on each training sample and then applied to its validation or evaluation sample. They are not calculated from the full well record during evaluation.

### Scaling

The notebook standardized predictors before Extra Trees. Tree ensembles do not require scaling. The skill uses raw predictor units for fitting, which also makes tree thresholds and SHAP feature values easier to interpret.

### Target provenance

The notebook overwrote the target in copied dataframes. The skill retains distinct original, cleaned, prediction, and final-imputed columns.

### Noise metric

The notebook calculated a coefficient of variation on a z-scored series whose mean is approximately zero. The skill removes that unstable quantity and retains standardized first-difference dispersion.

## Remaining scientific limitations

- Exogenous predictors may themselves contain product error and spatial-scale mismatch.
- Tree dispersion is not a calibrated uncertainty interval.
- Masked-gap validation cannot reproduce every real missingness mechanism.
- A model that performs well on internal gaps may still be unreliable for trailing extrapolation.
- SHAP and native feature importance describe statistical influence, not causal recharge processes.
