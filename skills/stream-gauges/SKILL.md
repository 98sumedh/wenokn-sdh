---
name: stream-gauges
description: Query active USGS stream gauges using the USGS Water Services API. Returns stream gauge locations and metadata as a GeoDataFrame with current status information.
---

# USGS Stream Gauges Skill

## Description

Retrieves active USGS stream gauge data using the official USGS Water Services API. This method provides access to all ~8,500 active USGS streamgages (not just forecast locations), includes current streamflow data, and returns results as a GeoPandas GeoDataFrame.

## When to Use

- Find active stream gauges by state, county, or bounding box
- Get gauges with current streamflow measurements
- Find gauges on specific rivers or watersheds (HUC codes)
- Spatial analysis involving stream gauges with live data
- Filter for only active, operational gauges

## Important Notes

- Use `siteStatus=active` to get only operational gauges
- Use `siteType=ST` to get stream gauges only (excludes groundwater, lakes, etc.)
- Use `parameterCd=00060` to ensure gauges measure streamflow/discharge
- County codes require state FIPS + county FIPS (e.g., "39049" for Franklin County, OH)
- HUC codes identify watersheds (8-digit HUC recommended for river systems)

## Examples

### Example 1: Find All Gauges on the Scioto River

Cut and paste the following code and don't make any changes. Keep the code as it is. Don't make any changes.

```python
from gages_utils import get_gages_on_river

gauges = get_gages_on_river("Scioto River")
```

Note that gages_utils.py is already in the sys.path. Always specify the buffer size used to find gauges on the river.

---

### Example 1: Find Active Stream Gauges in a State

**User Request:** "Find active stream gauges in Ohio" or "Get all Ohio streamgages"

**Complete Code:**

```python
import requests
import geopandas as gpd
from shapely.geometry import Point

def get_usgs_gauges_by_state(state_code):
    """
    Get active USGS stream gauges in a state.
    
    Args:
        state_code: Two-letter state code (e.g., "OH", "KY", "PA")
    
    Returns:
        GeoDataFrame with active stream gauges
    """
    url = "https://waterservices.usgs.gov/nwis/iv/"
    
    params = {
        "stateCd": state_code,
        "parameterCd": "00060",  # Discharge/streamflow
        "siteType": "ST",  # Stream only
        "siteStatus": "active",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return gpd.GeoDataFrame()
    
    # Parse timeSeries data
    gauges = []
    for ts in data.get('value', {}).get('timeSeries', []):
        site = ts['sourceInfo']
        site_code = site['siteCode'][0]['value']
        
        # Get current value if available
        current_value = None
        current_time = None
        if 'values' in ts and len(ts['values']) > 0:
            values_list = ts['values'][0].get('value', [])
            if len(values_list) > 0:
                latest = values_list[-1]
                current_value = latest.get('value')
                current_time = latest.get('dateTime')
        
        gauges.append({
            'usgs_site_no': site_code,
            'site_name': site['siteName'],
            'latitude': float(site['geoLocation']['geogLocation']['latitude']),
            'longitude': float(site['geoLocation']['geogLocation']['longitude']),
            'county': site['siteProperty'][0]['value'] if 'siteProperty' in site and len(site['siteProperty']) > 0 else None,
            'current_flow_cfs': float(current_value) if current_value else None,
            'current_time': current_time,
            'geometry': Point(
                float(site['geoLocation']['geogLocation']['longitude']),
                float(site['geoLocation']['geogLocation']['latitude'])
            )
        })
    
    gdf = gpd.GeoDataFrame(gauges, crs="EPSG:4326")
    return gdf

# Usage
ohio_gauges = get_usgs_gauges_by_state("OH")
print(f"Found {len(ohio_gauges)} active stream gauges in Ohio")
print(ohio_gauges.head())
```

---

### Example 2: Find Active Stream Gauges in a County

**User Request:** "Find stream gauges in Franklin County, Ohio" or "Get gauges in Ross County"

**Complete Code:**

