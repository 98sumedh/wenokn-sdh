"""Synthetic end-to-end test for the LT-LV karst imputation skill."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lt_lv_karst_imputation import DEFAULT_CONFIG, DEFAULT_WELLS, run_pipeline  # noqa: E402


def make_synthetic_data() -> pd.DataFrame:
    rng = np.random.default_rng(2026)
    dates = pd.date_range("2018-01-01", "2021-12-31", freq="D")
    day = np.arange(len(dates))
    precipitation = rng.gamma(shape=0.8, scale=2.2, size=len(dates))
    temperature = 8 + 11 * np.sin(2 * np.pi * (dates.dayofyear - 100) / 365.25) + rng.normal(0, 1.5, len(dates))
    aet = np.clip(1.5 + 1.2 * np.sin(2 * np.pi * (dates.dayofyear - 100) / 365.25) + rng.normal(0, 0.2, len(dates)), 0, None)
    gws = 35 + 7 * np.sin(2 * np.pi * (dates.dayofyear + 30) / 365.25) + 0.003 * day + rng.normal(0, 0.5, len(dates))

    frames = []
    for index, well in enumerate(DEFAULT_WELLS):
        level = (
            55
            + index * 2.5
            + 0.11 * gws
            - 0.025 * temperature
            + 0.004 * pd.Series(precipitation).rolling(90, min_periods=1).sum().to_numpy()
            + 0.4 * np.sin(2 * np.pi * dates.dayofyear / 365.25)
            + rng.normal(0, 0.12 + index * 0.01, len(dates))
        )
        frame = pd.DataFrame(
            {
                "well_no": well,
                "date": dates,
                "gw_level_m_asl": level,
                "precipitation_mm_eobs": precipitation + rng.normal(0, 0.1, len(dates)),
                "temperature_C_eobs": temperature + rng.normal(0, 0.1, len(dates)),
                "actual_evapotranspiration_mm_gleam": aet,
                "gws_mm_tavg_gldas": gws + rng.normal(0, 0.1, len(dates)),
                "country": well[:2],
            }
        )
        # Realistic internal gaps.
        frame.loc[(frame["date"] >= "2019-03-10") & (frame["date"] <= "2019-04-10"), "gw_level_m_asl"] = np.nan
        frame.loc[(frame["date"] >= "2020-08-15") & (frame["date"] <= "2020-09-20"), "gw_level_m_asl"] = np.nan
        # A single isolated spike to test cleaning.
        if index == 0:
            frame.loc[frame["date"] == "2020-01-15", "gw_level_m_asl"] += 8
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    workdir = ROOT / "tests" / "_smoke_output"
    workdir.mkdir(parents=True, exist_ok=True)
    input_path = workdir / "synthetic_daily_wells.csv"
    make_synthetic_data().to_csv(input_path, index=False)

    config = copy.deepcopy(DEFAULT_CONFIG)
    config["domain"]["date_start"] = "2018-01-01"
    config["domain"]["date_end"] = "2021-12-31"
    config["domain"]["known_bad_intervals"] = [
        {
            "well_no": "LT_35996",
            "start": "2021-09-01",
            "end": None,
            "reason": "synthetic_known_corruption",
        }
    ]
    config["cleaning"]["spike_detection"]["quantile"] = 0.995
    config["model"]["minimum_observed_values"] = 500
    config["model"]["outer_evaluation_fraction"] = 0.08
    config["model"]["inner_cv_fraction"] = 0.08
    config["model"]["inner_cv_repeats"] = 2
    config["model"]["minimum_mask_days"] = 7
    config["model"]["maximum_mask_days"] = 25
    config["model"]["parameter_grid"] = {
        "n_estimators": [30],
        "max_depth": [None],
        "min_samples_split": [2],
        "min_samples_leaf": [1],
        "max_features": [1.0],
    }
    config["model"]["save_models"] = False
    config["diagnostics"]["calculate_shap"] = False
    config["diagnostics"]["create_figures"] = False
    config["output"]["write_parquet"] = False

    manifest = run_pipeline(input_path, workdir / "results", config)
    assert set(manifest["wells_modeled"]) == set(DEFAULT_WELLS)

    summary = pd.read_csv(workdir / "results" / "tables" / "well_model_summary.csv")
    imputed = pd.read_csv(workdir / "results" / "tables" / "imputed_groundwater_levels.csv")
    events = pd.read_csv(workdir / "results" / "tables" / "signal_cleaning_events.csv")

    assert len(summary) == len(DEFAULT_WELLS)
    assert imputed["is_imputed"].astype(str).str.lower().eq("true").any()
    assert (events["event"] == "spike_removed").any()
    assert (events["event"] == "synthetic_known_corruption").any()
    assert (imputed["prediction_scope"] == "trailing_extrapolation").any()
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
