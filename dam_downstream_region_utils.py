
from pynhd import NLDI, WaterData
import geopandas as gpd
from shapely.geometry import Point, box
import numpy as np

def find_nearest_comid(lon, lat, search_radius_km=5):
    """Find nearest COMID using WaterData class."""
    try:
        buffer_deg = search_radius_km / 111.0
        bbox = box(
            lon - buffer_deg,
            lat - buffer_deg,
            lon + buffer_deg,
            lat + buffer_deg
        )
        
        print(f"  Searching for flowlines in {search_radius_km}km radius...")
        
        wd = WaterData("nhdflowline_network")
        flowlines = wd.bygeom(bbox, geo_crs="EPSG:4326")
        
        if len(flowlines) == 0:
            if search_radius_km < 20:
                return find_nearest_comid(lon, lat, search_radius_km * 2)
            return None, None
        
        dam_point = Point(lon, lat)
        flowlines_proj = flowlines.to_crs(epsg=3857)
        dam_point_gdf = gpd.GeoDataFrame(
            geometry=[dam_point], 
            crs="EPSG:4326"
        ).to_crs(epsg=3857)
        
        dam_point_proj = dam_point_gdf.geometry.iloc[0]
        flowlines_proj['distance'] = flowlines_proj.geometry.distance(dam_point_proj)
        nearest_idx = flowlines_proj['distance'].idxmin()
        nearest = flowlines_proj.loc[nearest_idx]
        
        for field in ['comid', 'nhdplusid', 'nhdplus_comid', 'COMID', 'permanent_identifier']:
            if field in nearest.index:
                comid = nearest[field]
                distance_m = nearest['distance']
                print(f"  ✓ Found COMID {comid} at {distance_m:.1f}m from dam")
                return int(comid), distance_m
        
        return None, None
        
    except Exception as e:
        print(f"  ⚠ Error: {e}")
        return None, None


