# Description

## Purpose

This skill reconstructs missing daily groundwater-level values for seven monitoring wells in the Lithuania-Latvia gypsum-karst transboundary area. It was extracted from `5_imputation.ipynb` and converted from an exploratory notebook into a reproducible command-line pipeline with explicit input, quality-control, validation, and output contracts.

The model relates groundwater elevation to precipitation, temperature, actual evapotranspiration, groundwater storage, lagged hydroclimatic states, accumulated precipitation, and seasonal timing. A separate Extra Trees model is selected and fitted for each well.

## Scientific rationale

Groundwater levels in karst aquifers may respond rapidly to recharge while also reflecting longer aquifer-storage memory. The predictor design therefore combines:

- recent precipitation accumulation;
- temperature at 30- to 360-day lags;
- groundwater-storage values at 90- to 360-day lags;
- current groundwater storage;
- optional seasonal phase and precipitation climatology.

Two feature sets reproduce the notebook comparison:

- `with_seasonal` includes seasonal phase and mean monthly precipitation;
- `no_seasonal` excludes those explicit seasonal terms.

## Evaluation concept

The workflow intentionally masks contiguous target intervals rather than isolated random points. This better represents the task of reconstructing monitoring gaps.

For each well:

1. an outer set of contiguous intervals is withheld from model selection;
2. repeated inner contiguous masks compare feature sets and hyperparameters;
3. the selected specification is evaluated on the untouched outer intervals;
4. the final model is fitted to all accepted observations;
5. missing and quality-rejected dates are reconstructed where predictor coverage is sufficient.

## Interpretation

The most defensible performance indicators are the outer masked-gap metrics. Inner repeated-CV metrics describe model-selection stability.

Internal-gap reconstruction is generally closer to interpolation. Predictions before the first accepted observation or after the last accepted observation are labeled as extrapolation.

The imputed series should be used together with the quality and source columns, never as an unlabeled replacement of the original observations.
