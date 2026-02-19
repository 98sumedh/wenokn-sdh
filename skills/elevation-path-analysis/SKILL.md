---
name: elevation-path-analysis
description: Analyze elevation along GPS paths using USGS 3DEP via Py3DEP. Calculate average elevation, generate profile charts, export CSV data. Handles single/multi-waypoint routes with comprehensive statistics for terrain analysis.
---

# Elevation Path Analysis Skill

## Description

Analyze elevation along paths defined by GPS coordinates using Py3DEP (HyRiver) to access USGS 3DEP data. Calculate average elevation, generate elevation profile charts, and export detailed CSV data with comprehensive statistics.

## When to Use

- When a user asks "What is the average elevation along this path/route?"
- When analyzing elevation profiles for hiking trails, cycling routes, or running paths
- When planning infrastructure projects that require terrain analysis
- When comparing elevation characteristics of different routes
- When creating elevation visualizations for reports or presentations
- When calculating elevation gain/loss for fitness or navigation purposes
- When conducting geographic or topographic research
- When assessing flood risk or drainage patterns along a path

## Prerequisites

### Required Python Packages

```bash
pip install py3dep geopandas shapely matplotlib numpy pandas --break-system-packages
```

### System Requirements

- Python 3.8 or higher
- Network access to download DEM data from USGS 3DEP
- Sufficient disk space for temporary DEM files (varies by path length)

### Input Requirements

- GPS coordinates in decimal degrees format: `(latitude, longitude)`
- Minimum of 2 coordinate points to define a path
- Coordinates must be within areas covered by USGS 3DEP (primarily United States)

### Important API Note

**The `py3dep.elevation_bycoords()` function does NOT accept a `resolution` parameter.**
It uses the default resolution from the 3DEP service. Do not attempt to specify resolution.

## How to Use

### Step 1: Understand the Coordinate Format

GPS coordinates must be provided as `(latitude, longitude)` tuples:
```python
# Correct format
coordinates = [
    (34.0522, -118.2437),  # Los Angeles (lat, lon)
    (36.7783, -119.4179)   # Fresno (lat, lon)
]

# INCORRECT - Do not use (longitude, latitude)
wrong_coords = [(-118.2437, 34.0522)]  # This will fail!
```

### Step 2: Choose Your Approach

**Option A - Quick Analysis (for simple requests):**
Use `quick_elevation.py` for straightforward two-point paths or when the user just wants a quick answer.

**Option B - Full Analysis (for complex requests):**
Use `ElevationPathAnalyzer` class from `elevation_path_analyzer.py` for:
- Multi-waypoint routes
- Custom analysis workflows
- Advanced visualizations
- Integration into larger projects

### Step 3: Run the Analysis

The analysis pipeline executes these steps automatically:
1. Interpolates points along the path
2. Fetches DEM data from USGS 3DEP
3. Extracts elevation at each point
4. Calculates distances using Haversine formula
5. Computes statistics
6. Generates elevation profile chart
7. Exports data to CSV

## Implementation Patterns

### Pattern 1: Simple Two-Point Path

**User Request:** "What is the average elevation between Los Angeles and Fresno?"

**Approach:**
1. Extract the two GPS coordinates
2. Use the analyzer class
3. Return the average elevation value and profile chart

```python
from elevation_path_analyzer import ElevationPathAnalyzer

coordinates = [
    (34.0522, -118.2437),  # Los Angeles
    (36.7783, -119.4179)   # Fresno
]

analyzer = ElevationPathAnalyzer(coordinates, num_samples=50)
stats = analyzer.run_complete_analysis()

print(f"Average elevation: {stats['average_elevation_m']:.2f} m")
```

**Expected outcome:** 
- Average elevation value in meters and feet
- Elevation profile chart saved to outputs
- Detailed CSV data file

### Pattern 2: Multi-Waypoint Route

**User Request:** "Analyze elevation for a road trip from LA through Bakersfield to Fresno"

**Approach:**
1. Collect all waypoint coordinates in order
2. Use higher sample count for longer paths
3. Enable waypoint markers on the visualization

```python
coordinates = [
    (34.0522, -118.2437),  # Los Angeles
    (35.3733, -119.0187),  # Bakersfield
    (36.7783, -119.4179)   # Fresno
]

analyzer = ElevationPathAnalyzer(coordinates, num_samples=100)
stats = analyzer.run_complete_analysis(
    title="LA → Bakersfield → Fresno Elevation Profile"
)
```