```python
import requests
import geopandas as gpd
from shapely.geometry import Point

def get_usgs_gauges_by_county(state_fips, county_fips):
    """
    Get active USGS stream gauges in a county.
    
    Args:
        state_fips: State FIPS code (e.g., "39" for Ohio)
        county_fips: County FIPS code (e.g., "049" for Franklin County)
    
    Returns:
        GeoDataFrame with active stream gauges
    """
    # Combine state and county FIPS
    county_code = f"{state_fips}{county_fips}"
    
    url = "https://waterservices.usgs.gov/nwis/iv/"
    
    params = {
        "countyCd": county_code,
        "parameterCd": "00060",
        "siteType": "ST",
        "siteStatus": "active",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return gpd.GeoDataFrame()
    
    gauges = []
    for ts in data.get('value', {}).get('timeSeries', []):
        site = ts['sourceInfo']
        site_code = site['siteCode'][0]['value']
        
        current_value = None
        current_time = None
        if 'values' in ts and len(ts['values']) > 0:
            values_list = ts['values'][0].get('value', [])
            if len(values_list) > 0:
                latest = values_list[-1]
                current_value = latest.get('value')
                current_time = latest.get('dateTime')
        
        gauges.append({
            'usgs_site_no': site_code,
            'site_name': site['siteName'],
            'latitude': float(site['geoLocation']['geogLocation']['latitude']),
            'longitude': float(site['geoLocation']['geogLocation']['longitude']),
            'current_flow_cfs': float(current_value) if current_value else None,
            'current_time': current_time,
            'geometry': Point(
                float(site['geoLocation']['geogLocation']['longitude']),
                float(site['geoLocation']['geogLocation']['latitude'])
            )
        })
    
    gdf = gpd.GeoDataFrame(gauges, crs="EPSG:4326")
    return gdf

# Example: Franklin County, Ohio (State FIPS: 39, County FIPS: 049)
franklin_gauges = get_usgs_gauges_by_county("39", "049")
print(f"Found {len(franklin_gauges)} active stream gauges in Franklin County, OH")

# Example: Ross County, Ohio (State FIPS: 39, County FIPS: 141)
ross_gauges = get_usgs_gauges_by_county("39", "141")
print(f"Found {len(ross_gauges)} active stream gauges in Ross County, OH")
```

**Common Ohio County FIPS Codes:**
- Franklin County: 39049
- Ross County: 39141
- Hamilton County: 39061
- Cuyahoga County: 39035

---

### Example 3: Find Active Stream Gauges in a Bounding Box

**User Request:** "Find stream gauges in this region" or "Get gauges in bounding box"

**Complete Code:**

```python
import requests
import geopandas as gpd
from shapely.geometry import Point

def get_usgs_gauges_by_bbox(west, south, east, north):
    """
    Get active USGS stream gauges in a bounding box.
    
    Args:
        west: Western longitude (negative for W)
        south: Southern latitude
        east: Eastern longitude (negative for W)
        north: Northern latitude
    
    Returns:
        GeoDataFrame with active stream gauges
    """
    url = "https://waterservices.usgs.gov/nwis/iv/"
    
    params = {
        "bBox": f"{west},{south},{east},{north}",
        "parameterCd": "00060",
        "siteType": "ST",
        "siteStatus": "active",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return gpd.GeoDataFrame()
    
    gauges = []
    for ts in data.get('value', {}).get('timeSeries', []):
        site = ts['sourceInfo']
        site_code = site['siteCode'][0]['value']
        
        current_value = None
        current_time = None
        if 'values' in ts and len(ts['values']) > 0:
            values_list = ts['values'][0].get('value', [])
            if len(values_list) > 0:
                latest = values_list[-1]
                current_value = latest.get('value')
                current_time = latest.get('dateTime')
        
        gauges.append({
            'usgs_site_no': site_code,
            'site_name': site['siteName'],
            'latitude': float(site['geoLocation']['geogLocation']['latitude']),
            'longitude': float(site['geoLocation']['geogLocation']['longitude']),
            'current_flow_cfs': float(current_value) if current_value else None,
            'current_time': current_time,
            'geometry': Point(
                float(site['geoLocation']['geogLocation']['longitude']),
                float(site['geoLocation']['geogLocation']['latitude'])
            )
        })
    
    gdf = gpd.GeoDataFrame(gauges, crs="EPSG:4326")
    return gdf

# Example: Columbus, Ohio area
bbox_gauges = get_usgs_gauges_by_bbox(-83.2, 39.8, -82.8, 40.2)
print(f"Found {len(bbox_gauges)} active stream gauges in bounding box")
```

---

### Example 4: Find Active Stream Gauges in a Watershed (HUC)

**User Request:** "Find gauges in Scioto River watershed" or "Get gauges in HUC 05060001"

**Complete Code:**

