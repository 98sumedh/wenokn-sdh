"""LT-LV karst transboundary groundwater-level imputation pipeline.

This module is a reusable, agent-oriented refactor of ``5_imputation.ipynb``.
It targets seven monitoring wells in the Lithuania-Latvia gypsum-karst area and
reconstructs missing daily groundwater levels from hydroclimatic predictors.

The implementation preserves the notebook's scientific intent while replacing
several notebook-only shortcuts with explicit and auditable behavior:

* lags are calendar-day lags because each well is regularized to a daily grid;
* signal cleaning is performed separately for each well;
* known corrupted intervals are configuration-driven;
* model selection uses repeated contiguous-gap validation rather than random
  GridSearchCV folds;
* an independent outer masked-gap evaluation is reported;
* synthetic end-of-series anchors are disabled by default;
* original, cleaned, predicted, and final values remain separate columns.

The workflow is intended for retrospective reconstruction. Predictions in
leading or trailing periods are extrapolations and must not be described as
independent operational forecasts.
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import math
import re
import sys
import warnings
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import ParameterGrid

LOGGER = logging.getLogger("lt_lv_karst_imputation")

DEFAULT_WELLS = (
    "LT_35994",
    "LT_35995",
    "LT_35996",
    "LV_12225",
    "LV_22606",
    "LV_22610",
    "LT_220",
)

DEFAULT_FEATURE_SETS: dict[str, list[str]] = {
    "with_seasonal": [
        "precipitation_mm_eobs_rollsum_90d",
        "temperature_C_eobs_lag_30d",
        "temperature_C_eobs_lag_90d",
        "temperature_C_eobs_lag_180d",
        "temperature_C_eobs_lag_270d",
        "temperature_C_eobs_lag_360d",
        "gws_mm_tavg_gldas_lag_90d",
        "gws_mm_tavg_gldas_lag_180d",
        "gws_mm_tavg_gldas_lag_270d",
        "gws_mm_tavg_gldas_lag_360d",
        "gws_mm_tavg_gldas",
        "seasonal_phase",
        "precip_monthly_avg",
    ],
    "no_seasonal": [
        "precipitation_mm_eobs_rollsum_90d",
        "temperature_C_eobs_lag_30d",
        "temperature_C_eobs_lag_90d",
        "temperature_C_eobs_lag_180d",
        "temperature_C_eobs_lag_270d",
        "temperature_C_eobs_lag_360d",
        "gws_mm_tavg_gldas_lag_90d",
        "gws_mm_tavg_gldas_lag_180d",
        "gws_mm_tavg_gldas_lag_270d",
        "gws_mm_tavg_gldas_lag_360d",
        "gws_mm_tavg_gldas",
    ],
}

DEFAULT_CONFIG: dict[str, Any] = {
    "input": {
        "path": None,
    },
    "columns": {
        "id": "well_no",
        "date": "date",
        "target": "gw_level_m_asl",
        "precipitation": "precipitation_mm_eobs",
        "temperature": "temperature_C_eobs",
        "actual_evapotranspiration": "actual_evapotranspiration_mm_gleam",
        "groundwater_storage": "gws_mm_tavg_gldas",
    },
    "domain": {
        "wells": list(DEFAULT_WELLS),
        "date_start": "2003-01-01",
        "date_end": "2023-12-31",
        "frequency": "D",
        "regularize_daily_grid": True,
        "duplicate_strategy": "error",
        "known_bad_intervals": [
            {
                "well_no": "LT_35996",
                "start": "2022-06-01",
                "end": None,
                "reason": "known_corruption",
            }
        ],
    },
    "cleaning": {
        "spike_detection": {
            "enabled": True,
            "mode": "isolated_spike",
            "threshold_method": "quantile",
            "quantile": 0.9995,
            "mad_z": 8.0,
            "minimum_jump_m": 0.0,
        },
        "legacy_dec31_anchor": {
            "enabled": False,
            "date": "2023-12-31",
            "use_for_training": False,
        },
    },
    "features": {
        "predictor_columns": [
            "precipitation_mm_eobs",
            "temperature_C_eobs",
            "actual_evapotranspiration_mm_gleam",
            "gws_mm_tavg_gldas",
        ],
        "lag_days": [30, 60, 90, 180, 270, 360],
        "rolling_days": [60, 90],
        "rolling_sum_columns": [
            "precipitation_mm_eobs",
            "actual_evapotranspiration_mm_gleam",
        ],
        "rolling_min_periods": 1,
        "feature_sets": copy.deepcopy(DEFAULT_FEATURE_SETS),
        "include_auxiliary_features": True,
    },
    "model": {
        "random_state": 42,
        "minimum_observed_values": 365,
        "minimum_feature_ratio": 0.5,
        "outer_evaluation_fraction": 0.20,
        "inner_cv_fraction": 0.20,
        "inner_cv_repeats": 5,
        "minimum_mask_days": 7,
        "maximum_mask_days": 60,
        "maximum_mask_attempts": 3000,
        "parameter_grid": {
            "n_estimators": [100, 200],
            "max_depth": [None, 20],
            "min_samples_split": [2],
            "min_samples_leaf": [1, 2],
            "max_features": [1.0],
        },
        "n_jobs": -1,
        "save_models": True,
        "calculate_prediction_uncertainty": True,
    },
    "diagnostics": {
        "calculate_vif": True,
        "calculate_shap": True,
        "maximum_shap_samples_per_well": 1000,
        "maximum_shap_features": 20,
        "create_figures": True,
        "figure_dpi": 300,
    },
    "output": {
        "write_csv": True,
        "write_parquet": True,
    },
}


@dataclass(slots=True)
class FittedWellModel:
    """Model and preprocessing objects required for deterministic prediction."""

    well_no: str
    feature_set: str
    features: list[str]
    medians: pd.Series
    model: ExtraTreesRegressor
    params: dict[str, Any]


def _deep_merge(base: Mapping[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(base))
    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load YAML configuration and merge it with audited defaults."""
    config = copy.deepcopy(DEFAULT_CONFIG)
    if path is not None:
        with Path(path).open("r", encoding="utf-8") as stream:
            user_config = yaml.safe_load(stream) or {}
        if not isinstance(user_config, Mapping):
            raise ValueError("The YAML root must be a mapping.")
        config = _deep_merge(config, user_config)
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    """Validate high-impact configuration choices before data processing."""
    required_sections = {
        "input",
        "columns",
        "domain",
        "cleaning",
        "features",
        "model",
        "diagnostics",
        "output",
    }
    missing_sections = sorted(required_sections - set(config))
    if missing_sections:
        raise ValueError(f"Missing configuration sections: {missing_sections}")

    duplicate_strategy = config["domain"].get("duplicate_strategy", "error")
    if duplicate_strategy not in {"error", "first", "mean"}:
        raise ValueError("domain.duplicate_strategy must be error, first, or mean.")

    spike_mode = config["cleaning"]["spike_detection"].get("mode")
    if spike_mode not in {"isolated_spike", "adjacent_jump"}:
        raise ValueError(
            "cleaning.spike_detection.mode must be isolated_spike or adjacent_jump."
        )

    threshold_method = config["cleaning"]["spike_detection"].get(
        "threshold_method"
    )
    if threshold_method not in {"quantile", "mad"}:
        raise ValueError(
            "cleaning.spike_detection.threshold_method must be quantile or mad."
        )

    for name in ("outer_evaluation_fraction", "inner_cv_fraction"):
        value = float(config["model"][name])
        if not 0 <= value < 1:
            raise ValueError(f"model.{name} must be in [0, 1).")

    feature_sets = config["features"].get("feature_sets", {})
    if not feature_sets:
        raise ValueError("At least one features.feature_sets entry is required.")