**Expected result:** Multi-segment elevation profile with waypoint markers

### Pattern 3: High-Resolution Trail Analysis

**User Request:** "I need detailed elevation data for this hiking trail with these coordinates"

**Approach:**
1. Use high sample count for detailed analysis
2. Calculate elevation gain for trail difficulty assessment

```python
trail_coords = [
    (36.5783, -118.2923),  # Trailhead
    (36.5785, -118.2915),  # Checkpoint 1
    (36.5786, -118.2900),  # Checkpoint 2
    (36.5786, -118.2920)   # Summit
]

analyzer = ElevationPathAnalyzer(trail_coords, num_samples=200)
stats = analyzer.run_complete_analysis()

# Additional trail-specific calculations
elevation_gain = stats['elevation_gain_m']
print(f"Total elevation gain: {elevation_gain:.0f} m ({elevation_gain*3.28084:.0f} ft)")
```

**Expected result:** Detailed elevation profile suitable for trail difficulty assessment

### Pattern 4: Custom Analysis Workflow

**User Request:** "Get elevation data but I want to process it myself before creating charts"

**Approach:**
1. Use step-by-step methods instead of `run_complete_analysis()`
2. Access raw data arrays for custom processing
3. Create custom visualizations or exports

```python
analyzer = ElevationPathAnalyzer(coordinates, num_samples=50)

# Step-by-step execution
analyzer.interpolate_path()
analyzer.get_elevations_py3dep()  # No resolution parameter
analyzer.calculate_distances()

# Access raw data
elevations = analyzer.elevations  # numpy array
distances = analyzer.distances    # numpy array
points = analyzer.path_points     # list of (lat, lon)

# Custom processing
slope_angles = np.diff(elevations) / np.diff(distances * 1000)  # gradient

# Then create visualizations
analyzer.plot_elevation_profile(title="Custom Analysis")
analyzer.export_to_csv()
```

**Expected result:** Full control over analysis pipeline with access to intermediate data

### Pattern 5: Batch Route Comparison

**User Request:** "Compare elevation profiles of three different routes between the same start and end points"

**Approach:**
1. Define multiple routes with different waypoints
2. Analyze each route separately
3. Compare average elevations and elevation gains

```python
route1_coords = [(34.0522, -118.2437), (36.7783, -119.4179)]  # Direct
route2_coords = [(34.0522, -118.2437), (35.3733, -119.0187), (36.7783, -119.4179)]  # Via Bakersfield
route3_coords = [(34.0522, -118.2437), (35.1500, -118.5000), (36.7783, -119.4179)]  # Mountain route

routes = [route1_coords, route2_coords, route3_coords]
results = []

for i, coords in enumerate(routes, 1):
    analyzer = ElevationPathAnalyzer(coords, num_samples=50)
    stats = analyzer.run_complete_analysis(
        title=f"Route {i} Elevation Profile"
    )
    results.append(stats)

# Compare results
for i, stats in enumerate(results, 1):
    print(f"Route {i}: Avg elevation = {stats['average_elevation_m']:.0f} m, "
          f"Gain = {stats['elevation_gain_m']:.0f} m")
```

**Expected result:** Comparative analysis of multiple routes

## Best Practices

### Sample Point Selection

- **Short paths (<50km)**: 50 samples
- **Medium paths (50-200km)**: 50-100 samples
- **Long paths (>200km)**: 100-200 samples
- **Detailed trail analysis**: 150-300 samples

### Performance Optimization

- Start with 25-50 samples for initial exploration
- Increase to 100+ samples for final analysis
- More sample points = more API calls = longer processing time

### Error Handling

Always wrap API calls in try-catch blocks:
```python
try:
    analyzer.get_elevations_py3dep()
except Exception as e:
    print(f"Error fetching elevation data: {e}")
    print("Try reducing num_samples or check network connection")
```

### Coordinate Validation

Verify coordinates are in the correct format and valid range:
```python
def validate_coordinates(coords):
    for lat, lon in coords:
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Invalid longitude: {lon}")
```

## Output Files and Statistics

### Generated Files

1. **elevation_profile.png** - High-resolution elevation chart with:
   - Main elevation profile with gradient fill
   - Average elevation reference line
   - Dual axes (meters/feet, kilometers/miles)
   - Peak/valley annotations
   - Waypoint markers (for multi-point paths)

