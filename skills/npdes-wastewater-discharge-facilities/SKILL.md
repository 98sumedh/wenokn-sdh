name:npdes-wastewater-discharge-facilities
description: Query EPA ECHO database for NPDES wastewater discharge facilities with coordinates as GeoDataframe
---

# NPDES Waterwater Discharge Facilities Skill

## Description

Query EPA ECHO to find NPDES permitted facilities (wastewater treatment plants, industrial dischargers, stormwater systems). **Critical limitation: JSON has latitude but NO longitude; CSV has longitude but NO latitude.** Must merge both sources.

## When to Use

- User asks about wastewater facilities in specific locations
- Need facility coordinates for mapping
- Search by state, county, city, ZIP, or facility name
- Filter by permit type (POTW, industrial) or status

## How to Use

### Step 1: Create Query
```python
response = requests.get(
    "https://echodata.epa.gov/echo/cwa_rest_services.get_facilities",
    params={'p_st': 'CA', 'p_co': 'San Diego', 'output': 'JSON'}
)
qid = response.json()['Results']['QueryID']
```

### Step 2: Get JSON (has latitude)
```python
response = requests.get(
    "https://echodata.epa.gov/echo/cwa_rest_services.get_qid",
    params={'qid': qid, 'pageno': 1, 'rows': 10000, 'output': 'JSON'}
)
json_facilities = response.json()['Results']['Facilities']
```

### Step 3: Get CSV (has longitude)
```python
import csv
from io import StringIO

csv_response = requests.get(
    "https://echodata.epa.gov/echo/cwa_rest_services.get_download",
    params={'qid': qid, 'output': 'CSV'}, timeout=120
)
csv_data = list(csv.DictReader(StringIO(csv_response.text)))
```

### Step 4: Merge by NPDES ID
```python
csv_lookup = {row['SourceID']: row for row in csv_data}
complete = []
for fac in json_facilities:
    csv_fac = csv_lookup.get(fac['SourceID'], {})
    complete.append({
        'name': fac.get('CWPName'),
        'npdes_id': fac['SourceID'],
        'latitude': fac.get('FacLat'),        # From JSON
        'longitude': csv_fac.get('FacLong'),  # From CSV
        'city': fac.get('CWPCity'),
        'state': fac.get('CWPState')
    })
```

## Key Parameters

| Param | Description | Example |
|-------|-------------|---------|
| `p_st` | State | 'CA', 'TX' |
| `p_co` | County | 'San Diego' |
| `p_ct` | City | 'Los Angeles' |
| `p_zip` | ZIP code | '92101' |
| `p_fn` | Facility name (partial) | 'Water' |
| `p_pid` | NPDES ID | 'CA0001309' |
| `p_ptype` | Type: POT/NPD/IND/MUN | 'POT' |
| `p_pstat` | Status: EFF/TRM/EXP | 'EFF' |
| `p_maj` | Major only | 'Y' |

## Key Fields

**JSON:** `CWPName`, `SourceID`, `FacLat` (lat only), `CWPCity`, `CWPState`, `CWPPermitStatusDesc`
**CSV:** `FacLong` (lon only), `FacStdCountyName`, `CWPTotalDesignFlowNmbr`, `PercentPeopleOfColor`

## Examples

**Find facilities in county:**
```python
params = {'p_st': 'CA', 'p_co': 'San Diego', 'output': 'JSON'}
```

**Find major POTWs:**
```python
params = {'p_st': 'TX', 'p_ptype': 'POT', 'p_maj': 'Y', 'output': 'JSON'}
```

**Search by name:**
```python
params = {'p_st': 'CA', 'p_fn': 'Water Reclamation', 'output': 'JSON'}
```

## Notes

- **Must merge JSON + CSV** to get both lat/lon
- JSON results paginated (10000/page) - loop through pages
- CSV download takes 30-120s for large queries
- Add `time.sleep(0.3)`
