---
name: elevation-terrain
description: Retrieve terrain data (DEM, slope, aspect, ruggedness) for any US region using HyRiver/py3dep and USGS 3DEP. Returns raster layers describing static land surface properties. Use this skill when the question is about WHAT THE LAND LOOKS LIKE — elevation ranges, slope steepness, terrain roughness, or aspect direction across an area. Do NOT use for elevation profiles along routes or trails — use elevation-path-analysis for that.
---

# Elevation Terrain Skill

## Description

This skill retrieves terrain and surface property data for any region in the United States using the HyRiver `py3dep` library, which accesses the USGS 3D Elevation Program (3DEP).

**Data Source:**
- USGS 3D Elevation Program (3DEP)
- Accessed via HyRiver Python package (`py3dep`)
- Server: USGS National Map WCS/WMS endpoints
- Coverage: Contiguous USA, Alaska, Hawaii
- Native resolution: 1m, 3m, 10m, or 30m depending on location

**Available Terrain Layers:**

| Layer Name | Description | Units |
|-----------|-------------|-------|
| `DEM` | Digital Elevation Model | meters |
| `Slope Degrees` | Steepness of terrain | degrees (0–90) |
| `Aspect Degrees` | Direction slope faces | degrees (0–360, -1=flat) |
| `Hillshade` | Shaded relief for visualization | 0–255 |
| `Slope Map` | Classified slope categories | categorical |
| `Aspect Map` | Classified aspect categories | categorical |
| `Roughness` | Terrain roughness (max-min in 3x3 window) | meters |
| `Flow Accumulation` | Upstream drainage area | cells |
| `Flow Direction` | Direction of water flow | categorical |
| `Curvature` | Surface curvature | 1/100 degrees |

## CRITICAL: Resolution Must Match Area Size — Wrong Resolution Will Crash

**Streamlit Community Tier has only ~1GB total memory** shared across the entire app
(Python runtime, geodata, rasters, and all other variables). Terrain rasters must
stay well under 200MB to avoid crashing.

**Target: keep each raster layer under 50MB (~12M pixels maximum).**
For a typical analysis with DEM + slope (2 layers), stay under 6M pixels total.

**Always use `get_safe_resolution()` before any terrain query:**

```python
def get_safe_resolution(region_gdf, target_resolution=30, max_pixels=500_000):
    """
    Select a safe resolution that keeps pixel count under max_pixels.

    Always call this before get_dem() or get_terrain_layers() to prevent
    memory crashes on Streamlit Community Tier (1GB total memory limit).

    Budget per raster layer: ~50MB = ~500,000 pixels (float32 with overhead)
    For 2 layers (DEM + slope): use max_pixels=500_000

    Parameters:
    -----------
    region_gdf : geopandas.GeoDataFrame
        Region of interest in EPSG:4326
    target_resolution : int
        Desired resolution in meters (will be increased if area is too large)
    max_pixels : int
        Maximum pixels per raster layer. Default 500,000 (~50MB with overhead).
        Reduce to 250,000 if fetching 3+ layers simultaneously.

    Returns:
    --------
    int : Safe resolution in meters

    Example:
    --------
    resolution = get_safe_resolution(buffer_gdf)
    dem = get_dem(buffer_gdf, resolution=resolution)
    """
    # Reproject to metric CRS for accurate area calculation
    region_proj = region_gdf.to_crs("EPSG:5070")
    area_sqm = float(region_proj.union_all().area)

    # Minimum resolution to stay under pixel budget
    min_resolution = int(np.sqrt(area_sqm / max_pixels)) + 1
    safe = max(target_resolution, min_resolution)

    area_sqkm = area_sqm / 1_000_000
    actual_pixels = area_sqm / safe**2
    print(f"  Area: {area_sqkm:.0f} sq km")
    print(f"  Resolution: {safe}m  (~{actual_pixels/1e6:.2f}M pixels per layer)")
    if safe > target_resolution:
        print(f"  Note: Requested {target_resolution}m would create "
              f"{area_sqm/target_resolution**2/1e6:.1f}M pixels — too large, "
              f"auto-increased to {safe}m")

    return safe
```

**Pixel budget for 1GB Streamlit app:**

