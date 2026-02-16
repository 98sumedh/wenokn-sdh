---
name: flooding-forecast
description: Fetch and analyze real-time US flooding alerts from NOAA/NWS API, convert to GeoDataFrame for spatial analysis.
---

# Flooding Forecast Skill

## Description

Retrieve current flood warnings, watches, and advisories for US locations using NOAA/NWS API. Convert alerts to GeoDataFrame with geometries for filtering and export.

## When to Use

- User asks about current flooding conditions (nationwide, state-level, or specific location)
- Need to identify active flood alerts by type or severity
- Task requires spatial data export (GeoJSON, Shapefile, GeoPackage)
- Analyzing flood alert coverage or geographic extent

## API Endpoint

Base URL: `https://api.weather.gov/alerts/active`

## Implementation

### Fetch Nationwide Alerts

```python
import requests

url = "https://api.weather.gov/alerts/active"
headers = {
    'User-Agent': '(YourApp, contact@youremail.com)',
    'Accept': 'application/geo+json'
}
params = {
    'event': 'Flood Warning,Flash Flood Warning,Flood Watch,Flash Flood Watch,Flood Advisory,Coastal Flood Warning,Coastal Flood Advisory'
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
```

### Fetch State-Specific Alerts

```python
params = {
    'area': 'CA',  # 2-letter state code
    'event': 'Flood Warning,Flash Flood Warning,Flood Watch,Flash Flood Watch,Flood Advisory'
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
```

### Fetch Location-Based Alerts

```python
params = {
    'point': f"{latitude},{longitude}",
    'event': 'Flood Warning,Flash Flood Warning,Flood Watch,Flash Flood Watch'
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
```

### Convert to GeoDataFrame

```python
import geopandas as gpd
from shapely.geometry import shape

alerts = data['features']
records = []
geometries = []

for alert in alerts:
    props = alert['properties']
    records.append({
        'id': props.get('id'),
        'event': props.get('event'),
        'severity': props.get('severity'),
        'certainty': props.get('certainty'),
        'urgency': props.get('urgency'),
        'headline': props.get('headline'),
        'description': props.get('description'),
        'instruction': props.get('instruction'),
        'areaDesc': props.get('areaDesc'),
        'effective': props.get('effective'),
        'onset': props.get('onset'),
        'expires': props.get('expires'),
        'status': props.get('status'),
        'category': props.get('category')
    })
    
    geom = alert.get('geometry')
    geometries.append(shape(geom) if geom else None)

gdf = gpd.GeoDataFrame(records, geometry=geometries, crs='EPSG:4326')
```

### Filter GeoDataFrame

```python
# By severity
severe_alerts = gdf[gdf['severity'] == 'Severe']

# By event type
flash_floods = gdf[gdf['event'] == 'Flash Flood Warning']
```

### Export GeoDataFrame

```python
# GeoJSON
gdf.to_file('flood_alerts.geojson', driver='GeoJSON')

# GeoPackage
gdf.to_file('flood_alerts.gpkg', driver='GPKG')

# Shapefile
gdf.to_file('flood_alerts.shp', driver='ESRI Shapefile')

# CSV (without geometry)
import pandas as pd
df = pd.DataFrame(gdf.drop(columns='geometry'))
df.to_csv('flood_alerts.csv', index=False)
```

## API Parameters

**Required Headers:**
- `User-Agent`: '(AppName, contact@email.com)'
- `Accept`: 'application/geo+json'

**Query Parameters:**
- `event`: Comma-separated list of event types
- `area`: 2-letter state code (e.g., 'CA', 'TX')
- `point`: "latitude,longitude" format

**Event Types:**
- Flood Warning
- Flash Flood Warning
- Flood Watch
- Flash Flood Watch
- Flood Advisory
- Coastal Flood Warning
- Coastal Flood Advisory

**Severity Levels:**
- Extreme
- Severe
- Moderate
- Minor

## Response Structure

```json
{
  "features": [
    {
      "properties": {
        "id": "...",
        "event": "Flood Warning",
        "severity": "Severe",
        "certainty": "Likely",
        "urgency": "Expected",
        "headline": "...",
        "description": "...",
        "instruction": "...",
        "areaDesc": "County, State",
        "effective": "2026-01-10T13:52:00-05:00",
        "expires": "2026-01-11T01:00:00-05:00"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      }
    }
  ]
}
```

## Dependencies

```bash
pip install requests geopandas shapely pandas
```

## Notes

- No API key required
- Free with no published rate limits (use responsibly)
- Geometries use CRS EPSG:4326 (WGS84)
- Empty results return empty list in `features` array
- User-Agent header is required by NOAA policy
- Flood alert descriptions are often very long (sometimes hundreds of lines). When reviewing multiple alerts, use pagination or similar methods.
- **Critical**: To generate a report for a specific flood alert, use the flood-alert-report skill.
