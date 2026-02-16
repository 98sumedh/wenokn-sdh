---
name: weather-forecast-nws
description: Retrieves hourly weather forecasts (temperature, precipitation, wind, humidity, sky cover, etc.) for US locations using the National Weather Service gridded data API.
---

# weather-forecast-nws Skill

## Description
Fetches hourly weather forecast data for one or more US geographic locations from the National Weather Service (NWS) gridded forecast data API:
```
https://api.weather.gov
```

**Returns:** GeoDataFrame that joins the input locations with weather forecast data. Each row represents one forecast time period for one location. Columns include `forecast_time_start`, `forecast_time_end`, `duration_hours`, and the requested weather variables.

**Important:** Each row represents a forecast time period (not necessarily one hour - periods can be 1-6 hours). The same location will appear multiple times (once per forecast period).

## Critical API Notes
- **US locations only** - coordinates must be within the United States
- **User-Agent required** - Must include identification (email recommended)
- **Response structure**: Three-step process (points → grid metadata → gridded forecast data)
- **Data structure**: Each variable has a `values` list containing objects with `validTime` and `value` keys
- **validTime format**: "start_time/duration" (ISO 8601), e.g., "2026-01-03T14:00:00+00:00/PT6H" means 6-hour period starting at that time
- **Forecast coverage**: ~156 hours (6.5 days) 
- **Timezone**: All times in UTC with offset (e.g., "2026-01-04T00:00:00+00:00")
- **Delay recommendation**: 1 second between requests

## Available Variables

### Precipitation (Quantitative)
- `quantitativePrecipitation` - Actual precipitation amount (mm) over the period
- `probabilityOfPrecipitation` - Probability of precipitation (%)
- `iceAccumulation` - Ice accumulation (mm)
- `snowfallAmount` - Snowfall amount (mm)

### Temperature
- `temperature` - Air temperature (°C)
- `apparentTemperature` - Apparent/feels-like temperature (°C)
- `dewpoint` - Dew point temperature (°C)
- `maxTemperature` - Maximum temperature (°C)
- `minTemperature` - Minimum temperature (°C)

### Wind
- `windSpeed` - Wind speed (km/h)
- `windDirection` - Wind direction (degrees)
- `windGust` - Wind gust speed (km/h)

### Sky & Visibility
- `skyCover` - Sky/cloud cover (%)
- `visibility` - Visibility distance (m)

### Atmospheric
- `relativeHumidity` - Relative humidity (%)
- `pressure` - Atmospheric pressure (Pa)

**Note:** All units are metric (°C, mm, km/h, etc.).

## Usage

