---
name: nlcd-land-cover
description: Retrieve NLCD (National Land Cover Database) land use and land cover data for any US region using HyRiver/pygeohydro. Query by geometry or GeoDataFrame. Returns raster data with land cover classes, imperviousness, and canopy. Built-in cover_statistics() computes percentage breakdown by land use type.
---

# NLCD Land Cover Skill

## Description

This skill retrieves land use and land cover (LULC) data from the USGS National Land Cover Database (NLCD) using the HyRiver `pygeohydro` library. Data is fetched directly from the MRLC GeoServer — no local files or downloads required.

**Data Source:**
- USGS National Land Cover Database (NLCD)
- Accessed via HyRiver Python package (`pygeohydro`)
- Server: MRLC (Multi-Resolution Land Characteristics) GeoServer
- Coverage: Contiguous USA (L48), Alaska (AK), Hawaii (HI), Puerto Rico (PR)
- Resolution: 30-meter native (resampled server-side to requested resolution)

**Available Layers:**
- **cover**: Land use / land cover class (integer codes)
- **impervious**: Percent impervious surface (0-100)
- **canopy**: Percent tree canopy cover (0-100)
- **descriptor**: Impervious surface descriptor

**Available Years:** 2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2021

## CRITICAL: Key Functions

| Function | Purpose |
|----------|---------|
| `gh.nlcd_bygeom(gdf, resolution, years, region)` | Get NLCD raster for a GeoDataFrame geometry |
| `gh.cover_statistics(cover_da)` | Compute percentage breakdown of land cover classes |
| `gh.helpers.nlcd_helper()` | Get NLCD class codes, labels, and categories |
| `gh.plot.cover_legends()` | Get official NLCD colormap for plotting |

## CRITICAL: cover_statistics() Returns Percentages Directly

**Do NOT manually count pixels.** `gh.cover_statistics()` handles all pixel counting and percentage calculation automatically:

```python
# Get NLCD data
lulc = gh.nlcd_bygeom(buffer_gdf, resolution=30, years={"cover": [2021]})

# Get percentage breakdown — one line!
stats = gh.cover_statistics(lulc.cover_2021)

# stats.categories  → dict of {category_name: percentage}
# stats.classes     → dict of {class_code: percentage}
```

## IMPORTANT: Memory and Resolution

- The MRLC GeoServer limits requests to ~8 million pixels
- `pygeohydro` automatically handles domain decomposition for large areas
- Use higher resolution numbers (coarser) for large regions to avoid memory issues
- Recommended resolutions: 30m (small areas), 100m (state-level), 300m (multi-state)

## IMPORTANT: GeoDataFrame Index as Keys

`nlcd_bygeom()` returns a **dict** keyed by the GeoDataFrame's index values. Set meaningful index values before calling:

```python
buffer_gdf.index = ["i80_buffer"]
lulc = gh.nlcd_bygeom(buffer_gdf, resolution=30, years={"cover": [2021]})
cover = lulc["i80_buffer"].cover_2021   # Access by index key
```

## When to Use

Use this skill to:

- Identify dominant land use within a buffer zone (road, river, park, etc.)
- Get land cover percentage breakdown for any polygon region
- Analyze urban vs. natural land cover
- Compare land cover across years (2001-2021)
- Get imperviousness or canopy data for a watershed or region
- Answer questions like "What is the land use within 5km of I-80 in California?"

## How to Use

### Step 1: Import Required Libraries

```python
import pygeohydro as gh
import geopandas as gpd
import pandas as pd
```

### Step 2: Prepare Your Region Geometry

```python
# Your region must be a GeoDataFrame in EPSG:4326
# Set a meaningful index — it becomes the key in the returned dict

# Example: 5km buffer around I-80 in California
# (assumes i80_ca is a GeoDataFrame from the freeway-system SKILL)
i80_projected = i80_ca.to_crs("EPSG:5070")       # Project to metric CRS
i80_buffer = i80_projected.buffer(5000)           # 5km buffer in meters
buffer_gdf = gpd.GeoDataFrame(geometry=[i80_buffer.union_all()], crs="EPSG:5070")
buffer_gdf = buffer_gdf.to_crs("EPSG:4326")       # Back to WGS84
buffer_gdf.index = ["i80_ca_buffer"]              # Set meaningful index
```

### Step 3: Get NLCD Data and Compute Statistics

