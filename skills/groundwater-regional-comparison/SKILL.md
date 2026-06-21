---
name: groundwater-regional-comparison
description: >-
  COMPARE groundwater across regions and explain WHY they differ. Use whenever
  the user asks to compare or contrast regions, asks about differences between
  Italy and the Eastern-European transboundary areas, differences across the
  five transboundary areas (Ukraine, Poland, Lithuania, Latvia, Estonia), which
  region is wettest/driest/deepest/most variable/most depleting, or asks WHY a
  region's water table behaves as it does (climate, aridity, recharge, GRACE
  storage, aquifer type, pumping). Puts every region on a common footing
  (depth-to-water, variability, aquifer character) and adds a bundled
  climate + GRACE layer for causal reasoning. For a SINGLE region/country use
  the per-dataset skills instead (po-wells, er-well-registry,
  transboundary-monitoring-points, transboundary-groundwater-timeseries).
---

# Groundwater Regional Comparison & Drivers Skill

This skill answers the **cross-region** and **"why"** questions that the
single-dataset skills cannot: comparing Italy's Po basin against the
Eastern-European transboundary areas, comparing the five transboundary
areas with each other, and explaining the differences using climate and
GRACE water-storage data.

It does not introduce new well inventories — it **reuses the bundled data of
the other skills** and puts them on a common footing, then adds a bundled
**climate + GRACE** layer (`data/transboundary_climate_grace.parquet`) for
causal reasoning. See `data/DATA_NOTES.md` for sources and fixes.

## The common currency

Different national programs measured wells differently, so the one metric
that is comparable everywhere is **depth to water table** (meters below
ground): `gw_level_from_ground` for the transboundary wells, `wtd_m` for the
Italian Po wells. Smaller = shallower/wetter, larger = deeper/drier.
Secondary comparables: **temporal variability** (per-well std of the water
table) and, for the transboundary wells, **aquifer character** (% karst,
% confined, lithology, borehole depth).

## Regions covered

Italy (Po basin) · Ukraine · Poland · Lithuania · Latvia · Estonia ·
United States (Rio Grande) · Mexico (Rio Grande). The "five transboundary
areas" Ilya refers to are the Baltic/Eastern-European group: **UA, PL, LT,
LV, EE**; US + MX are the separate Rio Grande pair.

## Honest limitations (state these in answers)

- **Climate/GRACE covers the transboundary wells only.** Italy and Mexico are
  **not** in the climate file (Mexico absent; the US has PET + GRACE but no
  precip/temp). So climate-driven "why" is available for UA, PL, LT, LV, EE
  and partially US — for Italy and Mexico, explain via aquifer/geology and
  qualitative reasoning instead.
- **Indicative, not exact.** Regions differ in measurement method, period, and
  cadence; always report cross-region numbers with that caveat.
- **Different denominators by design:** depth-to-water / variability come from
  wells that have a timeseries; aquifer % and well depth come from the full
  monitoring-point inventory.
- **Monthly precipitation correlates weakly** with the water table because
  groundwater integrates and lags climate — **GRACE storage is the stronger
  explanatory variable.** Don't overstate the precipitation link.

## Standard loaders