### Function Setup
```python
import time
import requests
import pandas as pd
import geopandas as gpd
from datetime import datetime

def parse_iso_duration(duration_str):
    """Parse ISO 8601 duration (e.g., 'PT6H') to hours as float."""
    if not duration_str or not duration_str.startswith('PT'):
        return 1.0
    
    hours = 0
    if 'H' in duration_str:
        hours = float(duration_str.split('PT')[1].split('H')[0])
    return hours

def fetch_weather_forecast_nws(
    locations_gdf: gpd.GeoDataFrame,
    user_agent: str,
    variables: list = None,
    delay_between_requests: float = 1.0
) -> gpd.GeoDataFrame:
    """Fetch weather forecast data for US geographic locations using NWS gridded data API.
    
    Args:
        locations_gdf: GeoDataFrame with Point geometries (must have geometry column)
        user_agent: Required user agent string (e.g., "myapp.com, contact@email.com")
        variables: List of forecast variables to extract 
                  (default: ['temperature', 'quantitativePrecipitation', 'windSpeed'])
        delay_between_requests: Seconds to wait between API requests (default: 1.0)
    
    Returns:
        GeoDataFrame joining input locations with weather forecasts.
        Each input row is duplicated for each forecast period.
        Adds columns: forecast_time_start, forecast_time_end, duration_hours, and requested variables
    """
    
    # Default variables if none specified
    if variables is None:
        variables = ['temperature', 'quantitativePrecipitation', 'windSpeed']
    
    # Setup headers
    headers = {
        'User-Agent': user_agent,
        'Accept': 'application/geo+json'
    }
    
    # Create list to store forecast DataFrames for each location
    forecast_dfs = []
    
    for idx, row in locations_gdf.iterrows():
        # Extract coordinates from Point geometry
        lon = row.geometry.x
        lat = row.geometry.y
        
        try:
            # Step 1: Get grid point information
            points_url = f'https://api.weather.gov/points/{lat:.4f},{lon:.4f}'
            points_response = requests.get(points_url, headers=headers, timeout=30)
            points_response.raise_for_status()
            points_data = points_response.json()
            
            # Step 2: Extract gridded forecast URL
            forecast_grid_url = points_data['properties']['forecastGridData']
            
            # Step 3: Get gridded forecast data
            time.sleep(delay_between_requests)
            grid_response = requests.get(forecast_grid_url, headers=headers, timeout=30)
            grid_response.raise_for_status()
            grid_data = grid_response.json()
            
            properties = grid_data['properties']
            
            # Collect all forecast periods from all variables
            # Use a dict to store values by time period
            periods_dict = {}
            
            for var in variables:
                if var not in properties:
                    continue
                
                # Access the variable data - it's a dict with 'values' key
                var_info = properties[var]
                if not isinstance(var_info, dict) or 'values' not in var_info:
                    continue
                
                values_list = var_info['values']
                
                for value_obj in values_list:
                    valid_time = value_obj.get('validTime', '')
                    value = value_obj.get('value')
                    
                    if '/' not in valid_time:
                        continue
                    
                    # Parse validTime: "2026-01-03T14:00:00+00:00/PT6H"
                    start_time_str, duration_str = valid_time.split('/')
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    duration_hours = parse_iso_duration(duration_str)
                    
                    # Create period key
                    period_key = (start_time, duration_hours)
                    
                    # Initialize period if not exists
                    if period_key not in periods_dict:
                        periods_dict[period_key] = {
                            'forecast_time_start': start_time.isoformat(),
                            'duration_hours': duration_hours
                        }
                    
                    # Add variable value
                    periods_dict[period_key][var] = value
            
            if not periods_dict:
                print(f'No forecast data available for location index {idx}')
                continue
            
            # Convert periods dict to list of records
            forecast_records = []
            for (start_time, duration_hours), period_data in sorted(periods_dict.items()):
                record = period_data.copy()
                
                # Calculate end time
                end_time = start_time + timedelta(hours=duration_hours)
                record['forecast_time_end'] = end_time.isoformat()
                
                # Add any missing variables as None
                for var in variables:
                    if var not in record:
                        record[var] = None
                
                # Copy all original columns from input location
                for col in locations_gdf.columns:
                    if col != 'geometry':
                        record[col] = row[col]
                
                forecast_records.append(record)
            
            if forecast_records:
                forecast_df = pd.DataFrame(forecast_records)
                forecast_df['_join_idx'] = idx
                # Preserve geometry
                forecast_df['geometry'] = row.geometry
                forecast_dfs.append(forecast_df)
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f'Location index {idx} (lat={lat}, lon={lon}) is outside US boundaries or invalid')
            else:
                print(f'HTTP error fetching data for location index {idx}: {e}')
            continue
        except (KeyError, ValueError) as e:
            print(f'Error parsing forecast data for location index {idx}: {e}')
            continue
        except requests.RequestException as e:
            print(f'Error fetching data for location index {idx} (lat={lat}, lon={lon}): {e}')
            continue
    
    if not forecast_dfs:
        # Return empty GeoDataFrame with expected columns
        result_gdf = locations_gdf.copy()
        result_gdf['forecast_time_start'] = None
        result_gdf['forecast_time_end'] = None
        result_gdf['duration_hours'] = None
        for var in variables:
            result_gdf[var] = None
        return result_gdf.iloc[0:0]
    
    # Combine all forecast data
    all_forecasts = pd.concat(forecast_dfs, ignore_index=True)
    
    # Remove temporary join column if exists
    if '_join_idx' in all_forecasts.columns:
        all_forecasts = all_forecasts.drop(columns=['_join_idx'])
    
    # Ensure it's a GeoDataFrame with proper CRS
    result_gdf = gpd.GeoDataFrame(all_forecasts, geometry='geometry', crs=locations_gdf.crs)
    
    return result_gdf
```