def load_table(path: str | Path) -> pd.DataFrame:
    """Load CSV, zipped CSV, Parquet, Feather, Pickle, or Excel input."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".zip":
        return pd.read_csv(path, compression="zip")
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if suffix in {".feather", ".ftr"}:
        return pd.read_feather(path)
    if suffix in {".pkl", ".pickle"}:
        return pd.read_pickle(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(
        f"Unsupported input format '{suffix}'. Use CSV, ZIP, Parquet, Feather, "
        "Pickle, or Excel."
    )


def _safe_r2(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    y_true_array = np.asarray(y_true, dtype=float)
    if len(y_true_array) < 2 or np.nanstd(y_true_array) == 0:
        return np.nan
    return float(r2_score(y_true_array, y_pred))


def _rmse(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def _slug(text: Any) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")
    return value or "unknown"


def _write_table(
    frame: pd.DataFrame,
    base_path: Path,
    write_csv: bool,
    write_parquet: bool,
    manifest: list[dict[str, Any]],
) -> None:
    """Write a dataframe in requested formats and record actual outputs."""
    if write_csv:
        csv_path = base_path.with_suffix(".csv")
        frame.to_csv(csv_path, index=False)
        manifest.append({"path": str(csv_path), "rows": int(len(frame)), "format": "csv"})

    if write_parquet:
        parquet_path = base_path.with_suffix(".parquet")
        try:
            frame.to_parquet(parquet_path, index=False)
            manifest.append(
                {"path": str(parquet_path), "rows": int(len(frame)), "format": "parquet"}
            )
        except Exception as exc:  # pyarrow/fastparquet may not be installed
            LOGGER.warning("Could not write %s: %s", parquet_path.name, exc)


def _coerce_and_filter_input(
    df: pd.DataFrame, config: Mapping[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    cols = config["columns"]
    domain = config["domain"]
    id_col = cols["id"]
    date_col = cols["date"]
    target_col = cols["target"]
    predictor_cols = list(config["features"]["predictor_columns"])

    required = [id_col, date_col, target_col, *predictor_cols]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Input is missing required columns: {missing}")

    work = df.copy()
    input_rows = len(work)
    work[id_col] = work[id_col].astype(str)
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    invalid_dates = int(work[date_col].isna().sum())
    work = work[work[date_col].notna()].copy()

    wells = [str(well) for well in domain["wells"]]
    work = work[work[id_col].isin(wells)].copy()

    start = pd.Timestamp(domain["date_start"]) if domain.get("date_start") else None
    end = pd.Timestamp(domain["date_end"]) if domain.get("date_end") else None
    if start is not None:
        work = work[work[date_col] >= start]
    if end is not None:
        work = work[work[date_col] <= end]

    numeric_cols = [target_col, *predictor_cols]
    coercion_failures: dict[str, int] = {}
    for column in numeric_cols:
        before_nonnull = int(work[column].notna().sum())
        work[column] = pd.to_numeric(work[column], errors="coerce")
        after_nonnull = int(work[column].notna().sum())
        coercion_failures[column] = before_nonnull - after_nonnull

    duplicate_mask = work.duplicated([id_col, date_col], keep=False)
    duplicate_rows = int(duplicate_mask.sum())
    strategy = domain.get("duplicate_strategy", "error")
    if duplicate_rows:
        if strategy == "error":
            duplicate_preview = work.loc[duplicate_mask, [id_col, date_col]].head(10)
            raise ValueError(
                "Duplicated well-date rows were found. Set domain.duplicate_strategy "
                f"to first or mean to resolve them. Preview:\n{duplicate_preview}"
            )
        if strategy == "first":
            work = work.sort_values([id_col, date_col]).drop_duplicates(
                [id_col, date_col], keep="first"
            )
        elif strategy == "mean":
            numeric_set = set(work.select_dtypes(include=[np.number]).columns)
            aggregations: dict[str, str] = {}
            for column in work.columns:
                if column in {id_col, date_col}:
                    continue
                aggregations[column] = "mean" if column in numeric_set else "first"
            work = work.groupby([id_col, date_col], as_index=False).agg(aggregations)

    work = work.sort_values([id_col, date_col]).reset_index(drop=True)

    report = {
        "input_rows": int(input_rows),
        "invalid_date_rows_removed": invalid_dates,
        "rows_after_well_and_date_filter": int(len(work)),
        "duplicate_rows_detected": duplicate_rows,
        "duplicate_strategy": strategy,
        "numeric_coercion_failures": coercion_failures,
        "requested_wells": wells,
        "present_wells": sorted(work[id_col].unique().tolist()),
        "missing_requested_wells": sorted(set(wells) - set(work[id_col].unique())),
    }
    return work, report


def _regularize_daily_grid(
    df: pd.DataFrame, config: Mapping[str, Any]
) -> pd.DataFrame:
    domain = config["domain"]
    cols = config["columns"]
    id_col = cols["id"]
    date_col = cols["date"]

    if not domain.get("regularize_daily_grid", True):
        return df.copy().sort_values([id_col, date_col]).reset_index(drop=True)

    start_global = pd.Timestamp(domain["date_start"])
    end_global = pd.Timestamp(domain["date_end"])
    frequency = domain.get("frequency", "D")
    predictor_cols = set(config["features"]["predictor_columns"])
    dynamic_cols = predictor_cols | {cols["target"]}

    frames: list[pd.DataFrame] = []
    for well in domain["wells"]:
        group = df[df[id_col] == str(well)].copy().sort_values(date_col)
        grid = pd.DataFrame({date_col: pd.date_range(start_global, end_global, freq=frequency)})
        if group.empty:
            grid[id_col] = str(well)
            for column in df.columns:
                if column not in grid.columns:
                    grid[column] = np.nan
            frames.append(grid[df.columns])
            continue

        merged = grid.merge(group, on=date_col, how="left", validate="one_to_one")
        merged[id_col] = str(well)

        # Preserve only truly static metadata across inserted daily rows. Dynamic
        # hydrometeorological variables are deliberately not interpolated here.
        for column in group.columns:
            if column in {id_col, date_col} or column in dynamic_cols:
                continue
            nonnull_unique = group[column].dropna().nunique()
            if nonnull_unique <= 1:
                merged[column] = merged[column].ffill().bfill()

        frames.append(merged)

    regularized = pd.concat(frames, ignore_index=True, sort=False)
    return regularized.sort_values([id_col, date_col]).reset_index(drop=True)


def _jump_threshold(series: pd.Series, settings: Mapping[str, Any]) -> float:
    differences = series.diff().abs().dropna()
    differences = differences[np.isfinite(differences)]
    if differences.empty:
        return np.inf

    minimum = float(settings.get("minimum_jump_m", 0.0))
    if settings.get("threshold_method") == "quantile":
        threshold = float(differences.quantile(float(settings.get("quantile", 0.9995))))
    else:
        median = float(differences.median())
        mad = float(np.median(np.abs(differences - median)))
        robust_sigma = 1.4826 * mad
        threshold = median + float(settings.get("mad_z", 8.0)) * robust_sigma
    return max(minimum, threshold)


def clean_target_signal(
    df: pd.DataFrame, config: Mapping[str, Any]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create original/clean target columns and apply auditable quality flags."""
    cols = config["columns"]
    id_col, date_col, target_col = cols["id"], cols["date"], cols["target"]
    work = df.copy().sort_values([id_col, date_col]).reset_index(drop=True)

    original_col = f"{target_col}_original"
    cleaned_col = f"{target_col}_cleaned"
    work[original_col] = work[target_col]
    work[cleaned_col] = work[target_col]
    work["target_quality_flag"] = np.where(
        work[original_col].notna(), "observed", "missing_raw"
    )
    work["synthetic_anchor"] = False
    work["training_eligible"] = True

    event_rows: list[dict[str, Any]] = []
    spike_cfg = config["cleaning"]["spike_detection"]
    if spike_cfg.get("enabled", True):
        for well, group in work.groupby(id_col, sort=False):
            series = group.set_index(date_col)[cleaned_col]
            threshold = _jump_threshold(series, spike_cfg)
            previous = series.shift(1)
            following = series.shift(-1)
            left = series - previous
            right = series - following

            if spike_cfg.get("mode") == "isolated_spike":
                spike = (
                    left.abs().gt(threshold)
                    & right.abs().gt(threshold)
                    & np.sign(left).eq(np.sign(right))
                )
            else:  # notebook-compatible, more aggressive adjacent-jump rule
                spike = left.abs().gt(threshold) | right.abs().gt(threshold)

            spike_dates = spike[spike.fillna(False)].index
            mask = (work[id_col] == well) & work[date_col].isin(spike_dates)
            mask &= work[cleaned_col].notna()
            if mask.any():
                for _, row in work.loc[mask, [id_col, date_col, cleaned_col]].iterrows():
                    event_rows.append(
                        {
                            "well_no": row[id_col],
                            "date": row[date_col],
                            "event": "spike_removed",
                            "original_value": row[cleaned_col],
                            "threshold_m": threshold,
                        }
                    )
                work.loc[mask, cleaned_col] = np.nan
                work.loc[mask, "target_quality_flag"] = "spike_removed"

    # Explicit domain corrections override generic spike labels.
    for rule in config["domain"].get("known_bad_intervals", []):
        well = str(rule["well_no"])
        start = pd.Timestamp(rule["start"]) if rule.get("start") else work[date_col].min()
        end = pd.Timestamp(rule["end"]) if rule.get("end") else work[date_col].max()
        mask = (
            (work[id_col] == well)
            & (work[date_col] >= start)
            & (work[date_col] <= end)
        )
        affected = work.loc[mask & work[cleaned_col].notna(), [id_col, date_col, cleaned_col]]
        for _, row in affected.iterrows():
            event_rows.append(
                {
                    "well_no": row[id_col],
                    "date": row[date_col],
                    "event": str(rule.get("reason", "known_corruption")),
                    "original_value": row[cleaned_col],
                    "threshold_m": np.nan,
                }
            )
        work.loc[mask, cleaned_col] = np.nan
        work.loc[mask, "target_quality_flag"] = str(
            rule.get("reason", "known_corruption")
        )

    anchor_cfg = config["cleaning"].get("legacy_dec31_anchor", {})
    if anchor_cfg.get("enabled", False):
        anchor_date = pd.Timestamp(anchor_cfg.get("date", "2023-12-31"))
        for well, group in work.groupby(id_col, sort=False):
            anchor_mask = (work[id_col] == well) & (work[date_col] == anchor_date)
            if not anchor_mask.any() or work.loc[anchor_mask, cleaned_col].notna().any():
                continue
            past_dec31 = group[
                (group[date_col] < anchor_date)
                & (group[date_col].dt.month == 12)
                & (group[date_col].dt.day == 31)
            ][cleaned_col].dropna()
            if past_dec31.empty:
                continue
            value = float(past_dec31.mean())
            work.loc[anchor_mask, cleaned_col] = value
            work.loc[anchor_mask, "target_quality_flag"] = "synthetic_dec31_anchor"
            work.loc[anchor_mask, "synthetic_anchor"] = True
            work.loc[anchor_mask, "training_eligible"] = bool(
                anchor_cfg.get("use_for_training", False)
            )
            event_rows.append(
                {
                    "well_no": well,
                    "date": anchor_date,
                    "event": "synthetic_dec31_anchor",
                    "original_value": np.nan,
                    "threshold_m": np.nan,
                }
            )

    events = pd.DataFrame(
        event_rows,
        columns=["well_no", "date", "event", "original_value", "threshold_m"],
    )
    return work, events


