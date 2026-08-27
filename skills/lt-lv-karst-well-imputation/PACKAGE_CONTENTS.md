# Package Contents

```text
lt_lv_karst_imputation_skill/
├── SKILL.md
├── DESCRIPTION.md
├── PIPELINE.md
├── INPUTS.md
├── OUTPUTS.md
├── METHODOLOGY_NOTES.md
├── INTEGRATION.md
├── PACKAGE_CONTENTS.md
├── VALIDATION.md
├── README.md
├── config.example.yaml
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── lt_lv_karst_imputation.py
├── tests/
│   └── smoke_test.py
└── notebooks/
    └── 5_imputation.ipynb
```

## Executable entry point

```bash
python src/lt_lv_karst_imputation.py \
  --input data/processed_daily_groundwater.csv \
  --config config.example.yaml \
  --output-dir results
```

## Validation

`tests/smoke_test.py` creates synthetic daily data for all seven wells and checks:

- well filtering and daily-grid creation;
- internal missing intervals;
- isolated-spike removal;
- a known-corruption trailing interval;
- seasonal/non-seasonal model selection;
- repeated blocked-gap validation;
- outer holdout evaluation;
- internal and trailing imputation;
- output manifests and tables.