```python
import pandas as pd, numpy as np

MP="skills/transboundary-monitoring-points/data"
GW="skills/transboundary-groundwater-timeseries/data"
PO="skills/po-wells/data"
CMP="skills/groundwater-regional-comparison/data"

def load_climate() -> pd.DataFrame:
    """Monthly climate + GRACE drivers (UA/PL/LT/LV/EE + partial US), with
    authoritative water levels re-joined. Italy & Mexico are not present."""
    return pd.read_parquet(f"{CMP}/transboundary_climate_grace.parquet")

def load_regions() -> pd.DataFrame:
    """One row per well, all regions, on a common schema:
    region, well_ID, dtw_mean (m below ground), dtw_std (variability),
    well_depth_m, aquifer_lithology, karst, confined."""
    frames=[]
    ts=pd.read_parquet(f"{GW}/transboundary_gwts_clean.parquet").dropna(subset=["gw_level_from_ground"])
    agg=ts.groupby("well_ID")["gw_level_from_ground"].agg(dtw_mean="mean", dtw_std="std")
    region=ts.groupby("well_ID")["country_name"].first()          # region from GWTS (keeps UA orphans)
    mp=pd.read_parquet(f"{MP}/transboundary_mp_clean.parquet").drop_duplicates("well_ID").set_index("well_ID")
    tb=(agg.join(region)
           .join(mp[["well_depth","aquifer_lithology","aquifer_karst","confinement"]])
           .reset_index()
           .rename(columns={"country_name":"region","well_depth":"well_depth_m",
                            "aquifer_karst":"karst","confinement":"confined"}))
    frames.append(tb)
    pm=pd.read_csv(f"{PO}/Steady_State_Leonardo.csv"); ps=pd.read_csv(f"{PO}/Standard_Deviation_Leonardo.csv")
    po=pm.merge(ps[["Well ID","STD"]], on="Well ID")
    frames.append(pd.DataFrame({"well_ID":po["Well ID"], "dtw_mean":po["WTD"], "dtw_std":po["STD"],
                                "region":"Italy (Po basin)", "well_depth_m":np.nan,
                                "aquifer_lithology":pd.NA, "karst":pd.NA, "confined":pd.NA}))
    return pd.concat(frames, ignore_index=True)

def regional_summary() -> pd.DataFrame:
    """Per-region comparison table. Depth-to-water & variability from timeseries
    wells; aquifer character from the full monitoring-point inventory."""
    df=load_regions()
    dtw=df.groupby("region").agg(
        dtw_median_m=("dtw_mean","median"),
        dtw_iqr_m=("dtw_mean", lambda s: s.quantile(.75)-s.quantile(.25)),
        variability_median_m=("dtw_std","median"))
    mp=pd.read_parquet(f"{MP}/transboundary_mp_clean.parquet")
    pct=lambda s:(100*(s.dropna()==True).mean() if s.notna().any() else np.nan)
    aq=mp.groupby("country_name").agg(
        n_wells=("well_ID","nunique"), well_depth_median_m=("well_depth","median"),
        pct_karst=("aquifer_karst",pct), pct_confined=("confinement",pct))
    out=dtw.join(aq, how="left")
    out.loc["Italy (Po basin)","n_wells"]=df[df.region=="Italy (Po basin)"].well_ID.nunique()
    return out
```

## Example queries (verified against the bundled data)

### Q1 — Italy vs the Eastern-European transboundary areas

```python
s = regional_summary()
print(s[["n_wells","dtw_median_m","variability_median_m","pct_karst","pct_confined"]])
```
Findings: Italy's Po basin median depth-to-water is **5.8 m** (wide spread,
IQR 11 m) with moderate variability (σ≈0.87 m). The Eastern-European areas
range from very shallow (**Ukraine 0.9 m**) to deep (**Estonia 11 m**) and are
generally **calmer** (σ≈0.2–0.4 m). Eastern Europe is also more heterogeneous
geologically — substantial **karst** (Lithuania 47%) and **confined** aquifers
(Latvia & Lithuania ≈53%) — whereas the Po basin is uniform alluvial plain.

### Q2 — Differences across the five transboundary areas (UA, PL, LT, LV, EE)

```python
s = regional_summary().loc[["Ukraine","Poland","Lithuania","Latvia","Estonia"]]
print(s)
```
Water table shallow→deep: **Ukraine (0.9) < Latvia (3.1) ≈ Poland (3.4) <
Lithuania (6.2) < Estonia (11) m.** Karst is essentially a **Lithuania**
phenomenon (47%; others ≤8%). Confinement is high in **Latvia/Lithuania**
(~53%), moderate in UA/PL (33–37%), zero in Estonia.

### Q3 — Why do they differ? (climate, storage, geology)

