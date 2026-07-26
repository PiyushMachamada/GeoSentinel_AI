from pyproj import Transformer

# UTM Zone 18N -> WGS84
transformer = Transformer.from_crs(
    "EPSG:32618",
    "EPSG:4326",
    always_xy=True
)

left = 221700.13274336283
bottom = 2706898.286908078

right = 339315.0
top = 2826915.0

min_lon, min_lat = transformer.transform(left, bottom)
max_lon, max_lat = transformer.transform(right, top)

print("\nLatitude / Longitude Bounds\n")

print("Min Longitude:", min_lon)
print("Min Latitude :", min_lat)

print("Max Longitude:", max_lon)
print("Max Latitude :", max_lat)