| Layers fetched | Max safe pixels | Reason |
|---------------|----------------|--------|
| 1 layer (DEM only) | 1,000,000 | ~50MB raster + 50MB overhead |
| 2 layers (DEM + slope) | 500,000 each | ~100MB total rasters |
| 3+ layers | 250,000 each | ~150MB total rasters |

**Always use this pattern:**

```python
# CORRECT
resolution = get_safe_resolution(buffer_gdf)           # auto-selects safe resolution
dem = get_dem(buffer_gdf, resolution=resolution)

# WILL CRASH on Streamlit Community for large areas
dem = get_dem(buffer_gdf, resolution=30)
```

| | **elevation-terrain** (this skill) | **elevation-path-analysis** |
|--|----------------------------------|----------------------------|
| **Input** | A polygon area (GeoDataFrame) | A line/route (points along path) |
| **Output** | Raster grids covering an area | Elevation profile along a route |
| **Question type** | "What is the terrain like IN this region?" | "What is the elevation change ALONG this route?" |
| **Examples** | Slope map of Rocky Mountain NP | Elevation gain hiking Trail Ridge Road |
| **Key function** | `py3dep.get_map()` | `py3dep.elevation_bycoords()` |
| **Result** | xarray.DataArray (2D raster) | pandas.Series (1D profile) |

**Use this skill for:**
- "What is the average slope in Yellowstone?"
- "Identify areas with slope < 15° for wildlife movement"
- "What elevation range does the Rocky Mountain corridor span?"
- "Find flat terrain suitable for development/agriculture"
- "Compute terrain ruggedness for habitat suitability"

**Use elevation-path-analysis for:**
- "What is the elevation gain on I-70 through the Rockies?"
- "Plot the elevation profile of the Colorado Trail"
- "How steep is the descent from Loveland Pass?"

## When to Use

Use this skill to:

- Get DEM raster data for a region
- Compute slope and aspect across an area
- Identify terrain barriers (steep slopes) for wildlife corridor analysis
- Find areas within an elevation range (e.g., alpine habitat)
- Compute terrain ruggedness index for habitat suitability
- Generate hillshade for visualization
- Support land use, habitat, and corridor analysis

## How to Use

### Step 1: Import Required Libraries

```python
import py3dep
import geopandas as gpd
import numpy as np
import xarray as xr
```

### Step 2: Define the Query Functions