```python
def get_land_cover_stats(region_gdf, year=2021, resolution=30, region="L48"):
    """
    Get NLCD land cover data and percentage statistics for a region.

    Parameters:
    -----------
    region_gdf : geopandas.GeoDataFrame
        Region of interest in EPSG:4326. Index values become dict keys.
    year : int
        NLCD year. Options: 2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2021
    resolution : float
        Raster resolution in meters. Use 30 for small areas, 100+ for large regions.
    region : str
        "L48" (CONUS), "AK" (Alaska), "HI" (Hawaii), "PR" (Puerto Rico)

    Returns:
    --------
    dict with keys:
        "lulc"      : xarray.Dataset (raw NLCD data)
        "stats"     : named tuple with .classes and .categories percentage dicts
        "dominant"  : str, name of dominant land cover class
        "cover_da"  : xarray.DataArray for the cover layer
    """
    # Fetch NLCD data from MRLC GeoServer
    lulc = gh.nlcd_bygeom(
        region_gdf,
        resolution,
        years={"cover": [year]},
        region=region
    )

    # Get the cover DataArray for the first geometry
    key = region_gdf.index[0]
    cover_attr = f"cover_{year}"
    cover_da = getattr(lulc[key], cover_attr)

    # Compute percentage statistics
    stats = gh.cover_statistics(cover_da)

    # Find dominant class
    dominant_class = max(stats.classes, key=stats.classes.get)
    nlcd_info = gh.helpers.nlcd_helper()
    dominant_label = nlcd_info["classes"].get(str(dominant_class), f"Class {dominant_class}")

    return {
        "lulc": lulc,
        "stats": stats,
        "dominant": dominant_label,
        "cover_da": cover_da
    }
```

### Step 4: Query Examples

#### Example 1: Dominant Land Use Within 5km of I-80 in California

```python
import pygeohydro as gh
import geopandas as gpd

# Step 1: Get I-80 in California (from freeway-system SKILL)
# i80_ca = get_highways_in_region("NUMBER = '80' AND CLASS = 'I'", california_gdf)

# Step 2: Create 5km buffer
i80_proj = i80_ca.to_crs("EPSG:5070")
buffer_union = i80_proj.buffer(5000).union_all()
buffer_gdf = gpd.GeoDataFrame(geometry=[buffer_union], crs="EPSG:5070")
buffer_gdf = buffer_gdf.to_crs("EPSG:4326")
buffer_gdf.index = ["i80_buffer"]

# Step 3: Get NLCD land cover
lulc = gh.nlcd_bygeom(buffer_gdf, resolution=100, years={"cover": [2021]})

# Step 4: Compute statistics
cover_da = lulc["i80_buffer"].cover_2021
stats = gh.cover_statistics(cover_da)

# Step 5: Find dominant land use
dominant_class = max(stats.classes, key=stats.classes.get)
nlcd_info = gh.helpers.nlcd_helper()
dominant_label = nlcd_info["classes"].get(str(dominant_class), f"Class {dominant_class}")

print(f"Dominant land use within 5km of I-80 in California:")
print(f"  {dominant_label}: {stats.classes[dominant_class]:.1f}%")

print(f"\nFull breakdown by class:")
sorted_classes = sorted(stats.classes.items(), key=lambda x: x[1], reverse=True)
for code, pct in sorted_classes:
    if pct > 0.1:
        label = nlcd_info["classes"].get(str(code), f"Class {code}")
        print(f"  {label}: {pct:.1f}%")

print(f"\nBreakdown by category:")
for category, pct in sorted(stats.categories.items(), key=lambda x: x[1], reverse=True):
    if pct > 0.1:
        print(f"  {category}: {pct:.1f}%")
```

#### Example 2: Land Cover for Any Polygon Region

```python
# Works with any GeoDataFrame: watershed, county, park, buffer, etc.
# Example: land cover in a national park boundary
# park_gdf = get_park_by_name("Yosemite")  # from national-parks SKILL
park_gdf.index = ["yosemite"]

lulc = gh.nlcd_bygeom(park_gdf, resolution=30, years={"cover": [2021]})
stats = gh.cover_statistics(lulc["yosemite"].cover_2021)

print("Land cover in Yosemite National Park:")
nlcd_info = gh.helpers.nlcd_helper()
for code, pct in sorted(stats.classes.items(), key=lambda x: x[1], reverse=True):
    if pct > 0.5:
        label = nlcd_info["classes"].get(str(code), f"Class {code}")
        print(f"  {label}: {pct:.1f}%")
```

#### Example 3: Compare Land Cover Across Years

