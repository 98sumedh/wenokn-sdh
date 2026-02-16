---
name: npdes-wastewater-discharge-facilities
description: Query EPA ECHO database for NPDES wastewater discharge facilities with coordinates as GeoDataframe
---

# NPDES Wastewater Discharge Facilities Skill

## Description

Query EPA ECHO to find NPDES permitted facilities (wastewater treatment plants, industrial dischargers, stormwater systems). **Critical limitation: JSON has latitude but NO longitude; CSV has longitude but NO latitude.** Must merge both sources.

**Default behavior: Returns only ACTIVE facilities (p_pstat='EFF') with automatic pagination for >5000 results.**

## When to Use

- User asks about wastewater facilities in specific locations
- Need facility coordinates for mapping
- Search by state, county, city, ZIP, or facility name
- Filter by permit type (POTW, industrial) or status

## How to Use

### Step 1: Create Query (Active Facilities Only)
```python
import requests
import time

response = requests.get(
    "https://echodata.epa.gov/echo/cwa_rest_services.get_facilities",
    params={
        'p_st': 'KY',           # State
        'p_pstat': 'EFF',       # ACTIVE facilities only (default)
        'output': 'JSON'
    }
)
qid = response.json()['Results']['QueryID']
```

### Step 2: Get JSON with Pagination (has latitude)
```python
# Fetch all facilities across multiple pages
all_json_facilities = []
page = 1

while True:
    response = requests.get(
        "https://echodata.epa.gov/echo/cwa_rest_services.get_qid",
        params={'qid': qid, 'pageno': page, 'rows': 10000, 'output': 'JSON'}
    )
    data = response.json()
    facilities = data['Results'].get('Facilities', [])
    
    if not facilities:
        break
    
    all_json_facilities.extend(facilities)
    total_records = data['Results'].get('TotalRecords', 0)
    
    print(f"Page {page}: Retrieved {len(facilities)} facilities (Total so far: {len(all_json_facilities)}/{total_records})")
    
    # Break if we've retrieved all records
    if len(all_json_facilities) >= total_records:
        break
    
    page += 1
    time.sleep(0.3)  # Rate limiting

print(f"Total facilities retrieved: {len(all_json_facilities)}")
```

### Step 3: Get CSV (has longitude)
```python
import csv
from io import StringIO

csv_response = requests.get(
    "https://echodata.epa.gov/echo/cwa_rest_services.get_download",
    params={'qid': qid, 'output': 'CSV'}, 
    timeout=120
)
csv_data = list(csv.DictReader(StringIO(csv_response.text)))
print(f"CSV records: {len(csv_data)}")
```

### Step 4: Merge by NPDES ID
```python
csv_lookup = {row['SourceID']: row for row in csv_data}
complete = []

for fac in all_json_facilities:
    csv_fac = csv_lookup.get(fac['SourceID'], {})
    
    # Only include if we have both coordinates
    lat = fac.get('FacLat')
    lon = csv_fac.get('FacLong')
    
    if lat and lon:
        complete.append({
            'name': fac.get('CWPName'),
            'npdes_id': fac['SourceID'],
            'latitude': float(lat),
            'longitude': float(lon),
            'city': fac.get('CWPCity'),
            'state': fac.get('CWPState'),
            'county': csv_fac.get('FacStdCountyName'),
            'permit_status': fac.get('CWPPermitStatusDesc'),
            'facility_type': fac.get('FacilityTypeIndicator'),
            'design_flow': csv_fac.get('CWPTotalDesignFlowNmbr')
        })

print(f"Facilities with complete coordinates: {len(complete)}")
```

### Step 5: Convert to GeoDataFrame (Optional)
```python
import geopandas as gpd
from shapely.geometry import Point

gdf = gpd.GeoDataFrame(
    complete,
    geometry=[Point(xy) for xy in zip([f['longitude'] for f in complete], 
                                       [f['latitude'] for f in complete])],
    crs='EPSG:4326'
)
```

## Key Parameters

| Param | Description | Example | Default |
|-------|-------------|---------|---------|
| `p_st` | State (required) | 'CA', 'TX', 'KY' | - |
| `p_pstat` | Permit Status | 'EFF'=Active, 'TRM'=Terminated, 'EXP'=Expired | **'EFF'** |
| `p_co` | County | 'San Diego', 'Jefferson' | - |
| `p_ct` | City | 'Los Angeles' | - |
| `p_zip` | ZIP code | '92101' | - |
| `p_fn` | Facility name (partial) | 'Water' | - |
| `p_pid` | NPDES ID | 'CA0001309' | - |
| `p_ptype` | Type | 'POT'=POTW, 'NPD'=NPDES, 'IND'=Industrial, 'MUN'=Municipal | - |
| `p_maj` | Major facilities only | 'Y' | - |

## Key Fields

**JSON:** `CWPName`, `SourceID`, `FacLat` (lat only), `CWPCity`, `CWPState`, `CWPPermitStatusDesc`, `FacilityTypeIndicator`

**CSV:** `FacLong` (lon only), `FacStdCountyName`, `CWPTotalDesignFlowNmbr`, `PercentPeopleOfColor`

