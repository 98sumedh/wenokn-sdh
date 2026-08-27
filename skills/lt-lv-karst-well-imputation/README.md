# LT-LV Karst Groundwater-Level Imputation

Standalone agent skill extracted from `5_imputation.ipynb` for seven monitoring wells in the Lithuania-Latvia karst transboundary area.

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
cp config.example.yaml config.yaml
python src/lt_lv_karst_imputation.py \
  --input /path/to/daily_groundwater.csv \
  --config config.yaml \
  --output-dir results
```

Read `SKILL.md` for agent behavior, `INPUTS.md` and `OUTPUTS.md` for contracts, and `METHODOLOGY_NOTES.md` for differences from the original notebook.
