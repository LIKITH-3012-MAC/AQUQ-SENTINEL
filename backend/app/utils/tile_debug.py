import math

def tile_to_lonlat(x, y, z):
    n = 2.0 ** z
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lon_deg, lat_deg

# Tile 16816-29821-16
# Top-left
tl_lon, tl_lat = tile_to_lonlat(16816, 29821, 16)
# Bottom-right
br_lon, br_lat = tile_to_lonlat(16817, 29822, 16)

print(f"Tile Bounds: Lon [{tl_lon}, {br_lon}], Lat [{br_lat}, {tl_lat}]")