def engineer_features(df: pd.DataFrame, config: Mapping[str, Any]) -> pd.DataFrame:
    """Create calendar-day, rolling, seasonal, anomaly, and climate flags."""
    cols = config["columns"]
    id_col, date_col = cols["id"], cols["date"]
    feature_cfg = config["features"]
    work = df.copy().sort_values([id_col, date_col]).reset_index(drop=True)

    predictor_cols = list(feature_cfg["predictor_columns"])
    for column in predictor_cols:
        work[column] = pd.to_numeric(work[column], errors="coerce")

    lags = [int(value) for value in feature_cfg.get("lag_days", [])]
    windows = [int(value) for value in feature_cfg.get("rolling_days", [])]
    sum_columns = set(feature_cfg.get("rolling_sum_columns", []))
    min_periods_setting = feature_cfg.get("rolling_min_periods", 1)

    for column in predictor_cols:
        grouped = work.groupby(id_col, sort=False)[column]
        for lag in lags:
            work[f"{column}_lag_{lag}d"] = grouped.shift(lag)
        for window in windows:
            if isinstance(min_periods_setting, float) and 0 < min_periods_setting <= 1:
                min_periods = max(1, int(math.ceil(window * min_periods_setting)))
            else:
                min_periods = int(min_periods_setting)
            rolled = grouped.rolling(window=window, min_periods=min_periods)
            if column in sum_columns:
                values = rolled.sum().reset_index(level=0, drop=True)
                work[f"{column}_rollsum_{window}d"] = values
            else:
                values = rolled.mean().reset_index(level=0, drop=True)
                work[f"{column}_rollmean_{window}d"] = values

    day_of_year = work[date_col].dt.dayofyear
    month = work[date_col].dt.month
    work["dayofyear"] = day_of_year
    work["month"] = month
    work["sin_doy"] = np.sin(2 * np.pi * day_of_year / 365.25)
    work["cos_doy"] = np.cos(2 * np.pi * day_of_year / 365.25)
    work["sin_month"] = np.sin(2 * np.pi * month / 12)
    work["cos_month"] = np.cos(2 * np.pi * month / 12)
    work["sin_annual"] = work["sin_doy"]
    work["cos_annual"] = work["cos_doy"]
    work["seasonal_phase"] = np.arctan2(work["sin_doy"], work["cos_doy"])

    if feature_cfg.get("include_auxiliary_features", True):
        precip = cols["precipitation"]
        temp = cols["temperature"]
        gws = cols["groundwater_storage"]

        precip_roll90 = f"{precip}_rollsum_90d"
        if precip_roll90 in work.columns:
            long_mean = (
                work.groupby(id_col, sort=False)[precip_roll90]
                .rolling(window=365, min_periods=180)
                .mean()
                .reset_index(level=0, drop=True)
            )
            work["precip_anomaly"] = work[precip_roll90] - long_mean
            work["drought_flag"] = work["precip_anomaly"] < 0

        if gws in work.columns:
            climatology = work.groupby([id_col, month])[gws].transform("mean")
            work["gws_monthly_mean"] = climatology
            work["gws_monthly_anomaly"] = work[gws] - climatology
            lag30_name = f"{gws}_lag_30d"
            if lag30_name in work.columns:
                work["gws_delta_30d"] = work[gws] - work[lag30_name]
                q90 = work.groupby(id_col)["gws_delta_30d"].transform(
                    lambda values: values.quantile(0.9)
                )
                work["gws_recharge_event"] = work["gws_delta_30d"] > q90

        if temp in work.columns:
            below_zero_fraction = (
                work.groupby(id_col, sort=False)[temp]
                .rolling(window=30, min_periods=30)
                .apply(lambda values: float(np.mean(values < 0)), raw=True)
                .reset_index(level=0, drop=True)
            )
            work["below_zero_rolling_30d"] = below_zero_fraction
            work["permafrost_flag"] = below_zero_fraction >= 0.8

        monthly_columns = {
            temp: "temp_monthly_avg",
            precip: "precip_monthly_avg",
            gws: "gws_monthly_avg",
        }
        for source, destination in monthly_columns.items():
            if source in work.columns:
                work[destination] = work.groupby([id_col, month])[source].transform("mean")

    return work