### Examples

#### Basic Usage - Get Precipitation Forecast
```python
from shapely.geometry import Point
import geopandas as gpd
from datetime import datetime, timezone, timedelta

# Single US location
locations = gpd.GeoDataFrame(
    geometry=[Point(-79.647778, 41.050556)],  # Bowser Mine, PA
    crs="EPSG:4326"
)

user_agent = "WENOKN (admin@wenokn.org)"
variables = ['quantitativePrecipitation', 'probabilityOfPrecipitation']

df = fetch_weather_forecast_nws(locations, user_agent=user_agent, variables=variables)

# Convert times to datetime for filtering
df['start_dt'] = pd.to_datetime(df['forecast_time_start'])
df['end_dt'] = pd.to_datetime(df['forecast_time_end'])

# Filter to next 6 hours
now = datetime.now(timezone.utc)
six_hours_later = now + timedelta(hours=6)
next_6h = df[(df['start_dt'] >= now) & (df['start_dt'] < six_hours_later)]

print(next_6h[['forecast_time_start', 'duration_hours', 'quantitativePrecipitation', 'probabilityOfPrecipitation']])
```

#### Multiple Locations
```python
locations = gpd.GeoDataFrame(
    geometry=[
        Point(-82.966956, 40.102520),  # Columbus, OH
        Point(-82.743058, 41.342046),  # Cleveland, OH
    ],
    crs="EPSG:4326"
)

variables = ['temperature', 'quantitativePrecipitation', 'windSpeed']
df = fetch_weather_forecast_nws(locations, user_agent=user_agent, variables=variables)

# Convert times
df['start_dt'] = pd.to_datetime(df['forecast_time_start'])

# Find periods with precipitation > 0
precip_periods = df[df['quantitativePrecipitation'] > 0]
print(precip_periods[['start_dt', 'quantitativePrecipitation']])
```

#### Filter Forecast by Date/Time Range
```python
df = fetch_weather_forecast_nws(locations, user_agent=user_agent)

# Convert to datetime
df['start_dt'] = pd.to_datetime(df['forecast_time_start'])
df['end_dt'] = pd.to_datetime(df['forecast_time_end'])

# Filter to next 24 hours
now = datetime.now(timezone.utc)
next_24h = now + timedelta(hours=24)
df_24h = df[(df['start_dt'] >= now) & (df['start_dt'] < next_24h)]

print(f"Periods in next 24 hours: {len(df_24h)}")
print(df_24h[['start_dt', 'temperature', 'quantitativePrecipitation']])
```

#### Calculate Total Precipitation for a Location
```python
# Get precipitation forecast for single location
variables = ['quantitativePrecipitation']
df = fetch_weather_forecast_nws(locations, user_agent=user_agent, variables=variables)

# Total precipitation across all forecast periods
total_precip = df['quantitativePrecipitation'].sum()
print(f"Total expected precipitation: {total_precip:.2f} mm")

# If multiple locations, group by location
# (each location will have same number of forecast periods)
num_periods = len(df) // len(locations)
df['location_idx'] = df.index // num_periods
totals = df.groupby('location_idx')['quantitativePrecipitation'].sum()
print("\nTotal by location:")
print(totals)
```

