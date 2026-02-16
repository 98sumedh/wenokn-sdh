"""
Diagnostic script to check actual NHD waterbody_hr column names
"""

from pynhd import NHD
from shapely.geometry import Point

# Boulder, Colorado coordinates
boulder_coords = (-105.2705, 40.0150)
point = Point(boulder_coords[0], boulder_coords[1])

# Small buffer for quick test
radius_degrees = 5 / 69.0  # 5 miles
buffer_geom = point.buffer(radius_degrees)

print("Querying NHD waterbody_hr layer...")
nhd = NHD("waterbody_hr")
lakes = nhd.bygeom(buffer_geom)

print(f"\nFound {len(lakes)} water bodies")

if len(lakes) > 0:
    print("\n" + "="*80)
    print("ACTUAL COLUMN NAMES:")
    print("="*80)
    for col in lakes.columns:
        print(f"  - {col}")
    
    print("\n" + "="*80)
    print("FIRST FEATURE (sample data):")
    print("="*80)
    first = lakes.iloc[0]
    for col in lakes.columns:
        if col != 'geometry':
            print(f"  {col}: {first[col]}")
    
    print("\n" + "="*80)
    print("DATA TYPES:")
    print("="*80)
    print(lakes.dtypes)
    
else:
    print("No water bodies found in test area")
