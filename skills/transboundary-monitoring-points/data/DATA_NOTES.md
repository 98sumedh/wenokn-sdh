# GRANDE-U Transboundary Groundwater — Data Notes & Merge Decisions

Source: owncloud share `GRANDE-U_Task1/`. Two regions, seven countries:
Baltic/E. Europe (UA, PL, LT, LV, EE) and US–Mexico Rio Grande (US, MX).
Each country contributes a Monitoring Points file (`*_MP_*`, one row per well)
and a Groundwater Time Series file (`*_GWTS_*`, periodic water-level readings).

Two products are built for each of MP and GWTS:
- **faithful** — raw string values untouched; only headers harmonised + `country`,
  `country_name`, `source_file` added.
- **clean** — typed and normalised; every change listed below.

## Canonical source file chosen per country (latest matched MP+GWTS pair)

| Country | MP file | GWTS file |
|---|---|---|
| UA Ukraine | `UA_MP_20260615.csv` | `UA_GWTS_20250516.csv` |
| PL Poland | `PL_MP_20250903.csv` | `PL_GWTS_20250311_corrected.csv` (corrected, not raw) |
| LT Lithuania | `LT_MP_20250903.csv` | `LT_GWTS_20250219.csv` |
| LV Latvia | `UL_MP_20250903.csv` | `UL_GWTS_20250215.csv` |
| EE Estonia | `UT_MP_20250903.csv` | `UT_GWTS_20250827.csv` |
| US United States | `US_MP_20260303.csv` | `US_GWTS_20251010.csv` |
| MX Mexico | `MX_MP_20250930.csv` | `MX_GWTS_20250930.csv` |

Notes on file naming: Latvia's files are prefixed `UL_`, Estonia's `UT_`
(University of Tartu), not `LV_`/`EE_`. Country is assigned from the folder, not
the filename prefix.

## Result sizes (verified by running the build)

- **MP**: 305 rows = UA 124, MX 60, LV 52, PL 27, LT 19, US 15, EE 8.
  299 unique well IDs (6 UA duplicates, see below).
- **GWTS**: 28,125 rows, observation years 1965–2025.

## Cross-country consistency checks

| Check | Finding | Decision |
|---|---|---|
| Delimiter | `;` everywhere | consistent — no action |
| Decimal separator | **LV uses comma** (`24,27525`) for coords/depths (but dot for `avg_gw_abs`); all other countries use dot | clean: comma→dot then numeric; faithful: left as-is |
| Encoding | mostly ASCII/UTF-8; US & MX MP and MX GWTS carry a UTF-8 BOM on `well_ID`; UA GWTS has Cyrillic chars and leading spaces in some IDs | read with `utf-8-sig`; clean strips whitespace from `well_ID` |
| Column names | `temporal data resolution` (spaces) vs `temporal_data_resolution` (LV, underscores); `Distance to the nearest river. m` (UA only) | headers harmonised in both products (rename only, values untouched) |
| Duplicate column | **US MP has `pumping` twice** — verified byte-identical | clean: drop the duplicate; faithful: keeps it as `pumping`/`pumping.1` collapsed at read (identical) |
| Coordinate sanity | every country's WGS84 lon/lat falls inside that country's territory (UA W-Ukraine, PL E-Poland, LT, LV, EE S-Estonia, US El Paso/Mesilla, MX Chihuahua/Juárez) | no relocation needed |
| Boolean encoding | `pumping` = TRUE/FALSE (most) or True/False; `aquifer_karst`,`confinement` = 0/1 | clean: all → nullable boolean (blank → NA) |
| Lithology typo | LT has `terrigenc` (missing i) | clean: corrected to `terrigenic`; faithful: left |
| EPSG_local | numeric (`2180`,`3346`) vs string (`EPSG3301`) vs blank (UA, LV, US, MX) | clean: digits extracted → Int64 |
| Duplicate well IDs | UA has 6: `UA_RDS_S237-?`, `UA_RDS_Sp1-?`..`Sp4-?`, `UA_RDS_Sp10-?` — the `-?` marks an unknown well number; cannot confirm they are the same well | **FLAGGED, left in place** — not merged or dropped |

## MP↔GWTS join coverage (clean)

| Country | MP wells | GWTS wells | join | MP-only | GWTS-only |
|---|---|---|---|---|---|
| UA | 118 | 100 | 60 | 58 | 40 |
| PL | 27 | 27 | 27 | 0 | 0 |
| LT | 19 | 19 | 19 | 0 | 0 |
| LV | 52 | 52 | 52 | 0 | 0 |
| EE | 8 | 8 | 8 | 0 | 0 |
| US | 15 | 15 | 15 | 0 | 0 |
| MX | 60 | 60 | 58 | 2 | 2 |

- **UA join is only partial (60 of 118 MP wells have a series; 40 series wells have
  no MP record).** Genuine missing records (same ID prefixes on both sides), not a
  naming-scheme mismatch. FLAGGED — not patched.
- **MX**: 2 MP wells without series and 2 series wells without MP. FLAGGED.

## Country-specific / not-comparable-across-countries columns

- `greatest_permeability_zone`, `distance_to_nearest_river_m` exist **only for UA**.
- `Long_local`/`Lat_local`/`EPSG_local` populated only for some countries
  (PL, LT, EE have local grid coords; UA, LV, US, MX mostly blank).
- `temporal_data_resolution`: only MX states it (`annual`); blank elsewhere.
- `well_depth`, `open_from`, `open_to`, `aquifer_thickness` largely blank for MX.
- GWTS `ground_altitude` column is present **only in MX** (per-row repeat of the
  well altitude); blank/absent for all others.
- GWTS `observation_month` is blank for 141 rows (mostly MX annual readings).

## Open decision flagged for the user

**Lithuania has a second, newer partial update** (`LT_MP_20250904.csv` +
`LT_GWTS_20250904.csv`): only 10 wells, bare numeric IDs (no `LT_` prefix), no
`avg_gw_abs`, booleans as `True/False`, but the series run later (2006–2023 vs the
chosen pair's 1975–2003 for overlapping wells). The chosen canonical pair
(`*_20250903` + `*_20250219`, 19 wells, complete schema) is the fuller dataset.
Decision taken: **use the 19-well pair; flag the 10-well update.** Confirm if you'd
prefer to merge/replace with the newer series for those 10 wells.
