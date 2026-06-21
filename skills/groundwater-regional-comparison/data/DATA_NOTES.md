# Groundwater Regional Comparison — Data Notes

This skill answers **cross-region** and **"why"** questions by putting every
groundwater region on a common footing. It does not hold new well data of its
own except the climate/GRACE drivers; it reuses the bundled datasets of the
other skills and adds the explanatory layer.

## Sources combined

| Region(s) | Depth-to-water / variability | Aquifer character | Climate drivers |
|---|---|---|---|
| Italy (Po basin) | `po-wells` (WTD mean + STD per well) | — (not in dataset) | — (not available) |
| UA, PL, LT, LV, EE | `transboundary-groundwater-timeseries` | `transboundary-monitoring-points` | bundled climate/GRACE |
| US | same | same | PET + GRACE only |
| MX | same | same | — (not in climate file) |

## The bundled climate/GRACE file

`data/transboundary_climate_grace.parquet` is cleaned from the GRANDE-U
`08_mergedTimeseries/GWTS_with_climate_and_GRACE.csv` (monthly, 1995–2024):

| Column | Meaning |
|---|---|
| `well_ID`, `country`, `country_name` | well + region |
| `observation_year`, `observation_month` | from the file's `date` |
| `precip` | monthly precipitation (mm, E-OBS) |
| `pet`, `aet` | potential / actual evapotranspiration (mm, GLEAM) |
| `temp` | mean temperature (°C) |
| `grace_value` | GRACE terrestrial-water-storage anomaly |
| `gw_level_from_ground` / `gw_level_abs` | **re-joined from `transboundary-groundwater-timeseries`** (see fix below) |

## Decisions & fixes

- **Latvia GW levels were empty in the climate file.** The merged CSV had
  precip/PET/temp/GRACE for Latvia but its `gw_level_from_ground` column was
  blank (and `rel_gw_change` absent). Fixed by re-joining the authoritative
  water levels from `transboundary-groundwater-timeseries` on
  `well_ID` + year + month. After the fix, Latvia's water table correlates
  with GRACE at −0.49 (was unusable).
- **Depth-to-water / variability** are computed from wells that have a
  **timeseries**; **aquifer character** (% karst, % confined, well depth) is
  computed from the **full monitoring-point inventory** (all wells, % over
  non-null values). These use different denominators on purpose — stated in
  the loader and the skill.
- **Comparability caveat:** regions were measured by different national
  programs over different periods and cadences. Cross-region numbers are
  **indicative**, not exact, and should always be reported with that caveat.

## Known gaps (do not paper over)

- **Italy and Mexico have no climate/GRACE data** in this file (Mexico absent
  entirely; the US has PET + GRACE but no precip/temp). So the full "why"
  (climate-driven) analysis is available for UA, PL, LT, LV, EE and partially
  US — **not** Italy or Mexico. For those, "why" must rely on aquifer/geology
  attributes and qualitative reasoning.
- Monthly precipitation correlates only weakly with water-table depth because
  groundwater integrates and lags climate; **GRACE storage is the stronger,
  more honest explanatory variable.**