def get_downstream_area(lon, lat, buffer_km=5, distance_km=300):
    """
    Get downstream area - IMPROVED automatic detection.
    
    Key insight: For tributaries options, TRUE downstream will have:
    - FEWER total segments (tributaries converge upstream, diverge downstream)
    - Main channel options should go away from upstream sources
    
    Parameters:
    -----------
    lon, lat : float
        Dam coordinates (WGS84)
    buffer_km : int
        Buffer width around rivers in km (default: 10)
    distance_km : int
        Maximum downstream trace distance in km (default: 300)
    
    Returns:
    --------
    downstream_area : GeoDataFrame
        Buffered downstream area polygon
    comid : int
        NHD COMID of the dam location
    navigation_used : str
        Which navigation option was selected
    """
    
    comid, distance = find_nearest_comid(lon, lat)
    
    if comid is None:
        print("  ⚠ Using buffer fallback")
        dam_gdf = gpd.GeoDataFrame(
            geometry=[Point(lon, lat)],
            crs="EPSG:4326"
        )
        dam_proj = dam_gdf.to_crs(epsg=3857)
        dam_proj['geometry'] = dam_proj.buffer(buffer_km * 1000)
        return dam_proj.to_crs(epsg=4326), None, 'buffer'
    
    nldi = NLDI()
    
    # Test all navigation options
    print(f"\n  Testing all navigation options...")
    
    # CHANGED: Only test "Main" options first
    main_nav_options = [
        ('upstreamMain', 'Upstream Main Channel'),
        ('downstreamMain', 'Downstream Main Channel')
    ]
    
    main_results = {}
    
    for nav_type, description in main_nav_options:
        try:
            print(f"  → Testing '{nav_type}'...")
            flowlines = nldi.navigate_byid(
                fsource="comid",
                fid=str(comid),
                navigation=nav_type,
                source="flowlines",
                distance=distance_km
            )
            
            bounds = flowlines.total_bounds
            center_lat = (bounds[1] + bounds[3]) / 2
            center_lon = (bounds[0] + bounds[2]) / 2
            
            # Calculate distance from dam
            distance_from_dam = np.sqrt((center_lat - lat)**2 + (center_lon - lon)**2)
            
            print(f"     Segments: {len(flowlines)}, "
                  f"Center: ({center_lat:.4f}°, {center_lon:.4f}°), "
                  f"Distance: {distance_from_dam:.4f}°")
            
            main_results[nav_type] = {
                'flowlines': flowlines,
                'center_lat': center_lat,
                'center_lon': center_lon,
                'distance': distance_from_dam,
                'count': len(flowlines)
            }
            
        except Exception as e:
            print(f"     Failed: {e}")
    
    # Determine which "Main" direction goes further from dam
    if len(main_results) == 2:
        upstream_dist = main_results['upstreamMain']['distance']
        downstream_dist = main_results['downstreamMain']['distance']
        
        print(f"\n  Comparing main channel directions:")
        print(f"    upstreamMain distance from dam: {upstream_dist:.4f}°")
        print(f"    downstreamMain distance from dam: {downstream_dist:.4f}°")
        
        # The one that goes FURTHER is likely the true downstream
        if upstream_dist > downstream_dist:
            true_downstream_base = 'upstream'
            print(f"    → 'upstream' goes further, so TRUE downstream is 'upstreamTributaries'")
        else:
            true_downstream_base = 'downstream'
            print(f"    → 'downstream' goes further, so TRUE downstream is 'downstreamTributaries'")
    
    elif 'downstreamMain' in main_results:
        true_downstream_base = 'downstream'
        print(f"\n  Only downstreamMain available, using 'downstreamTributaries'")
    elif 'upstreamMain' in main_results:
        true_downstream_base = 'upstream'
        print(f"\n  Only upstreamMain available, using 'upstreamTributaries'")
    else:
        print("\n  ⚠ No main channels found, using buffer fallback")
        dam_gdf = gpd.GeoDataFrame(
            geometry=[Point(lon, lat)],
            crs="EPSG:4326"
        )
        dam_proj = dam_gdf.to_crs(epsg=3857)
        dam_proj['geometry'] = dam_proj.buffer(buffer_km * 1000)
        return dam_proj.to_crs(epsg=4326), comid, 'buffer'
    
    # Now get the tributaries version of the correct direction
    chosen_nav = f"{true_downstream_base}Tributaries"
    
    print(f"\n  Fetching '{chosen_nav}' (with all tributaries)...")
    
    try:
        flowlines = nldi.navigate_byid(
            fsource="comid",
            fid=str(comid),
            navigation=chosen_nav,
            source="flowlines",
            distance=distance_km
        )
        
        print(f"  ✓ Found {len(flowlines)} segments including tributaries")
        
        print(f"\n  Creating {buffer_km}km buffer around river network...")
        downstream_proj = flowlines.to_crs(epsg=3857)
        downstream_proj['geometry'] = downstream_proj.buffer(buffer_km * 1000)
        downstream_area = downstream_proj.dissolve().to_crs(epsg=4326)
        
        return downstream_area, comid, chosen_nav
        
    except Exception as e:
        print(f"  ⚠ Error with '{chosen_nav}': {e}")
        print(f"  Falling back to '{true_downstream_base}Main'")
        
        if true_downstream_base + 'Main' in main_results:
            flowlines = main_results[true_downstream_base + 'Main']['flowlines']
            
            downstream_proj = flowlines.to_crs(epsg=3857)
            downstream_proj['geometry'] = downstream_proj.buffer(buffer_km * 1000)
            downstream_area = downstream_proj.dissolve().to_crs(epsg=4326)
            
            return downstream_area, comid, true_downstream_base + 'Main'
        else:
            dam_gdf = gpd.GeoDataFrame(
                geometry=[Point(lon, lat)],
                crs="EPSG:4326"
            )
            dam_proj = dam_gdf.to_crs(epsg=3857)
            dam_proj['geometry'] = dam_proj.buffer(buffer_km * 1000)
            return dam_proj.to_crs(epsg=4326), comid, 'buffer'

if __name__ == "__main__":
    
    # Test with Julian Griggs Dam (should go SOUTH toward Ohio River)
    print("\n" + "="*70)
    print("TEST: Julian Griggs Dam (Scioto River)")
    print("Expected: Flow SOUTH toward Ohio River at Portsmouth")
    print("="*70)
    
    downstream_area, comid, navigation_used = get_downstream_area(
        lon=-83.18848,
        lat=41.73033,
        buffer_km=5,
        distance_km=300
    )
    
    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    print(f"COMID: {comid}")
    print(f"Navigation used: {navigation_used}")
    print(f"Dam location: (41.7303°N, -83.1885°W)")
    
    bounds = downstream_area.total_bounds
    print(f"Downstream bounds: [{bounds[0]:.4f}, {bounds[1]:.4f}, {bounds[2]:.4f}, {bounds[3]:.4f}]")
    
    # Check direction
    center_lat = (bounds[1] + bounds[3]) / 2
    if center_lat < 41.73033:
        print(f"✓ CORRECT: Downstream goes SOUTH (center at {center_lat:.4f}°N)")
    else:
        print(f"✗ WRONG: Downstream goes NORTH (center at {center_lat:.4f}°N)")
        print(f"  Expected: South toward Portsmouth, OH (38.7°N)")
    
    print(f"Area: {downstream_area.to_crs(epsg=3857).area.sum() / 1e6:.2f} km²")
    print(f"{'='*70}\n")
    
    downstream_area.to_file("julian_griggs_downstream_v2.geojson", driver="GeoJSON")
    print(f"✓ Saved to julian_griggs_downstream_v2.geojson\n")