def _indices_to_intervals(
    frame: pd.DataFrame, indices: Sequence[int], date_col: str
) -> list[tuple[pd.Timestamp, pd.Timestamp, int]]:
    if not indices:
        return []
    dates = frame.loc[list(indices), date_col].sort_values()
    if dates.empty:
        return []
    gap = dates.diff().dt.days.fillna(1)
    segment = (gap > 1).cumsum()
    intervals: list[tuple[pd.Timestamp, pd.Timestamp, int]] = []
    for _, values in dates.groupby(segment):
        intervals.append((values.min(), values.max(), int(len(values))))
    return intervals


def generate_contiguous_mask(
    frame: pd.DataFrame,
    eligible_indices: Sequence[int],
    target_fraction: float,
    min_days: int,
    max_days: int,
    max_attempts: int,
    rng: np.random.Generator,
    date_col: str,
) -> list[int]:
    """Select non-overlapping calendar intervals that mimic missing target blocks."""
    eligible = frame.loc[list(eligible_indices), [date_col]].sort_values(date_col)
    if eligible.empty or target_fraction <= 0:
        return []

    target_count = max(1, int(round(target_fraction * len(eligible))))
    eligible_dates = eligible[date_col]
    selected: set[int] = set()
    attempts = 0
    eligible_index_array = eligible.index.to_numpy()

    while len(selected) < target_count and attempts < max_attempts:
        start_idx = int(rng.choice(eligible_index_array))
        start_date = frame.at[start_idx, date_col]
        interval_days = int(rng.integers(min_days, max_days + 1))
        end_date = start_date + pd.Timedelta(days=interval_days - 1)
        candidate = eligible.index[
            (eligible_dates >= start_date) & (eligible_dates <= end_date)
        ].tolist()
        if candidate and not selected.intersection(candidate):
            selected.update(candidate)
        attempts += 1

    if len(selected) < target_count:
        LOGGER.warning(
            "Contiguous-mask generator selected %s of %s requested observations.",
            len(selected),
            target_count,
        )

    return sorted(selected)


def _prepare_train_test(
    frame: pd.DataFrame,
    train_indices: Sequence[int],
    test_indices: Sequence[int],
    feature_candidates: Sequence[str],
    target_col: str,
    minimum_feature_ratio: float,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.Series, list[str]] | None:
    features = [feature for feature in feature_candidates if feature in frame.columns]
    if len(features) < 2:
        return None

    train = frame.loc[list(train_indices)].copy()
    test = frame.loc[list(test_indices)].copy()
    required = max(1, int(math.ceil(len(features) * minimum_feature_ratio)))
    train = train[train[features].notna().sum(axis=1) >= required]
    test = test[test[features].notna().sum(axis=1) >= required]
    train = train[train[target_col].notna()]
    test = test[test[target_col].notna()]
    if train.empty or test.empty:
        return None

    usable_features = [feature for feature in features if train[feature].notna().any()]
    if len(usable_features) < 2:
        return None

    medians = train[usable_features].median()
    medians = medians.fillna(0.0)
    x_train = train[usable_features].fillna(medians)
    x_test = test[usable_features].fillna(medians)
    y_train = train[target_col]
    y_test = test[target_col]
    return x_train, y_train, x_test, y_test, medians, usable_features


def _fit_model(
    frame: pd.DataFrame,
    train_indices: Sequence[int],
    feature_candidates: Sequence[str],
    target_col: str,
    minimum_feature_ratio: float,
    params: Mapping[str, Any],
    random_state: int,
    n_jobs: int,
) -> FittedWellModel | None:
    features = [feature for feature in feature_candidates if feature in frame.columns]
    if len(features) < 2:
        return None
    train = frame.loc[list(train_indices)].copy()
    required = max(1, int(math.ceil(len(features) * minimum_feature_ratio)))
    train = train[train[features].notna().sum(axis=1) >= required]
    train = train[train[target_col].notna()]
    if train.empty:
        return None
    usable_features = [feature for feature in features if train[feature].notna().any()]
    if len(usable_features) < 2:
        return None
    medians = train[usable_features].median().fillna(0.0)
    x_train = train[usable_features].fillna(medians)
    model = ExtraTreesRegressor(
        random_state=random_state,
        n_jobs=n_jobs,
        **dict(params),
    )
    model.fit(x_train, train[target_col])
    return FittedWellModel(
        well_no="",
        feature_set="",
        features=usable_features,
        medians=medians,
        model=model,
        params=dict(params),
    )