2. **elevation_data.csv** - Complete dataset with columns:
   - Point number
   - Latitude, Longitude
   - Distance (km and miles)
   - Elevation (meters and feet)

### Available Statistics

The `get_statistics()` method returns:
- `average_elevation_m` - Mean elevation in meters
- `average_elevation_ft` - Mean elevation in feet
- `median_elevation_m` - Median elevation
- `min_elevation_m` - Lowest point
- `max_elevation_m` - Highest point
- `std_elevation_m` - Standard deviation
- `elevation_gain_m` - Total elevation change
- `total_distance_km` - Path length in kilometers
- `total_distance_mi` - Path length in miles
- `start_elevation_m` - Starting elevation
- `end_elevation_m` - Ending elevation
- `net_elevation_change_m` - Net elevation change

## Response Templates

### Simple Requests

User: "What's the average elevation from A to B?"

Response:
- State average elevation in meters and feet
- Include total distance, elevation range, and peak location
- Attach elevation_profile.png and elevation_data.csv

### Detailed Requests

User: "Comprehensive analysis needed"

Response:
- Lead with average elevation (meters and feet)
- Provide distance, elevation range, total gain, peak elevation
- Describe key terrain features (climb, descent, plateau)
- Attach files with note about CSV containing all sample points

## Troubleshooting

### Common Issues

**Import Error - Py3DEP not found:**
```bash
# Solution
pip install py3dep geopandas shapely matplotlib numpy pandas --break-system-packages
```

**API Error - "unexpected keyword argument 'resolution'":**
- The `elevation_bycoords()` function does NOT accept a resolution parameter
- Remove any `resolution=` arguments from the function call
- Use: `py3dep.elevation_bycoords(coords, crs="EPSG:4326")`

**Network/Download Errors:**
- Check internet connectivity
- Verify coordinates are within USGS 3DEP coverage area (primarily US)
- Reduce sample count if path is very long

**Coordinate Format Errors:**
```
Error: Coordinates must be (latitude, longitude), not (longitude, latitude)
Correct: (34.0522, -118.2437)
Wrong: (-118.2437, 34.0522)
```

**Memory Issues with Large Paths:**
- Reduce `num_samples` (try 50 instead of 200)
- Split very long paths into segments

**NaN Values in Results:**
- Some points may return NaN if outside coverage area
- The analyzer filters these out automatically
- Check `stats['valid_points']` vs `stats['total_points']`

### Debugging Steps

1. **Verify coordinates:**
   ```python
   print(f"Start: {coordinates[0]}")
   print(f"End: {coordinates[-1]}")
   ```

2. **Test with known working coordinates:**
   ```python
   # Test coordinates (Los Angeles)
   test_coords = [(34.0522, -118.2437), (34.0622, -118.2537)]
   ```

3. **Check package versions:**
   ```bash
   pip show py3dep geopandas shapely
   ```

4. **Verify USGS 3DEP service status:**
   Check https://www.usgs.gov/3d-elevation-program for service updates

## Notes

- USGS 3DEP data covers the United States, including Alaska, Hawaii, and territories
- For international locations, this approach may not work; alternative DEM sources needed
- Elevation values are in meters by default; conversions to feet are provided
- The Haversine formula provides accurate distance calculations for paths <500km
- For very long paths (>1000km), consider using geodesic distance calculations
- Processing time increases with more sample points
- The API uses default resolution from 3DEP service; resolution cannot be specified in `elevation_bycoords()`

## Advanced Usage

### Custom Visualization Styling

```python
# After analysis, customize the chart
analyzer.plot_elevation_profile(
    title="Custom Title",
    output_path="/custom/path.png",
    show_waypoints=True
)
```

### Integration with Other Tools

```python
# Export to GeoJSON for GIS applications
import geopandas as gpd
from shapely.geometry import LineString

line = LineString([(lon, lat) for lat, lon in analyzer.path_points])
gdf = gpd.GeoDataFrame([{'geometry': line, 'avg_elevation': stats['average_elevation_m']}])
gdf.to_file('elevation_path.geojson', driver='GeoJSON')
```

### Slope Analysis

```python
# Calculate slope between points
slopes = np.diff(analyzer.elevations) / (np.diff(analyzer.distances) * 1000)
avg_slope = np.mean(np.abs(slopes))
max_slope = np.max(np.abs(slopes))
print(f"Average slope: {avg_slope*100:.2f}%")
```
