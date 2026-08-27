# Validation

The package was tested with a synthetic daily dataset covering all seven configured wells.

The test includes:

- a complete daily hydroclimatic predictor record;
- two internal groundwater-level gaps per well;
- one isolated groundwater-level spike;
- one configured trailing corruption interval for `LT_35996`;
- both seasonal and non-seasonal feature sets;
- contiguous inner and outer masked intervals;
- Extra Trees model selection and final reconstruction.

The end-to-end test verifies that:

- all seven wells are modeled;
- the isolated spike is recorded as a cleaning event;
- the domain corruption interval is recorded and reconstructed;
- missing target values receive imputed values where predictors are available;
- trailing extrapolations are labeled explicitly;
- evaluation and output tables are created.

A second execution enabled SHAP and figures and successfully produced:

- per-feature-set SHAP beeswarms;
- a stacked SHAP comparison;
- stacked groundwater-level time series;
- feature-importance comparison;
- noise-versus-performance diagnostics.

Run the included test with:

```bash
python tests/smoke_test.py
```