```python
# Get land cover for multiple years to detect change
buffer_gdf.index = ["study_area"]

lulc = gh.nlcd_bygeom(
    buffer_gdf,
    resolution=100,
    years={"cover": [2001, 2011, 2021]}
)

nlcd_info = gh.helpers.nlcd_helper()
print("Land cover change over time:")
print(f"{'Class':<40} {'2001':>8} {'2011':>8} {'2021':>8}")
print("-" * 68)

stats_2001 = gh.cover_statistics(lulc["study_area"].cover_2001)
stats_2011 = gh.cover_statistics(lulc["study_area"].cover_2011)
stats_2021 = gh.cover_statistics(lulc["study_area"].cover_2021)

all_codes = set(stats_2001.classes) | set(stats_2011.classes) | set(stats_2021.classes)
rows = []
for code in all_codes:
    p2001 = stats_2001.classes.get(code, 0)
    p2011 = stats_2011.classes.get(code, 0)
    p2021 = stats_2021.classes.get(code, 0)
    if max(p2001, p2011, p2021) > 0.5:
        label = nlcd_info["classes"].get(str(code), f"Class {code}")
        rows.append((label, p2001, p2011, p2021))

for label, p1, p2, p3 in sorted(rows, key=lambda x: x[3], reverse=True):
    print(f"  {label:<38} {p1:>7.1f}% {p2:>7.1f}% {p3:>7.1f}%")
```

#### Example 4: Get Imperviousness and Canopy Too

```python
# Fetch multiple layers at once
lulc = gh.nlcd_bygeom(
    buffer_gdf,
    resolution=100,
    years={
        "cover":      [2021],
        "impervious": [2021],
        "canopy":     [2021]
    }
)

key = buffer_gdf.index[0]
dataset = lulc[key]

# Land cover stats
cover_stats = gh.cover_statistics(dataset.cover_2021)

# Imperviousness (mean % impervious surface)
imp = dataset.impervious_2021
mean_imperv = float(imp.where(imp >= 0).mean())

# Tree canopy (mean % canopy cover)
canopy = dataset.canopy_2021
mean_canopy = float(canopy.where(canopy >= 0).mean())

print(f"Summary for study area:")
print(f"  Mean imperviousness: {mean_imperv:.1f}%")
print(f"  Mean tree canopy:    {mean_canopy:.1f}%")
print(f"  Dominant land cover: {max(cover_stats.classes, key=cover_stats.classes.get)}")
```

#### Example 5: Plot Land Cover Map

```python
import matplotlib.pyplot as plt

# Get official NLCD colormap
cmap, norm, levels = gh.plot.cover_legends()

cover_da = lulc["i80_buffer"].cover_2021

fig, ax = plt.subplots(figsize=(12, 6))
cover_da.where(cover_da < 127).plot(
    ax=ax,
    cmap=cmap,
    levels=levels,
    cbar_kwargs={"ticks": levels[:-1]}
)
ax.set_title("Land Use/Land Cover 2021 — 5km Buffer around I-80, California")
ax.set_axis_off()
plt.tight_layout()
plt.show()
```

## Notes

### NLCD Land Cover Class Codes

```python
# Get full class info programmatically
nlcd_info = gh.helpers.nlcd_helper()
for code, description in nlcd_info["classes"].items():
    print(f"  {code}: {description}")
```

**Key classes:**

| Code | Class |
|------|-------|
| 11 | Open Water |
| 21 | Developed, Open Space |
| 22 | Developed, Low Intensity |
| 23 | Developed, Medium Intensity |
| 24 | Developed, High Intensity |
| 31 | Barren Land |
| 41 | Deciduous Forest |
| 42 | Evergreen Forest |
| 43 | Mixed Forest |
| 52 | Shrub/Scrub |
| 71 | Grassland/Herbaceous |
| 81 | Pasture/Hay |
| 82 | Cultivated Crops |
| 90 | Woody Wetlands |
| 95 | Emergent Herbaceous Wetlands |

### Resolution Guidelines

| Area Size | Recommended Resolution |
|-----------|----------------------|
| Small buffer / watershed | 30m |
| County / park | 30–100m |
| State | 100–300m |
| Multi-state | 300m+ |

### Region Codes

- `"L48"` — Contiguous USA (default)
- `"AK"` — Alaska
- `"HI"` — Hawaii
- `"PR"` — Puerto Rico

### Integration with Other SKILL.md Files

This NLCD skill works seamlessly with other skills:

**freeway-system SKILL:**
```python
# Get I-80 in California, buffer it, get land cover
i80_ca = get_highways_in_region("NUMBER = '80' AND CLASS = 'I'", california_gdf)
buffer_gdf = make_buffer(i80_ca, km=5)
lulc = gh.nlcd_bygeom(buffer_gdf, resolution=100, years={"cover": [2021]})
```

**national-parks SKILL:**
```python
# Get land cover inside a national park
park = get_park_by_name("Grand Canyon")
park.index = ["grand_canyon"]
lulc = gh.nlcd_bygeom(park, resolution=30, years={"cover": [2021]})
```

**watersheds SKILL:**
```python
# Get land cover for a watershed
watershed = get_watershed_by_huc("14010001")
watershed.index = ["watershed_huc8"]
lulc = gh.nlcd_bygeom(watershed, resolution=100, years={"cover": [2021]})
```

**lakes SKILL:**
```python
# Get land cover around a lake buffer
lake = get_lakes_by_name("Tahoe")
lake_proj = lake.to_crs("EPSG:5070")
buffer = gpd.GeoDataFrame(geometry=[lake_proj.buffer(1000).union_all()], crs="EPSG:5070")
buffer = buffer.to_crs("EPSG:4326")
buffer.index = ["tahoe_buffer"]
lulc = gh.nlcd_bygeom(buffer, resolution=30, years={"cover": [2021]})
```

### Complete Example: I-80 California Land Use Analysis

```python
import pygeohydro as gh
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# --- Step 1: Get I-80 in California ---
# (assumes california_gdf and freeway SKILL functions are available)
i80_ca = get_highways_in_region("NUMBER = '80' AND CLASS = 'I'", california_gdf)
print(f"I-80 in California: {len(i80_ca)} segments, "
      f"{i80_ca['DIST_MILES'].sum():.1f} miles")

# --- Step 2: Create 5km buffer ---
i80_proj = i80_ca.to_crs("EPSG:5070")
buffer_union = i80_proj.buffer(5000).union_all()
buffer_gdf = gpd.GeoDataFrame(geometry=[buffer_union], crs="EPSG:5070")
buffer_gdf = buffer_gdf.to_crs("EPSG:4326")
buffer_gdf.index = ["i80_buffer"]

# --- Step 3: Fetch NLCD data ---
print("Fetching NLCD land cover data...")
lulc = gh.nlcd_bygeom(buffer_gdf, resolution=100, years={"cover": [2021]})

# --- Step 4: Compute statistics ---
cover_da = lulc["i80_buffer"].cover_2021
stats = gh.cover_statistics(cover_da)
nlcd_info = gh.helpers.nlcd_helper()

# --- Step 5: Report results ---
print(f"\n{'='*60}")
print(f"LAND USE WITHIN 5KM OF I-80 IN CALIFORNIA (NLCD 2021)")
print(f"{'='*60}")

# Dominant land use
dominant_code = max(stats.classes, key=stats.classes.get)
dominant_label = nlcd_info["classes"].get(str(dominant_code), f"Class {dominant_code}")
print(f"\nDominant land use: {dominant_label} ({stats.classes[dominant_code]:.1f}%)")

# Full class breakdown
print(f"\nFull breakdown by land cover class:")
sorted_classes = sorted(stats.classes.items(), key=lambda x: x[1], reverse=True)
for code, pct in sorted_classes:
    if pct > 0.1:
        label = nlcd_info["classes"].get(str(code), f"Class {code}")
        bar = "█" * int(pct / 2)
        print(f"  {label:<40} {pct:>5.1f}%  {bar}")

# Category summary
print(f"\nBreakdown by land cover category:")
for cat, pct in sorted(stats.categories.items(), key=lambda x: x[1], reverse=True):
    if pct > 0.1:
        print(f"  {cat:<30} {pct:>5.1f}%")

# --- Step 6: Plot ---
cmap, norm, levels = gh.plot.cover_legends()
fig, ax = plt.subplots(figsize=(14, 5))
cover_da.where(cover_da < 127).plot(
    ax=ax, cmap=cmap, levels=levels,
    cbar_kwargs={"ticks": levels[:-1]}
)
ax.set_title("Land Use/Land Cover 2021 — 5km Buffer around I-80, California")
ax.set_axis_off()
plt.tight_layout()
plt.savefig("i80_ca_landcover.png", dpi=150, bbox_inches="tight")
plt.show()
```