```python
def get_dem(region_gdf, resolution=30):
    """
    Get Digital Elevation Model (DEM) raster for a region.

    Parameters:
    -----------
    region_gdf : geopandas.GeoDataFrame
        Region of interest. Will be reprojected to EPSG:4326 if needed.
    resolution : int
        Resolution in meters. Options: 1, 3, 10, 30.
        Use 30 for large regions, 10 for detailed local analysis.

    Returns:
    --------
    xarray.DataArray
        DEM raster in meters, CRS = EPSG:4326

    Example:
    --------
    dem = get_dem(rocky_mountain_gdf, resolution=30)
    print(f"Elevation range: {float(dem.min()):.0f}m to {float(dem.max()):.0f}m")
    """
    if region_gdf.crs is None:
        region_gdf = region_gdf.set_crs("EPSG:4326")
    elif region_gdf.crs.to_epsg() != 4326:
        region_gdf = region_gdf.to_crs("EPSG:4326")

    geometry = region_gdf.union_all()
    return py3dep.get_map("DEM", geometry, resolution=resolution, crs="EPSG:4326")


def get_terrain_layers(region_gdf, layers=None, resolution=30):
    """
    Get multiple terrain layers for a region in a single call.

    Parameters:
    -----------
    region_gdf : geopandas.GeoDataFrame
        Region of interest.
    layers : list, optional
        List of layer names to retrieve. Default: ["DEM", "Slope Degrees", "Aspect Degrees"]
        Options: "DEM", "Slope Degrees", "Aspect Degrees", "Hillshade",
                 "Roughness", "Flow Accumulation", "Flow Direction", "Curvature"
    resolution : int
        Resolution in meters (1, 3, 10, or 30).

    Returns:
    --------
    dict of {layer_name: xarray.DataArray}

    Example:
    --------
    terrain = get_terrain_layers(park_gdf, layers=["DEM", "Slope Degrees", "Aspect Degrees"])
    dem = terrain["DEM"]
    slope = terrain["Slope Degrees"]
    """
    if layers is None:
        layers = ["DEM", "Slope Degrees", "Aspect Degrees"]

    if region_gdf.crs is None:
        region_gdf = region_gdf.set_crs("EPSG:4326")
    elif region_gdf.crs.to_epsg() != 4326:
        region_gdf = region_gdf.to_crs("EPSG:4326")

    geometry = region_gdf.union_all()
    result = {}

    for layer in layers:
        result[layer] = py3dep.get_map(layer, geometry, resolution=resolution, crs="EPSG:4326")

    return result


def get_terrain_stats(dem_da):
    """
    Compute summary statistics from a DEM DataArray.

    Parameters:
    -----------
    dem_da : xarray.DataArray
        DEM raster from get_dem() or get_terrain_layers()

    Returns:
    --------
    dict with keys: min, max, mean, median, std (all in meters),
                    and min_ft, max_ft, mean_ft (in feet)

    Example:
    --------
    dem = get_dem(region_gdf)
    stats = get_terrain_stats(dem)
    print(f"Elevation: {stats['min_ft']:.0f} ft to {stats['max_ft']:.0f} ft")
    """
    valid = dem_da.values[~np.isnan(dem_da.values)]
    stats = {
        "min":    float(valid.min()),
        "max":    float(valid.max()),
        "mean":   float(valid.mean()),
        "median": float(np.median(valid)),
        "std":    float(valid.std()),
    }
    # Add feet conversions
    for key in ["min", "max", "mean", "median"]:
        stats[f"{key}_ft"] = stats[key] * 3.28084
    return stats


def classify_slope(slope_da, thresholds=(5, 15, 30, 45)):
    """
    Classify slope raster into passability categories.

    Parameters:
    -----------
    slope_da : xarray.DataArray
        Slope raster in degrees from get_terrain_layers()
    thresholds : tuple of 4 floats
        Breakpoints in degrees defining 5 categories:
          Category 1 (Flat)       :   0° to thresholds[0]
          Category 2 (Gentle)     :   thresholds[0] to thresholds[1]
          Category 3 (Moderate)   :   thresholds[1] to thresholds[2]
          Category 4 (Steep)      :   thresholds[2] to thresholds[3]
          Category 5 (Impassable) :   > thresholds[3]

        Common presets:
          (5, 15, 30, 45) — default, general large mammals (elk, deer)
          (5, 15, 35, 50) — elk (literature supports 35° barrier)
          (5, 10, 15, 20) — pronghorn (prefers nearly flat terrain)
          (5, 20, 45, 60) — mountain lion / wolverine (very agile)
          (3,  8, 12, 20) — bison (nearly flat terrain only)
          (5, 15, 30, 45) — grizzly bear (similar to elk)

    Returns:
    --------
    xarray.DataArray
        Classified slope (1=flat/easy, 2=gentle, 3=moderate,
                          4=steep, 5=impassable)

    Examples:
    ---------
    # Default — general large mammal movement
    classified = classify_slope(slope)

    # Elk-specific threshold
    classified = classify_slope(slope, thresholds=(5, 15, 35, 45))

    # Pronghorn — very sensitive to slope
    classified = classify_slope(slope, thresholds=(5, 10, 15, 20))

    # Check percentage too steep for elk (>35°)
    elk = classify_slope(slope, thresholds=(5, 15, 35, 45))
    too_steep = float((elk >= 4).sum()) / float((~np.isnan(slope.values)).sum()) * 100
    print(f"Too steep for elk: {too_steep:.1f}%")
    """
    t1, t2, t3, t4 = thresholds
    slope_vals = slope_da.values.copy()

    classified = np.zeros_like(slope_vals, dtype=np.int8)
    classified[(slope_vals >= 0)  & (slope_vals < t1)] = 1
    classified[(slope_vals >= t1) & (slope_vals < t2)] = 2
    classified[(slope_vals >= t2) & (slope_vals < t3)] = 3
    classified[(slope_vals >= t3) & (slope_vals < t4)] = 4
    classified[slope_vals >= t4]                        = 5

    result = slope_da.copy(data=classified)
    return result


def slope_passability_report(slope_da, thresholds=(5, 15, 30, 45),
                              category_labels=None):
    """
    Print a full passability breakdown and return percentage dict.

    Parameters:
    -----------
    slope_da : xarray.DataArray
        Slope raster in degrees
    thresholds : tuple of 4 floats
        Breakpoints — same as classify_slope()
    category_labels : list of 5 strings, optional
        Custom labels for the 5 categories.
        Default uses threshold values to auto-generate labels.

    Returns:
    --------
    dict : {category_label: percentage}

    Example:
    --------
    # Elk analysis
    results = slope_passability_report(
        slope,
        thresholds=(5, 15, 35, 45),
        category_labels=[
            "Flat — preferred (0-5°)",
            "Gentle — easy movement (5-15°)",
            "Moderate — passable (15-35°)",
            "Steep — elk barrier (35-45°)",
            "Impassable — cliffs (>45°)"
        ]
    )
    passable_pct = results["Flat — preferred (0-5°)"] + \
                   results["Gentle — easy movement (5-15°)"] + \
                   results["Moderate — passable (15-35°)"]
    print(f"Suitable for elk: {passable_pct:.1f}%")
    """
    t1, t2, t3, t4 = thresholds

    if category_labels is None:
        category_labels = [
            f"Flat (0-{t1}°)",
            f"Gentle ({t1}-{t2}°)",
            f"Moderate ({t2}-{t3}°)",
            f"Steep ({t3}-{t4}°)",
            f"Impassable (>{t4}°)"
        ]

    classified = classify_slope(slope_da, thresholds=thresholds)
    total = float((~np.isnan(slope_da.values)).sum())

    results = {}
    for code, label in enumerate(category_labels, start=1):
        count = float((classified.values == code).sum())
        pct = (count / total) * 100
        results[label] = pct

    print("Slope Passability Breakdown:")
    print("-" * 50)
    for label, pct in results.items():
        bar = "█" * int(pct / 2)
        print(f"  {label:<35} {pct:>5.1f}%  {bar}")

    return results
```