#### Using with Custom Location Attributes
```python
# Create locations with attributes
locations = gpd.GeoDataFrame({
    'site_name': ['Mine A', 'Mine B'],
    'site_type': ['coal', 'coal'],
    'geometry': [Point(-79.647778, 41.050556), Point(-80.0, 40.0)]
}, crs="EPSG:4326")

# Fetch forecast - original columns preserved
variables = ['quantitativePrecipitation', 'temperature']
df = fetch_weather_forecast_nws(locations, user_agent=user_agent, variables=variables)

# Convert time for display
df['start_dt'] = pd.to_datetime(df['forecast_time_start'])

print(df[['site_name', 'start_dt', 'temperature', 'quantitativePrecipitation']].head(10))
```

### Understanding the Results

- Each row represents one forecast time period for one location
- **Periods are not always 1 hour** - can be 1-6 hours depending on the forecast
- `duration_hours` shows how long each period lasts
- `forecast_time_start` and `forecast_time_end` define the period boundaries
- `quantitativePrecipitation` is the total amount (mm) expected during that period
- All columns from input GeoDataFrame are preserved
- Times are in ISO 8601 format with UTC timezone offset
- All units are metric: °C, mm, km/h, %, Pa

### Working with Time Periods

```python
from datetime import datetime, timezone, timedelta

# After fetching forecast
df = fetch_weather_forecast_nws(locations, user_agent=user_agent)

# Convert time strings to datetime objects
df['start_dt'] = pd.to_datetime(df['forecast_time_start'])
df['end_dt'] = pd.to_datetime(df['forecast_time_end'])

# Check if a specific datetime falls within a forecast period
target_time = datetime(2026, 1, 4, 12, 0, tzinfo=timezone.utc)
matching = df[(df['start_dt'] <= target_time) & (df['end_dt'] > target_time)]

# Get forecast for next N hours
now = datetime.now(timezone.utc)
hours_ahead = 12
cutoff = now + timedelta(hours=hours_ahead)
next_n_hours = df[(df['start_dt'] >= now) & (df['start_dt'] < cutoff)]

# Calculate hourly rate (if needed for comparison)
df['precip_rate_per_hour'] = df['quantitativePrecipitation'] / df['duration_hours']
```

### API Limitations

- **US ONLY**: Coordinates outside US boundaries return 404 errors
- **User-Agent Required**: Must provide identification string
- **Variable Period Lengths**: Forecast periods are 1-6 hours, not uniform
- **Forecast Range**: ~156 hours (6.5 days)
- **Three API Calls**: Requires three requests per location
- **Data Sparsity**: Some variables may have fewer periods than others

### Best Practices

```python
# Always provide descriptive user agent
user_agent = "WENOKN (admin@wenokn.com)"

# For multiple locations, use delay between requests
df = fetch_weather_forecast_nws(
    locations, 
    user_agent=user_agent,
    delay_between_requests=1.0
)

# Validate US coordinates before calling
us_bounds = {
    'lat_min': 24.0, 'lat_max': 49.0,
    'lon_min': -125.0, 'lon_max': -66.0
}

locations_us = locations[
    (locations.geometry.y >= us_bounds['lat_min']) &
    (locations.geometry.y <= us_bounds['lat_max']) &
    (locations.geometry.x >= us_bounds['lon_min']) &
    (locations.geometry.x <= us_bounds['lon_max'])
]

# Handle missing values
df = df.fillna(0)
```

### Variable Selection Tips

**For precipitation:**
```python
['quantitativePrecipitation', 'probabilityOfPrecipitation']
```

**For general weather:**
```python
['temperature', 'quantitativePrecipitation', 'windSpeed', 'skyCover']
```

**For winter weather:**
```python
['temperature', 'quantitativePrecipitation', 'snowfallAmount', 'iceAccumulation']
```

**For wind analysis:**
```python
['windSpeed', 'windDirection', 'windGust']
```

## Additional Resources

- **NWS API Documentation**: https://www.weather.gov/documentation/services-web-api
- **Gridpoints FAQ**: https://weather-gov.github.io/api/gridpoints
- **API GitHub**: https://github.com/weather-gov/api