## Examples

### Find all active facilities in Kentucky
```python
params = {
    'p_st': 'KY',
    'p_pstat': 'EFF',  # Active only
    'output': 'JSON'
}
```

### Find active facilities in county
```python
params = {
    'p_st': 'CA',
    'p_co': 'San Diego',
    'p_pstat': 'EFF',
    'output': 'JSON'
}
```

### Find active major POTWs
```python
params = {
    'p_st': 'TX',
    'p_ptype': 'POT',
    'p_maj': 'Y',
    'p_pstat': 'EFF',
    'output': 'JSON'
}
```

### Search by name (active only)
```python
params = {
    'p_st': 'CA',
    'p_fn': 'Water Reclamation',
    'p_pstat': 'EFF',
    'output': 'JSON'
}
```

### Include terminated facilities (if needed)
```python
# Option 1: All statuses (active, terminated, expired)
params = {'p_st': 'KY', 'output': 'JSON'}  # Omit p_pstat

# Option 2: Only terminated
params = {'p_st': 'KY', 'p_pstat': 'TRM', 'output': 'JSON'}
```

## Complete Example Script

```python
import requests
import csv
from io import StringIO
import time
import geopandas as gpd
from shapely.geometry import Point

def fetch_npdes_facilities(state, county=None, active_only=True):
    """
    Fetch NPDES facilities with complete coordinates.
    
    Args:
        state: Two-letter state code (e.g., 'KY')
        county: County name (optional)
        active_only: If True, only fetch active facilities (default)
    
    Returns:
        GeoDataFrame with facility data and coordinates
    """
    # Step 1: Create query
    params = {
        'p_st': state,
        'output': 'JSON'
    }
    
    if active_only:
        params['p_pstat'] = 'EFF'
    
    if county:
        params['p_co'] = county
    
    response = requests.get(
        "https://echodata.epa.gov/echo/cwa_rest_services.get_facilities",
        params=params
    )
    qid = response.json()['Results']['QueryID']
    
    # Step 2: Get JSON with pagination
    all_json_facilities = []
    page = 1
    
    while True:
        response = requests.get(
            "https://echodata.epa.gov/echo/cwa_rest_services.get_qid",
            params={'qid': qid, 'pageno': page, 'rows': 10000, 'output': 'JSON'}
        )
        data = response.json()
        facilities = data['Results'].get('Facilities', [])
        
        if not facilities:
            break
        
        all_json_facilities.extend(facilities)
        total_records = data['Results'].get('TotalRecords', 0)
        
        if len(all_json_facilities) >= total_records:
            break
        
        page += 1
        time.sleep(0.3)
    
    # Step 3: Get CSV
    csv_response = requests.get(
        "https://echodata.epa.gov/echo/cwa_rest_services.get_download",
        params={'qid': qid, 'output': 'CSV'},
        timeout=120
    )
    csv_data = list(csv.DictReader(StringIO(csv_response.text)))
    
    # Step 4: Merge
    csv_lookup = {row['SourceID']: row for row in csv_data}
    complete = []
    
    for fac in all_json_facilities:
        csv_fac = csv_lookup.get(fac['SourceID'], {})
        lat = fac.get('FacLat')
        lon = csv_fac.get('FacLong')
        
        if lat and lon:
            complete.append({
                'name': fac.get('CWPName'),
                'npdes_id': fac['SourceID'],
                'latitude': float(lat),
                'longitude': float(lon),
                'city': fac.get('CWPCity'),
                'state': fac.get('CWPState'),
                'county': csv_fac.get('FacStdCountyName'),
                'permit_status': fac.get('CWPPermitStatusDesc'),
                'facility_type': fac.get('FacilityTypeIndicator')
            })
    
    # Step 5: Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        complete,
        geometry=[Point(xy) for xy in zip([f['longitude'] for f in complete],
                                          [f['latitude'] for f in complete])],
        crs='EPSG:4326'
    )
    
    return gdf

# Usage
gdf = fetch_npdes_facilities('KY', active_only=True)
print(f"Retrieved {len(gdf)} active facilities with coordinates")
```

## Notes

- **Default: Active facilities only** (`p_pstat='EFF'`) - omit this parameter to get all statuses
- **Automatic pagination** handles >5000 records from JSON API
- **Must merge JSON + CSV** to get both lat/lon
- JSON results paginated at 10,000 records per page
- CSV download takes 30-120s for large queries
- Add `time.sleep(0.3)` between paginated requests for rate limiting
- Facilities without complete coordinates are excluded from final dataset
- To get terminated facilities, use `p_pstat='TRM'` or omit `p_pstat` entirely

## Troubleshooting

**Issue: Missing coordinates**
- JSON API may have 5000+ facilities but some lack latitude
- CSV may have all facilities but some lack longitude
- Merged dataset only includes facilities with BOTH coordinates

**Issue: Slow CSV download**
- Normal for large queries (30-120 seconds)
- Increase timeout parameter if needed

**Issue: Different counts between JSON and CSV**
- This is expected - merge by SourceID to align them
- Final count will be ≤ minimum of both sources