```python
cl = load_climate()

# (a) Climate normals / aridity per region
clim = cl.groupby("country_name").agg(
    precip_ann_mm=("precip", lambda s: s.mean()*12 if s.notna().any() else np.nan),
    pet_ann_mm  =("pet",    lambda s: s.mean()*12 if s.notna().any() else np.nan),
).assign(water_balance_mm=lambda d: d.precip_ann_mm - d.pet_ann_mm)

# (b) Which driver explains the water table? median per-well correlation
def corr_by_well(sub, x):
    out=[]
    for _, g in sub.groupby("well_ID"):
        g=g.dropna(subset=["gw_level_from_ground", x])
        if len(g)>=24 and g[x].std()>0 and g["gw_level_from_ground"].std()>0:
            out.append(g["gw_level_from_ground"].corr(g[x]))
    return round(float(np.nanmedian(out)),2) if out else np.nan
why = {r: {"precip":corr_by_well(g,"precip"), "pet":corr_by_well(g,"pet"),
           "grace":corr_by_well(g,"grace_value")} for r,g in cl.groupby("country_name")}
```
Findings:
- **GRACE total water storage is the dominant control** — depth-to-water moves
  *opposite* to storage everywhere: Poland −0.69, US −0.71, Latvia −0.49,
  Lithuania −0.41, Ukraine −0.39, Estonia −0.30. When regional water storage
  rises, the water table rises.
- **Aridity sets the baseline depth.** All Baltic/E-European areas are
  water-limited (precip < PET; Poland & Lithuania most so at ≈ −150 mm/yr).
  The deepest, most variable tables — **Mexico ~70 m, US ~12 m, σ 2.65 m** —
  are arid Rio-Grande desert **alluvium under heavy irrigation pumping** (US
  PET ≈ 1388 mm, the highest in the dataset).
- **Monthly precipitation alone explains little** (|corr| ≤ 0.13) — groundwater
  integrates climate over time, which is why GRACE storage is the better
  explanation.

### Q4 — Which region's water table is declining fastest?

```python
ts = pd.read_parquet(f"{GW}/transboundary_gwts_clean.parquet")
def trend(sub):
    slopes=[]
    for _,g in sub.groupby("well_ID"):
        g=g.dropna(subset=["gw_level_from_ground"])
        if g.observation_year.nunique()>=5:
            slopes.append(np.polyfit(g.observation_year.astype(float), g.gw_level_from_ground,1)[0])
    return round(float(np.nanmedian(slopes)),3) if slopes else np.nan
print({r:trend(g) for r,g in ts.groupby("country_name")})
```
Findings: the Rio-Grande wells are **deepening fastest** — Mexico **+0.22 m/yr**
and the US **+0.22 m/yr** (sustained depletion) — while Poland and Ukraine
deepen slowly (~+0.02 m/yr) and the Baltic areas are roughly flat or slightly
rising. Positive = water table getting deeper over time.

## Provenance

- Depth-to-water / variability: `transboundary-groundwater-timeseries`
  (per-country source files) and `po-wells` (`Steady_State_Leonardo.csv`,
  `Standard_Deviation_Leonardo.csv`).
- Aquifer character / well depth: `transboundary-monitoring-points`.
- Climate / GRACE: `data/transboundary_climate_grace.parquet`, cleaned from
  GRANDE-U `GWTS_with_climate_and_GRACE.csv` (E-OBS precip, GLEAM PET/AET,
  GRACE storage), water levels re-joined from the timeseries skill.
- Always cite the comparability caveat and the Italy/Mexico climate gap when
  relevant.

## Reporting tips

- Lead with the **common currency** (depth-to-water, m below ground) and state
  it's measured differently per program → indicative comparison.
- For "why", lead with **GRACE storage** and **aridity (precip vs PET)**, then
  geology (karst/confined/lithology); note monthly rainfall is a weak predictor.
- For Italy or Mexico "why", say climate/GRACE isn't available and reason from
  aquifer type and setting instead.
- "Deepening / depleting" → positive trend in `gw_level_from_ground`.