### Step 3: Query Examples

#### Example 1: Get DEM and Basic Elevation Statistics

```python
import py3dep
import geopandas as gpd
import numpy as np

# Define region (e.g., from national-parks SKILL or any GeoDataFrame)
# park_gdf = get_park_by_name("Rocky Mountain")

resolution = get_safe_resolution(park_gdf)          # auto-select safe resolution
dem = get_dem(park_gdf, resolution=resolution)
stats = get_terrain_stats(dem)

print(f"Resolution used: {resolution}m")
print(f"Elevation Statistics:")
print(f"  Minimum : {stats['min']:.0f} m  ({stats['min_ft']:.0f} ft)")
print(f"  Maximum : {stats['max']:.0f} m  ({stats['max_ft']:.0f} ft)")
print(f"  Mean    : {stats['mean']:.0f} m  ({stats['mean_ft']:.0f} ft)")
print(f"  Std Dev : {stats['std']:.0f} m")
```

#### Example 2: Compute Slope and Find Passable Areas

```python
resolution = get_safe_resolution(park_gdf)
terrain = get_terrain_layers(park_gdf, layers=["Slope Degrees"], resolution=resolution)
slope = terrain["Slope Degrees"]

# --- General breakdown (default thresholds) ---
results = slope_passability_report(slope)

# --- Elk-specific analysis ---
elk_results = slope_passability_report(
    slope,
    thresholds=(5, 15, 35, 45),
    category_labels=[
        "Flat — preferred forage (0-5°)",
        "Gentle — easy movement (5-15°)",
        "Moderate — passable (15-35°)",
        "Steep — elk barrier (35-45°)",
        "Impassable — cliffs (>45°)"
    ]
)
suitable = sum(v for k, v in elk_results.items() if "barrier" not in k and "Impassable" not in k)
print(f"\nSuitable for elk (<35°): {suitable:.1f}%")
print(f"Too steep for elk (>35°): {100 - suitable:.1f}%")

# --- Pronghorn analysis (very sensitive to slope) ---
pronghorn_results = slope_passability_report(
    slope,
    thresholds=(5, 10, 15, 20),
    category_labels=[
        "Flat — ideal (0-5°)",
        "Gentle — usable (5-10°)",
        "Moderate — marginal (10-15°)",
        "Steep — pronghorn barrier (15-20°)",
        "Impassable for pronghorn (>20°)"
    ]
)
```

#### Example 3: Find Areas Within an Elevation Range

