---
name: dam-downstream-region
description: Estimate the downstream region of a dam and return as a GeoDataFrame (278 lines).
---

# Dam Downstream Region Skill

## Description

Retrieves the downstream region of a dam as a GeoPandas GeoDataFrame.

## When to Use

- Need to get the downstream region of a dam

## Examples

## Get the downstream region of the Kentucky Dam

Cut and paste the following code and don't make any changes. Keep the code as it is. Don't make any changes.

**Complete Code:**

```python
from dam_downstream_region_utils import get_downstream_area

downstream_area, comid, navigation_used = get_downstream_area(
        lon=-88.270105,
        lat=37.012498,
        buffer_km=5,
        distance_km=300
    )
```
Note that dam_downstream_region_utils.py is already in the sys.path.