```python
import requests
import geopandas as gpd
from shapely.geometry import Point

def get_usgs_gauges_by_huc(huc_code):
    """
    Get active USGS stream gauges in a watershed (Hydrologic Unit Code).
    
    Args:
        huc_code: HUC code (2, 4, 6, or 8 digits)
                 Example: "05060001" for Upper Scioto River
    
    Returns:
        GeoDataFrame with active stream gauges
    """
    url = "https://waterservices.usgs.gov/nwis/iv/"
    
    params = {
        "huc": huc_code,
        "parameterCd": "00060",
        "siteType": "ST",
        "siteStatus": "active",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return gpd.GeoDataFrame()
    
    gauges = []
    for ts in data.get('value', {}).get('timeSeries', []):
        site = ts['sourceInfo']
        site_code = site['siteCode'][0]['value']
        
        current_value = None
        current_time = None
        if 'values' in ts and len(ts['values']) > 0:
            values_list = ts['values'][0].get('value', [])
            if len(values_list) > 0:
                latest = values_list[-1]
                current_value = latest.get('value')
                current_time = latest.get('dateTime')
        
        gauges.append({
            'usgs_site_no': site_code,
            'site_name': site['siteName'],
            'latitude': float(site['geoLocation']['geogLocation']['latitude']),
            'longitude': float(site['geoLocation']['geogLocation']['longitude']),
            'huc': huc_code,
            'current_flow_cfs': float(current_value) if current_value else None,
            'current_time': current_time,
            'geometry': Point(
                float(site['geoLocation']['geogLocation']['longitude']),
                float(site['geoLocation']['geogLocation']['latitude'])
            )
        })
    
    gdf = gpd.GeoDataFrame(gauges, crs="EPSG:4326")
    return gdf

# Example: Upper Scioto River watershed
scioto_gauges = get_usgs_gauges_by_huc("05060001")
print(f"Found {len(scioto_gauges)} active stream gauges in Upper Scioto River watershed")

# Example: Entire Ohio River basin (Region 05)
ohio_basin_gauges = get_usgs_gauges_by_huc("05")
print(f"Found {len(ohio_basin_gauges)} active stream gauges in Ohio River basin")
```

**Common Ohio HUC Codes:**
- Upper Scioto River: 05060001
- Lower Scioto River: 05060002
- Great Miami River: 05080001
- Muskingum River: 05040004
- Ohio River Basin: 05

---

### Example 5: Get Detailed Site Metadata

**User Request:** "Get detailed information for gauge 03227500"

**Complete Code:**

```python
import requests
import geopandas as gpd
from shapely.geometry import Point

def get_usgs_site_metadata(site_numbers):
    """
    Get detailed metadata for USGS sites.
    
    Args:
        site_numbers: Single site number (str) or list of site numbers
    
    Returns:
        GeoDataFrame with detailed site metadata
    """
    if isinstance(site_numbers, str):
        site_numbers = [site_numbers]
    
    url = "https://waterservices.usgs.gov/nwis/site/"
    
    params = {
        "sites": ",".join(site_numbers),
        "siteOutput": "expanded",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return gpd.GeoDataFrame()
    
    sites = []
    for site in data.get('value', {}).get('timeSeries', []):
        source = site['sourceInfo']
        
        sites.append({
            'usgs_site_no': source['siteCode'][0]['value'],
            'site_name': source['siteName'],
            'latitude': float(source['geoLocation']['geogLocation']['latitude']),
            'longitude': float(source['geoLocation']['geogLocation']['longitude']),
            'datum': source['geoLocation']['geogLocation'].get('srs', 'Unknown'),
            'agency': source['siteCode'][0].get('agencyCode', 'USGS'),
            'site_type': source.get('siteType', [{}])[0].get('name', 'Unknown'),
            'huc': source.get('siteProperty', [{}])[0].get('value') if 'siteProperty' in source else None,
            'geometry': Point(
                float(source['geoLocation']['geogLocation']['longitude']),
                float(source['geoLocation']['geogLocation']['latitude'])
            )
        })
    
    gdf = gpd.GeoDataFrame(sites, crs="EPSG:4326")
    return gdf

# Example: Get metadata for specific sites
sites_metadata = get_usgs_site_metadata(["03227500", "03221500", "03234500"])
print(sites_metadata)
```

---

## USGS Parameter Codes

Common parameter codes for water data:

- `00060` - Discharge (streamflow) in cubic feet per second (cfs)
- `00065` - Gage height (stage) in feet
- `00010` - Water temperature in degrees Celsius
- `00300` - Dissolved oxygen in mg/L
- `00400` - pH
- `63680` - Turbidity in FNU

## USGS Site Type Codes

- `ST` - Stream
- `ES` - Estuary
- `LK` - Lake, Reservoir, Impoundment
- `GW` - Well (groundwater)
- `SP` - Spring
- `OC` - Ocean

## State FIPS Codes (Common)

- Ohio: 39
- Kentucky: 21
- Pennsylvania: 42
- Indiana: 18
- West Virginia: 54
- Michigan: 26

## API Limitations

- Instantaneous values (IV) service: Returns current/recent data
- Daily values (DV) service: Use base URL `https://waterservices.usgs.gov/nwis/dv/` for historical daily data
- Rate limits: Generally no strict limits for reasonable use
- Timeout: Set reasonable timeouts (30s recommended) for large queries

## Resources

- USGS Water Services Documentation: https://waterservices.usgs.gov/rest/
- FIPS Codes: https://www.census.gov/library/reference/code-lists/ansi.html
- HUC Lookup: https://water.usgs.gov/GIS/huc.html
- USGS Parameter Codes: https://help.waterdata.usgs.gov/parameter_cd