```python
# Find alpine habitat zone (2500m - 4000m) in Rocky Mountains
resolution = get_safe_resolution(rocky_mountain_gdf)
dem = get_dem(rocky_mountain_gdf, resolution=resolution)

# Define elevation zones
zones = {
    "Lowland (<1500m)"       : (dem < 1500),
    "Montane (1500-2500m)"   : ((dem >= 1500) & (dem < 2500)),
    "Subalpine (2500-3500m)" : ((dem >= 2500) & (dem < 3500)),
    "Alpine (>3500m)"        : (dem >= 3500),
}

total = float((~np.isnan(dem.values)).sum())
print("Elevation zone distribution:")
for zone, mask in zones.items():
    pct = float(mask.sum()) / total * 100
    print(f"  {zone:<30}: {pct:.1f}%")
```

#### Example 4: Multi-Layer Terrain Analysis

```python
# Get DEM, slope, aspect, and hillshade together
resolution = get_safe_resolution(region_gdf)
terrain = get_terrain_layers(
    region_gdf,
    layers=["DEM", "Slope Degrees", "Aspect Degrees", "Hillshade", "Roughness"],
    resolution=resolution
)

dem    = terrain["DEM"]
slope  = terrain["Slope Degrees"]
aspect = terrain["Aspect Degrees"]

# Aspect analysis — what direction does terrain face?
aspect_vals = aspect.values
valid_aspect = aspect_vals[aspect_vals >= 0]  # -1 = flat, exclude

aspect_zones = {
    "North (315-360° or 0-45°)": ((valid_aspect >= 315) | (valid_aspect < 45)).sum(),
    "East  (45-135°)"          : ((valid_aspect >= 45)  & (valid_aspect < 135)).sum(),
    "South (135-225°)"         : ((valid_aspect >= 135) & (valid_aspect < 225)).sum(),
    "West  (225-315°)"         : ((valid_aspect >= 225) & (valid_aspect < 315)).sum(),
}

total_aspect = sum(aspect_zones.values())
print("Aspect distribution (slope direction):")
for direction, count in aspect_zones.items():
    print(f"  {direction}: {count/total_aspect*100:.1f}%")

# Roughness stats
roughness = terrain["Roughness"]
print(f"\nTerrain roughness:")
print(f"  Mean roughness : {float(roughness.mean()):.1f} m")
print(f"  Max roughness  : {float(roughness.max()):.1f} m")
```

#### Example 5: Terrain Suitability for Wildlife Corridors

```python
# Build terrain suitability combining elevation and slope
# for multiple species simultaneously
resolution = get_safe_resolution(region_gdf)
terrain = get_terrain_layers(
    region_gdf,
    layers=["DEM", "Slope Degrees"],
    resolution=resolution
)

dem   = terrain["DEM"]
slope = terrain["Slope Degrees"]

# Elevation filter — Rocky Mountain species ranges
elevation_suitable = ((dem >= 1500) & (dem <= 3800))

# Species-specific slope passability
species = {
    "Elk"         : (5, 15, 35, 45),
    "Pronghorn"   : (5, 10, 15, 20),
    "Grizzly Bear": (5, 15, 35, 50),
    "Mountain Lion": (5, 20, 45, 60),
}

print("Terrain suitability by species (elevation + slope):")
print("-" * 55)
for name, thresholds in species.items():
    classified = classify_slope(slope, thresholds=thresholds)
    # Passable = categories 1, 2, 3 (codes < 4)
    slope_passable = (classified <= 3)
    # Combined suitability
    suitable = elevation_suitable & slope_passable
    total = float((~np.isnan(dem.values)).sum())
    pct = float(suitable.sum()) / total * 100
    print(f"  {name:<16}: {pct:.1f}% of area suitable")
```

#### Example 6: Visualize Terrain

```python
import matplotlib.pyplot as plt

resolution = get_safe_resolution(region_gdf)
terrain = get_terrain_layers(
    region_gdf,
    layers=["DEM", "Slope Degrees", "Hillshade"],
    resolution=resolution
)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# DEM
terrain["DEM"].plot(ax=axes[0], cmap="terrain",
                    cbar_kwargs={"label": "Elevation (m)"})
axes[0].set_title("Digital Elevation Model")
axes[0].set_axis_off()

# Slope
terrain["Slope Degrees"].plot(ax=axes[1], cmap="YlOrRd",
                               cbar_kwargs={"label": "Slope (degrees)"})
axes[1].set_title("Slope")
axes[1].set_axis_off()

# Hillshade
terrain["Hillshade"].plot(ax=axes[2], cmap="gray",
                           cbar_kwargs={"label": "Hillshade"})
axes[2].set_title("Hillshade")
axes[2].set_axis_off()

plt.suptitle("Terrain Analysis", fontsize=14)
plt.tight_layout()
plt.savefig("terrain_analysis.png", dpi=150, bbox_inches="tight")
plt.show()
```

