---
name: precipitation-forecast
description: Retrieves hourly precipitation forecasts for geographic locations using the Open-Meteo API.
---

# precipitation-forecast Skill

## Description
Fetches hourly precipitation forecast data for one or more geographic locations from:
```
https://api.open-meteo.com/v1/forecast
```

**Returns:** GeoDataFrame that joins the input locations with precipitation forecast data. Each input location is duplicated for each forecast hour, with added columns: `forecast_time`, `precipitation_mm`, and `hour_offset`.

**Important:** Each row represents a single hour of precipitation forecast for a specific location. The same location will appear multiple times (once per forecast hour).

## Critical API Notes
- Free API with no authentication required
- Response structure: Hourly data under `data["hourly"]` with parallel arrays for `time` and `precipitation`
- Times are returned in ISO 8601 format in the requested timezone (default: UTC)
- Precipitation values are in millimeters (mm)
- Default forecast hours: 24 (configurable via `forecast_hours` parameter)

## Usage

### Function Setup
```python
def fetch_precipitation_forecast(
    locations_gdf: gpd.GeoDataFrame,
    forecast_hours: int = 24,
    timezone_str: str = "UTC"
) -> gpd.GeoDataFrame:
    """Fetch precipitation forecast data for geographic locations.
    
    Args:
        locations_gdf: GeoDataFrame with Point geometries (must have geometry column)
        forecast_hours: Number of hours to forecast (default: 24)
        timezone_str: Timezone for forecast times (default: "UTC")
    
    Returns:
        GeoDataFrame joining input locations with precipitation forecasts.
        Each input row is duplicated for each forecast hour.
        Adds columns: forecast_time, precipitation_mm, hour_offset
    """
    
    # Create list to store forecast DataFrames for each location
    forecast_dfs = []
    
    for idx, row in locations_gdf.iterrows():
        # Extract coordinates from Point geometry
        lon = row.geometry.x
        lat = row.geometry.y
        
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': 'precipitation',
            'forecast_hours': forecast_hours,
            'timezone': timezone_str
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract hourly precipitation data
            hourly = data.get('hourly', {})
            times = hourly.get('time', [])
            precipitations = hourly.get('precipitation', [])
            
            # Create DataFrame for this location's forecast
            if times and precipitations:
                forecast_df = pd.DataFrame({
                    'forecast_time': times,
                    'precipitation_mm': precipitations,
                    'hour_offset': range(len(times))
                })
                
                # Add index to join back to original row
                forecast_df['_join_idx'] = idx
                forecast_dfs.append(forecast_df)
                
        except requests.RequestException as e:
            print(f'Error fetching data for location index {idx} (lat={lat}, lon={lon}): {e}')
            continue
    
    if not forecast_dfs:
        # Return empty GeoDataFrame with expected columns
        result_gdf = locations_gdf.copy()
        result_gdf['forecast_time'] = None
        result_gdf['precipitation_mm'] = None
        result_gdf['hour_offset'] = None
        return result_gdf.iloc[0:0]  # Empty with all columns
    
    # Combine all forecast data
    all_forecasts = pd.concat(forecast_dfs, ignore_index=True)
    
    # Create temporary DataFrame from locations_gdf for joining
    locations_df = locations_gdf.copy()
    locations_df['_join_idx'] = locations_df.index
    
    # Perform the join
    result_gdf = locations_df.merge(
        all_forecasts,
        on='_join_idx',
        how='inner'
    )
    
    # Remove temporary join column
    result_gdf = result_gdf.drop(columns=['_join_idx'])
    
    # Ensure it's a GeoDataFrame with proper CRS
    result_gdf = gpd.GeoDataFrame(result_gdf, geometry='geometry', crs=locations_gdf.crs)
    
    return result_gdf
```

### Examples
```python
# Single location
from shapely.geometry import Point
import geopandas as gpd

locations = gpd.GeoDataFrame(
    geometry=[Point(-82.966956, 40.102520)],
    crs="EPSG:4326"
)
df = fetch_precipitation_forecast(locations, forecast_hours=24)

# Multiple locations
locations = gpd.GeoDataFrame(
    geometry=[
        Point(-82.966956, 40.102520),
        Point(-82.743058, 41.342046),
        Point(-80.731081, 41.602796)
    ],
    crs="EPSG:4326"
)
df = fetch_precipitation_forecast(locations, forecast_hours=48)

# Analysis: Hours with significant precipitation
significant = df[df['precipitation_mm'] > 1.0]

# Analysis: Total precipitation by location
summary = df.groupby(df.index // forecast_hours).agg({
    'precipitation_mm': ['max', 'sum', 'mean']
})
```

### Understanding the Results

- Each row represents one hour of precipitation forecast joined with one input location.
- For N input locations and H forecast hours, the result will have N × H rows.
- `hour_offset` indicates hours from now (0 = current hour, 1 = next hour, etc.).
- `precipitation_mm` values of 0.0 indicate no precipitation forecasted for that hour.
- All columns from the input GeoDataFrame are preserved, including geometry.
- `forecast_time` is in ISO 8601 format (e.g., "2025-12-30T14:00") in the specified timezone.

### Common Use Cases

**Combining with flood risk data:**
```python
# Get locations at flood risk
flood_locations_gdf = fetch_flood_impacts("2025123014", fips="county", feature_type="building", scope="39")

# Get precipitation forecast for those locations
precip_gdf = fetch_precipitation_forecast(flood_locations_gdf, forecast_hours=24)

# Now precip_gdf is a GeoDataFrame with all original columns (fips, feature-type, 
# date, geometry) plus precipitation forecast columns (forecast_time, precipitation_mm, 
# hour_offset) with one row per location per forecast hour

# Identify locations with heavy precipitation forecast (> 5mm/hour)
heavy_precip = precip_gdf[precip_gdf['precipitation_mm'] > 5.0]
```

**Using with custom locations:**
```python
# Create GeoDataFrame with custom attributes
locations = gpd.GeoDataFrame({
    'site_name': ['Site A', 'Site B'],
    'geometry': [Point(-82.5, 40.0), Point(-83.0, 41.0)]
}, crs="EPSG:4326")

# Fetch forecast - site_name will be included in results
precip_gdf = fetch_precipitation_forecast(locations)

# Result has geometry and site_name for each forecast hour
print(precip_gdf[['site_name', 'forecast_time', 'precipitation_mm']].head())
```

### API Limitations

- No authentication required (free tier)
- Rate limits apply but are generous for typical use cases
- Historical data available through different endpoint
- Maximum forecast range depends on model (typically 7-16 days)
- Precipitation accuracy decreases for longer forecast periods