def _predict_with_uncertainty(
    fitted: FittedWellModel,
    frame: pd.DataFrame,
    minimum_feature_ratio: float,
    calculate_uncertainty: bool,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    features = fitted.features
    required = max(1, int(math.ceil(len(features) * minimum_feature_ratio)))
    enough = frame[features].notna().sum(axis=1) >= required
    predictions = pd.Series(np.nan, index=frame.index, dtype=float)
    uncertainty = pd.Series(np.nan, index=frame.index, dtype=float)
    if not enough.any():
        return predictions, uncertainty, enough

    matrix = frame.loc[enough, features].fillna(fitted.medians)
    predictions.loc[enough] = fitted.model.predict(matrix)
    if calculate_uncertainty and hasattr(fitted.model, "estimators_"):
        tree_predictions = np.vstack(
            [estimator.predict(matrix.to_numpy()) for estimator in fitted.model.estimators_]
        )
        uncertainty.loc[enough] = np.std(tree_predictions, axis=0, ddof=1)
    return predictions, uncertainty, enough


def _compute_vif(matrix: pd.DataFrame) -> pd.DataFrame:
    """Compute VIF without requiring statsmodels."""
    if matrix.shape[1] < 2 or matrix.empty:
        return pd.DataFrame(columns=["feature", "vif"])
    values = matrix.to_numpy(dtype=float)
    std = np.nanstd(values, axis=0)
    keep = std > 0
    matrix = matrix.loc[:, keep]
    values = matrix.to_numpy(dtype=float)
    if matrix.shape[1] < 2:
        return pd.DataFrame({"feature": matrix.columns, "vif": [1.0] * matrix.shape[1]})

    values = (values - np.mean(values, axis=0)) / np.std(values, axis=0)
    rows: list[dict[str, Any]] = []
    for index, feature in enumerate(matrix.columns):
        y = values[:, index]
        x = np.delete(values, index, axis=1)
        x = np.column_stack([np.ones(len(x)), x])
        try:
            coefficients, *_ = np.linalg.lstsq(x, y, rcond=None)
            fitted = x @ coefficients
            residual_ss = float(np.sum((y - fitted) ** 2))
            total_ss = float(np.sum((y - np.mean(y)) ** 2))
            r_squared = 1.0 - residual_ss / total_ss if total_ss > 0 else 0.0
            vif = np.inf if r_squared >= 1 - 1e-12 else 1.0 / (1.0 - r_squared)
        except np.linalg.LinAlgError:
            vif = np.inf
        rows.append({"feature": feature, "vif": float(vif)})
    return pd.DataFrame(rows)


def _calculate_noise_metrics(
    frame: pd.DataFrame, id_col: str, date_col: str, cleaned_col: str
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for well, group in frame.groupby(id_col, sort=False):
        values = group.sort_values(date_col)[cleaned_col]
        mean = float(values.mean()) if values.notna().any() else np.nan
        std = float(values.std()) if values.notna().sum() > 1 else np.nan
        if np.isfinite(std) and std > 0:
            zscore = (values - mean) / std
            first_diff = zscore.diff()
            std_first_diff = float(first_diff.std())
            median_diff = float(first_diff.median())
            mad_first_diff = float(np.nanmedian(np.abs(first_diff - median_diff)))
        else:
            std_first_diff = np.nan
            mad_first_diff = np.nan
        rows.append(
            {
                "well_no": well,
                "n_clean_observed": int(values.notna().sum()),
                "target_mean_m_asl": mean,
                "target_std_m": std,
                "std_first_diff_z": std_first_diff,
                "mad_first_diff_z": mad_first_diff,
            }
        )
    return pd.DataFrame(rows)


def _create_timeseries_figure(
    series: pd.DataFrame,
    config: Mapping[str, Any],
    output_path: Path,
) -> None:
    cols = config["columns"]
    id_col, date_col, target_col = cols["id"], cols["date"], cols["target"]
    original_col = f"{target_col}_original"
    cleaned_col = f"{target_col}_cleaned"
    final_col = f"{target_col}_imputed"
    wells = [well for well in config["domain"]["wells"] if well in set(series[id_col])]
    if not wells:
        return

    fig, axes = plt.subplots(len(wells), 1, figsize=(11.7, 2.2 * len(wells)), sharex=True)
    if len(wells) == 1:
        axes = [axes]
    for index, (axis, well) in enumerate(zip(axes, wells)):
        group = series[series[id_col] == well].sort_values(date_col)
        observed = group[cleaned_col].notna()
        imputed = group[cleaned_col].isna() & group[final_col].notna()
        removed = group[original_col].notna() & group[cleaned_col].isna()
        axis.plot(group.loc[observed, date_col], group.loc[observed, cleaned_col], linewidth=1.2, label="Observed")
        axis.scatter(group.loc[imputed, date_col], group.loc[imputed, final_col], s=4, label="Imputed")
        if removed.any():
            axis.scatter(group.loc[removed, date_col], group.loc[removed, original_col], s=8, marker="x", label="Removed")
        axis.set_title(f"({chr(97 + index)}) Well {well}", loc="left")
        axis.grid(True, alpha=0.3)
    axes[-1].set_xlabel("Date")
    fig.supylabel("Groundwater level (m ASL)")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=3)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(output_path, dpi=int(config["diagnostics"]["figure_dpi"]), bbox_inches="tight")
    plt.close(fig)


def _create_feature_importance_figure(
    feature_importance: pd.DataFrame,
    output_path: Path,
    dpi: int,
) -> None:
    if feature_importance.empty:
        return
    aggregates = (
        feature_importance.groupby(["feature_set", "feature"], as_index=False)
        .agg(mean_importance=("importance", "mean"), std_importance=("importance", "std"))
    )
    feature_sets = aggregates["feature_set"].unique().tolist()
    fig, axes = plt.subplots(len(feature_sets), 1, figsize=(12, max(4, 4 * len(feature_sets))))
    if len(feature_sets) == 1:
        axes = [axes]
    for index, (axis, feature_set) in enumerate(zip(axes, feature_sets)):
        group = aggregates[aggregates["feature_set"] == feature_set].sort_values(
            "mean_importance", ascending=False
        )
        axis.bar(
            np.arange(len(group)),
            group["mean_importance"],
            yerr=group["std_importance"].fillna(0),
            capsize=3,
        )
        axis.set_xticks(np.arange(len(group)))
        axis.set_xticklabels(group["feature"], rotation=45, ha="right")
        axis.set_ylabel("Mean importance")
        axis.set_title(f"({chr(97 + index)}) {feature_set}", loc="left")
        axis.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def _create_noise_performance_figure(
    table: pd.DataFrame, output_path: Path, dpi: int
) -> None:
    valid = table[["std_first_diff_z", "outer_r2"]].dropna()
    if len(valid) < 2:
        return
    fig, axis = plt.subplots(figsize=(7, 5))
    axis.scatter(valid["std_first_diff_z"], valid["outer_r2"], s=45)
    if valid["std_first_diff_z"].nunique() > 1:
        coefficients = np.polyfit(valid["std_first_diff_z"], valid["outer_r2"], 1)
        x_line = np.linspace(valid["std_first_diff_z"].min(), valid["std_first_diff_z"].max(), 100)
        axis.plot(x_line, coefficients[0] * x_line + coefficients[1], linewidth=1.5)
    axis.set_xlabel("Groundwater-level noise (SD of standardized first differences)")
    axis.set_ylabel("Outer masked-gap R²")
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def _create_shap_outputs(
    shap_records: list[dict[str, Any]],
    output_dir: Path,
    max_display: int,
    dpi: int,
) -> list[str]:
    if not shap_records:
        return []
    try:
        import shap
    except Exception as exc:
        LOGGER.warning("SHAP outputs skipped because shap could not be imported: %s", exc)
        return []

    created: list[str] = []
    panel_paths: list[Path] = []
    for feature_set in sorted({record["feature_set"] for record in shap_records}):
        records = [record for record in shap_records if record["feature_set"] == feature_set]
        common_features = records[0]["features"]
        records = [record for record in records if record["features"] == common_features]
        if not records:
            continue
        shap_matrix = np.vstack([record["shap_values"] for record in records])
        feature_frame = pd.concat([record["feature_values"] for record in records], ignore_index=True)
        plt.figure()
        shap.summary_plot(
            shap_matrix,
            features=feature_frame,
            feature_names=common_features,
            max_display=max_display,
            show=False,
        )
        figure = plt.gcf()
        if figure.axes:
            figure.axes[0].set_title(feature_set)
        path = output_dir / f"shap_beeswarm_{_slug(feature_set)}.png"
        figure.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(figure)
        panel_paths.append(path)
        created.append(str(path))

    if panel_paths:
        images = [plt.imread(path) for path in panel_paths]
        fig, axes = plt.subplots(len(images), 1, figsize=(12, 6 * len(images)))
        if len(images) == 1:
            axes = [axes]
        for index, (axis, image) in enumerate(zip(axes, images)):
            axis.imshow(image)
            axis.axis("off")
            axis.text(0.01, 0.99, f"({chr(97 + index)})", transform=axis.transAxes, va="top", fontweight="bold")
        fig.tight_layout()
        stacked_path = output_dir / "shap_beeswarm_stacked.png"
        fig.savefig(stacked_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        created.append(str(stacked_path))
    return created


def run_pipeline(
    input_path: str | Path,
    output_dir: str | Path,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Execute the complete specialized imputation workflow."""
    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    models_dir = output_dir / "models"
    shap_dir = output_dir / "shap"
    for directory in (output_dir, tables_dir, figures_dir, models_dir, shap_dir):
        directory.mkdir(parents=True, exist_ok=True)

    cols = config["columns"]
    id_col, date_col, target_col = cols["id"], cols["date"], cols["target"]
    original_col = f"{target_col}_original"
    cleaned_col = f"{target_col}_cleaned"
    predicted_col = f"{target_col}_model_prediction"
    uncertainty_col = f"{target_col}_prediction_std"
    final_col = f"{target_col}_imputed"

    source = load_table(input_path)
    filtered, validation_report = _coerce_and_filter_input(source, config)
    daily = _regularize_daily_grid(filtered, config)
    cleaned, cleaning_events = clean_target_signal(daily, config)
    featured = engineer_features(cleaned, config)

    model_cfg = config["model"]
    diagnostic_cfg = config["diagnostics"]
    minimum_observed = int(model_cfg["minimum_observed_values"])
    minimum_feature_ratio = float(model_cfg["minimum_feature_ratio"])
    seed = int(model_cfg["random_state"])
    parameter_grid = list(ParameterGrid(model_cfg["parameter_grid"]))
    feature_sets: Mapping[str, Sequence[str]] = config["features"]["feature_sets"]

    summary_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    cv_interval_rows: list[dict[str, Any]] = []
    outer_prediction_frames: list[pd.DataFrame] = []
    series_frames: list[pd.DataFrame] = []
    feature_importance_rows: list[dict[str, Any]] = []
    vif_rows: list[dict[str, Any]] = []
    shap_importance_rows: list[dict[str, Any]] = []
    shap_value_rows: list[dict[str, Any]] = []
    shap_records: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []

    for well in config["domain"]["wells"]:
        well = str(well)
        group = featured[featured[id_col] == well].copy().sort_values(date_col)
        if group.empty:
            skipped_rows.append({"well_no": well, "reason": "well_not_present"})
            continue

        observed_mask = group[cleaned_col].notna() & group["training_eligible"].fillna(True)
        observed_indices = group.index[observed_mask].tolist()
        if len(observed_indices) < minimum_observed:
            skipped_rows.append(
                {
                    "well_no": well,
                    "reason": "insufficient_observed_values",
                    "n_observed": len(observed_indices),
                }
            )
            continue

        well_seed = seed + zlib.crc32(well.encode("utf-8"))
        outer_rng = np.random.default_rng(well_seed)
        outer_indices = generate_contiguous_mask(
            group,
            observed_indices,
            float(model_cfg["outer_evaluation_fraction"]),
            int(model_cfg["minimum_mask_days"]),
            int(model_cfg["maximum_mask_days"]),
            int(model_cfg["maximum_mask_attempts"]),
            outer_rng,
            date_col,
        )
        selection_indices = [index for index in observed_indices if index not in set(outer_indices)]
        if len(selection_indices) < max(20, minimum_observed // 2):
            skipped_rows.append(
                {
                    "well_no": well,
                    "reason": "insufficient_selection_training_values_after_outer_mask",
                    "n_observed": len(observed_indices),
                    "n_outer": len(outer_indices),
                }
            )
            continue

        cv_masks: list[list[int]] = []
        for repeat in range(int(model_cfg["inner_cv_repeats"])):
            rng = np.random.default_rng(well_seed + 10_000 + repeat)
            mask = generate_contiguous_mask(
                group,
                selection_indices,
                float(model_cfg["inner_cv_fraction"]),
                int(model_cfg["minimum_mask_days"]),
                int(model_cfg["maximum_mask_days"]),
                int(model_cfg["maximum_mask_attempts"]),
                rng,
                date_col,
            )
            cv_masks.append(mask)
            for interval_no, (start, end, n_rows) in enumerate(
                _indices_to_intervals(group, mask, date_col), start=1
            ):
                cv_interval_rows.append(
                    {
                        "well_no": well,
                        "repeat": repeat,
                        "interval_no": interval_no,
                        "start_date": start,
                        "end_date": end,
                        "n_observed_values": n_rows,
                    }
                )

        best: dict[str, Any] | None = None
        for feature_set_name, requested_features in feature_sets.items():
            feature_candidates = [feature for feature in requested_features if feature in group.columns]
            if len(feature_candidates) < 2:
                continue
            for params in parameter_grid:
                repeat_metrics: list[dict[str, float]] = []
                for repeat, cv_test_indices in enumerate(cv_masks):
                    cv_train_indices = [
                        index for index in selection_indices if index not in set(cv_test_indices)
                    ]
                    prepared = _prepare_train_test(
                        group,
                        cv_train_indices,
                        cv_test_indices,
                        feature_candidates,
                        cleaned_col,
                        minimum_feature_ratio,
                    )
                    if prepared is None:
                        continue
                    x_train, y_train, x_test, y_test, _, usable_features = prepared
                    model = ExtraTreesRegressor(
                        random_state=well_seed + repeat,
                        n_jobs=int(model_cfg["n_jobs"]),
                        **params,
                    )
                    model.fit(x_train, y_train)
                    predictions = model.predict(x_test)
                    repeat_metrics.append(
                        {
                            "r2": _safe_r2(y_test, predictions),
                            "mae": float(mean_absolute_error(y_test, predictions)),
                            "rmse": _rmse(y_test, predictions),
                            "n_train": float(len(y_train)),
                            "n_test": float(len(y_test)),
                            "n_features": float(len(usable_features)),
                        }
                    )

                if not repeat_metrics:
                    continue
                metrics_frame = pd.DataFrame(repeat_metrics)
                mean_r2 = float(metrics_frame["r2"].mean())
                mean_rmse = float(metrics_frame["rmse"].mean())
                record = {
                    "well_no": well,
                    "feature_set": feature_set_name,
                    "params": json.dumps(params, sort_keys=True),
                    "cv_r2_mean": mean_r2,
                    "cv_r2_std": float(metrics_frame["r2"].std(ddof=0)),
                    "cv_mae_mean": float(metrics_frame["mae"].mean()),
                    "cv_mae_std": float(metrics_frame["mae"].std(ddof=0)),
                    "cv_rmse_mean": mean_rmse,
                    "cv_rmse_std": float(metrics_frame["rmse"].std(ddof=0)),
                    "valid_repeats": int(len(metrics_frame)),
                    "mean_n_train": float(metrics_frame["n_train"].mean()),
                    "mean_n_test": float(metrics_frame["n_test"].mean()),
                    "mean_n_features": float(metrics_frame["n_features"].mean()),
                }
                candidate_rows.append(record)
                selection_key = (
                    -np.inf if not np.isfinite(mean_r2) else mean_r2,
                    -mean_rmse,
                )
                if best is None or selection_key > best["selection_key"]:
                    best = {
                        "selection_key": selection_key,
                        "feature_set": feature_set_name,
                        "features": feature_candidates,
                        "params": params,
                        "metrics": record,
                    }

        if best is None:
            skipped_rows.append({"well_no": well, "reason": "no_valid_candidate_model"})
            continue

        # Independent outer masked-gap evaluation.
        outer_fitted = _fit_model(
            group,
            selection_indices,
            best["features"],
            cleaned_col,
            minimum_feature_ratio,
            best["params"],
            well_seed + 50_000,
            int(model_cfg["n_jobs"]),
        )
        outer_r2 = outer_mae = outer_rmse = np.nan
        outer_n = 0
        if outer_fitted is not None and outer_indices:
            outer_predictions, outer_std, enough = _predict_with_uncertainty(
                outer_fitted,
                group.loc[outer_indices],
                minimum_feature_ratio,
                bool(model_cfg["calculate_prediction_uncertainty"]),
            )
            outer_frame = group.loc[outer_indices, [id_col, date_col, cleaned_col]].copy()
            outer_frame["prediction"] = outer_predictions
            outer_frame["prediction_std"] = outer_std
            outer_frame["feature_set"] = best["feature_set"]
            outer_frame["params"] = json.dumps(best["params"], sort_keys=True)
            valid = outer_frame[cleaned_col].notna() & outer_frame["prediction"].notna()
            outer_n = int(valid.sum())
            if outer_n:
                outer_r2 = _safe_r2(
                    outer_frame.loc[valid, cleaned_col], outer_frame.loc[valid, "prediction"]
                )
                outer_mae = float(
                    mean_absolute_error(
                        outer_frame.loc[valid, cleaned_col],
                        outer_frame.loc[valid, "prediction"],
                    )
                )
                outer_rmse = _rmse(
                    outer_frame.loc[valid, cleaned_col],
                    outer_frame.loc[valid, "prediction"],
                )
            outer_prediction_frames.append(outer_frame)

        final_fitted = _fit_model(
            group,
            observed_indices,
            best["features"],
            cleaned_col,
            minimum_feature_ratio,
            best["params"],
            well_seed + 60_000,
            int(model_cfg["n_jobs"]),
        )
        if final_fitted is None:
            skipped_rows.append({"well_no": well, "reason": "final_model_fit_failed"})
            continue
        final_fitted.well_no = well
        final_fitted.feature_set = best["feature_set"]

        predictions, prediction_std, enough = _predict_with_uncertainty(
            final_fitted,
            group,
            minimum_feature_ratio,
            bool(model_cfg["calculate_prediction_uncertainty"]),
        )
        group[predicted_col] = predictions
        group[uncertainty_col] = prediction_std
        group[final_col] = group[cleaned_col].where(group[cleaned_col].notna(), predictions)
        group["is_imputed"] = group[cleaned_col].isna() & group[final_col].notna()
        group["imputation_feature_set"] = best["feature_set"]
        group["imputation_params"] = json.dumps(best["params"], sort_keys=True)

        clean_dates = group.loc[group[cleaned_col].notna(), date_col]
        first_observed = clean_dates.min()
        last_observed = clean_dates.max()
        group["prediction_scope"] = "not_imputed"
        internal = group["is_imputed"] & (group[date_col] >= first_observed) & (group[date_col] <= last_observed)
        leading = group["is_imputed"] & (group[date_col] < first_observed)
        trailing = group["is_imputed"] & (group[date_col] > last_observed)
        group.loc[internal, "prediction_scope"] = "internal_gap"
        group.loc[leading, "prediction_scope"] = "leading_extrapolation"
        group.loc[trailing, "prediction_scope"] = "trailing_extrapolation"
        group.loc[group[cleaned_col].isna() & group[final_col].isna(), "prediction_scope"] = "unresolved"

        group["value_source"] = "observed_cleaned"
        group.loc[group["is_imputed"], "value_source"] = "model_imputed"
        group.loc[group[final_col].isna(), "value_source"] = "unresolved"
        group.loc[group["synthetic_anchor"], "value_source"] = "synthetic_anchor"
        series_frames.append(group)

        for feature, importance in zip(
            final_fitted.features, final_fitted.model.feature_importances_
        ):
            feature_importance_rows.append(
                {
                    "well_no": well,
                    "feature_set": best["feature_set"],
                    "feature": feature,
                    "importance": float(importance),
                }
            )

        final_train = group.loc[observed_indices, final_fitted.features].fillna(
            final_fitted.medians
        )
        if diagnostic_cfg.get("calculate_vif", True):
            vif_frame = _compute_vif(final_train)
            if not vif_frame.empty:
                vif_frame["well_no"] = well
                vif_frame["feature_set"] = best["feature_set"]
                vif_rows.extend(vif_frame.to_dict("records"))

        if diagnostic_cfg.get("calculate_shap", True):
            try:
                import shap

                sample_n = min(
                    len(final_train),
                    int(diagnostic_cfg["maximum_shap_samples_per_well"]),
                )
                sample = final_train.sample(n=sample_n, random_state=well_seed)
                explainer = shap.TreeExplainer(final_fitted.model)
                values = explainer.shap_values(sample)
                values = np.asarray(values)
                mean_abs = np.abs(values).mean(axis=0)
                for feature, importance in zip(final_fitted.features, mean_abs):
                    shap_importance_rows.append(
                        {
                            "well_no": well,
                            "feature_set": best["feature_set"],
                            "feature": feature,
                            "mean_abs_shap": float(importance),
                        }
                    )
                sample_dates = group.loc[sample.index, date_col]
                for row_position, row_index in enumerate(sample.index):
                    for feature_position, feature in enumerate(final_fitted.features):
                        shap_value_rows.append(
                            {
                                "well_no": well,
                                "date": sample_dates.loc[row_index],
                                "feature_set": best["feature_set"],
                                "feature": feature,
                                "feature_value": float(sample.loc[row_index, feature]),
                                "shap_value": float(values[row_position, feature_position]),
                            }
                        )
                shap_records.append(
                    {
                        "well_no": well,
                        "feature_set": best["feature_set"],
                        "features": final_fitted.features,
                        "shap_values": values,
                        "feature_values": sample.reset_index(drop=True),
                    }
                )
            except Exception as exc:
                LOGGER.warning("SHAP failed for %s: %s", well, exc)

        if model_cfg.get("save_models", True):
            model_path = models_dir / f"{_slug(well)}_extra_trees.joblib"
            joblib.dump(
                {
                    "well_no": well,
                    "feature_set": best["feature_set"],
                    "features": final_fitted.features,
                    "medians": final_fitted.medians.to_dict(),
                    "params": best["params"],
                    "model": final_fitted.model,
                    "target_col": target_col,
                },
                model_path,
            )

        summary_rows.append(
            {
                "well_no": well,
                "n_grid_rows": int(len(group)),
                "n_original_observed": int(group[original_col].notna().sum()),
                "n_clean_observed": int(group[cleaned_col].notna().sum()),
                "n_removed_or_corrupt": int(
                    (group[original_col].notna() & group[cleaned_col].isna()).sum()
                ),
                "n_imputed": int(group["is_imputed"].sum()),
                "n_unresolved": int(group[final_col].isna().sum()),
                "n_internal_imputed": int((group["prediction_scope"] == "internal_gap").sum()),
                "n_leading_extrapolated": int((group["prediction_scope"] == "leading_extrapolation").sum()),
                "n_trailing_extrapolated": int((group["prediction_scope"] == "trailing_extrapolation").sum()),
                "feature_set": best["feature_set"],
                "best_params": json.dumps(best["params"], sort_keys=True),
                "cv_r2_mean": best["metrics"]["cv_r2_mean"],
                "cv_r2_std": best["metrics"]["cv_r2_std"],
                "cv_mae_mean": best["metrics"]["cv_mae_mean"],
                "cv_mae_std": best["metrics"]["cv_mae_std"],
                "cv_rmse_mean": best["metrics"]["cv_rmse_mean"],
                "cv_rmse_std": best["metrics"]["cv_rmse_std"],
                "outer_n": outer_n,
                "outer_r2": outer_r2,
                "outer_mae": outer_mae,
                "outer_rmse": outer_rmse,
            }
        )

    summary = pd.DataFrame(summary_rows)
    candidates = pd.DataFrame(candidate_rows)
    cv_intervals = pd.DataFrame(cv_interval_rows)
    outer_predictions = (
        pd.concat(outer_prediction_frames, ignore_index=True)
        if outer_prediction_frames
        else pd.DataFrame()
    )
    imputed_series = (
        pd.concat(series_frames, ignore_index=True).sort_values([id_col, date_col])
        if series_frames
        else pd.DataFrame()
    )
    feature_importance = pd.DataFrame(feature_importance_rows)
    vif = pd.DataFrame(vif_rows)
    shap_importance = pd.DataFrame(shap_importance_rows)
    shap_values = pd.DataFrame(shap_value_rows)
    skipped = pd.DataFrame(skipped_rows)

    noise = _calculate_noise_metrics(featured, id_col, date_col, cleaned_col)
    noise_performance = noise.merge(summary[["well_no", "outer_r2"]], on="well_no", how="left") if not summary.empty else noise

    if not vif.empty:
        avg_vif = (
            vif.groupby(["feature_set", "feature"], as_index=False)
            .agg(vif_mean=("vif", "mean"), vif_std=("vif", "std"), n_wells=("well_no", "nunique"))
        )
    else:
        avg_vif = pd.DataFrame()

    if not shap_importance.empty:
        shap_aggregate = (
            shap_importance.groupby(["feature_set", "feature"], as_index=False)
            .agg(mean_abs_shap=("mean_abs_shap", "mean"), std_abs_shap=("mean_abs_shap", "std"), n_wells=("well_no", "nunique"))
            .sort_values(["feature_set", "mean_abs_shap"], ascending=[True, False])
        )
    else:
        shap_aggregate = pd.DataFrame()

    write_csv = bool(config["output"].get("write_csv", True))
    write_parquet = bool(config["output"].get("write_parquet", True))
    output_manifest: list[dict[str, Any]] = []
    tables = {
        "imputed_groundwater_levels": imputed_series,
        "well_model_summary": summary,
        "candidate_model_metrics": candidates,
        "outer_holdout_predictions": outer_predictions,
        "cv_masked_intervals": cv_intervals,
        "signal_cleaning_events": cleaning_events,
        "feature_importance_per_well": feature_importance,
        "vif_per_well": vif,
        "vif_aggregate": avg_vif,
        "noise_metrics": noise,
        "noise_vs_performance": noise_performance,
        "shap_importance_per_well": shap_importance,
        "shap_importance_aggregate": shap_aggregate,
        "shap_values_sample": shap_values,
        "skipped_wells": skipped,
    }
    for name, table in tables.items():
        _write_table(
            table,
            tables_dir / name,
            write_csv,
            write_parquet,
            output_manifest,
        )

    figure_outputs: list[str] = []
    if diagnostic_cfg.get("create_figures", True) and not imputed_series.empty:
        timeseries_path = figures_dir / "stacked_imputation_timeseries.png"
        _create_timeseries_figure(imputed_series, config, timeseries_path)
        if timeseries_path.exists():
            figure_outputs.append(str(timeseries_path))

        feature_path = figures_dir / "feature_importance_comparison.png"
        _create_feature_importance_figure(
            feature_importance,
            feature_path,
            int(diagnostic_cfg["figure_dpi"]),
        )
        if feature_path.exists():
            figure_outputs.append(str(feature_path))

        noise_path = figures_dir / "groundwater_noise_vs_performance.png"
        _create_noise_performance_figure(
            noise_performance,
            noise_path,
            int(diagnostic_cfg["figure_dpi"]),
        )
        if noise_path.exists():
            figure_outputs.append(str(noise_path))

        if diagnostic_cfg.get("calculate_shap", True):
            figure_outputs.extend(
                _create_shap_outputs(
                    shap_records,
                    shap_dir,
                    int(diagnostic_cfg["maximum_shap_features"]),
                    int(diagnostic_cfg["figure_dpi"]),
                )
            )

    manifest = {
        "skill": "lt-lv-karst-well-imputation",
        "input_path": str(Path(input_path).resolve()),
        "output_directory": str(output_dir.resolve()),
        "wells_requested": list(config["domain"]["wells"]),
        "wells_modeled": summary["well_no"].tolist() if not summary.empty else [],
        "validation": validation_report,
        "cleaning_event_count": int(len(cleaning_events)),
        "table_outputs": output_manifest,
        "figure_outputs": figure_outputs,
        "model_files": sorted(str(path) for path in models_dir.glob("*.joblib")),
        "methodological_warnings": [
            "The output is a retrospective reconstruction, not an independent forecast.",
            "Leading and trailing predictions are extrapolations and are labeled prediction_scope.",
            "Known bad intervals are domain assumptions and must be reviewed for each dataset revision.",
            "Synthetic 31 December anchoring is disabled by default because it creates a non-observed target value.",
        ],
        "config": config,
    }
    manifest_path = output_dir / "run_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2, default=str)
    return manifest


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Impute daily groundwater levels for specific LT-LV karst wells."
    )
    parser.add_argument("--input", help="Input CSV/ZIP/Parquet/Excel table.")
    parser.add_argument("--config", help="YAML configuration file.")
    parser.add_argument("--output-dir", required=True, help="Output directory.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    config = load_config(args.config)
    input_path = args.input or config["input"].get("path")
    if not input_path:
        parser.error("Provide --input or set input.path in the YAML configuration.")
    manifest = run_pipeline(input_path, args.output_dir, config)
    LOGGER.info(
        "Completed LT-LV karst imputation for %s wells. Manifest: %s",
        len(manifest["wells_modeled"]),
        Path(args.output_dir) / "run_manifest.json",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