## Notes

### Resolution Guidelines

**Streamlit Community Tier: 1GB total memory. Target <500K pixels per raster layer.**

Always call `get_safe_resolution()` — never hardcode resolution for unknown area sizes.

| Area | Approx Size | Safe Resolution | ~Pixels |
|------|------------|----------------|---------|
| Small park / local buffer | <100 sq km | 10–30m | <500K |
| National park / county | 100–500 sq km | 30m | ~300K–500K |
| State highway buffer (e.g. I-80 CA) | ~3,200 sq km | 80–100m | ~300K–500K |
| Whole state (e.g. California) | ~400,000 sq km | 1000m+ | ~400K |
| Multi-state (Rockies) | >1M sq km | 2000m+ | ~250K |

**Memory breakdown for 1GB app:**

```
Python runtime + app overhead  : ~400MB
Geodata (GeoDataFrames, etc.)  : ~100MB
Raster headroom (safe limit)   : ~200MB
─────────────────────────────────────────
Available for terrain rasters  : ~200MB
Per layer at 500K pixels       : ~8MB raw + ~40MB processing overhead
Safe simultaneous layers       : 2–3 maximum
```

### Elevation Conversions

```python
# Meters to feet
feet = meters * 3.28084

# Common Rocky Mountain elevations in meters
# Treeline:    ~3500m (11,500 ft)
# Alpine zone: 3500m+ (11,500 ft+)
# 14ers:       4267m+ (14,000 ft+)
```

### Slope Thresholds by Species and Application

```python
# Pass directly to classify_slope(slope, thresholds=(...))
# or slope_passability_report(slope, thresholds=(...))
```

| Species / Use Case | Thresholds (t1, t2, t3, t4) | Barrier at |
|-------------------|----------------------------|------------|
| Elk, mule deer | `(5, 15, 35, 45)` | >35° |
| Pronghorn | `(5, 10, 15, 20)` | >15° |
| Bison | `(3, 8, 12, 20)` | >12° |
| Grizzly bear | `(5, 15, 35, 50)` | >35° |
| Mountain lion | `(5, 20, 45, 60)` | >45° |
| Wolverine | `(5, 20, 45, 60)` | >45° |
| General large mammal | `(5, 15, 30, 45)` | >30° (default) |
| Road construction | `(2, 5, 10, 15)` | >10° |
| Agriculture | `(2, 5, 8, 12)` | >8° |

### Aspect Interpretation

- **North-facing (315–45°)**: Cooler, more snow, denser forest — preferred by some species
- **South-facing (135–225°)**: Warmer, drier, more shrub/grass — preferred by others
- **East/West**: Intermediate conditions
- **-1**: Flat terrain (no dominant aspect)

### Integration with Other SKILL.md Files

This terrain skill is a key building block for complex analyses:

**wildlife-corridors analysis:**
```python
# Terrain feeds directly into resistance surface
terrain  = get_terrain_layers(rockies_gdf, ["DEM", "Slope Degrees"])
lulc     = gh.nlcd_bygeom(rockies_gdf, resolution=30)   # nlcd-land-cover SKILL
# Combine into resistance surface → corridor analysis
```

**national-parks SKILL:**
```python
# Get terrain for a park
park = get_park_by_name("Yellowstone")
dem  = get_dem(park, resolution=30)
```

**lakes SKILL:**
```python
# Understand elevation context of lakes
lake = get_lakes_by_name("Grand Lake", state="CO")
dem  = get_dem(lake, resolution=10)
stats = get_terrain_stats(dem)
print(f"Lake elevation: {stats['mean_ft']:.0f} ft")
```

**freeway-system SKILL:**
```python
# Get terrain along a highway corridor
i70_ca  = get_highways_in_region("NUMBER = '70' AND CLASS = 'I'", colorado_gdf)
buffer  = make_buffer(i70_ca, km=1)
terrain = get_terrain_layers(buffer, ["DEM", "Slope Degrees"])
# → use elevation-path-analysis for the profile along the route itself
```
