# Data provenance — Jordan climate-health model results

## Source
Outputs of the **Jordan HSA optimization / climate-health modeling pipeline**
(`Jordan-hsa-optimization_v2`), run configuration:

- **NETWORK** = `INF` (infectious; disease focus = diarrheal)
- **HSA_MODE** = `footprint`
- **BOUNDARY_VERSION** = `v7`
- Run date: 2026-07-15 (pipeline steps 1–6), HSA delineation 2026-07-13.

## ⚠️ Synthetic data
The disease inputs are the **SYNMODINF** synthetic network — sparse, artificial
patient/visit data used to validate the pipeline machinery. These results are
**not real epidemiology** and must never be reported as clinical or public-health
fact about Jordan. They demonstrate that the modeling and forecasting pipeline
works end-to-end.

## What was bundled vs. excluded
The full run is ~1.6 GB. Only small, queryable **summaries** are bundled here
(62 files, <1 MB):

- Bundled: model-comparison tables (`*_comparison_*.csv`, `*_summary.json`),
  feature-importance rankings, per-analysis sensitivity CSV/JSON, all
  `textresults/*.md` written summaries, and the 19-HSA boundary GeoJSON.
- **Excluded on purpose:** multi-MB train/val/test data splits
  (`*_train_data.csv`, `*_val_data.csv`, `*_test_data.csv`), the raw
  per-HSA climate downloads (`DRIVE_CLIMATE_BY_HSA_DOWNLOAD_*`), and the 27 PNG
  figures. Regenerate any of these from the pipeline if needed.

## Regenerating
Run the pipeline in `Jordan-hsa-optimization_v2`:
```
PYTHONHASHSEED=42 python run_pipeline.py --network INF --hsa-mode footprint \
    --boundary-version v7
```
Note: steps require Google Earth Engine climate extraction (manual GEE notebooks)
before the local modeling steps — see that repo's `PIPELINE_GUIDE.md`.
