import os
import json
import math
import numpy as np
import cv2

# --- CONFIGURATION ---
DATASET_DIR = "/Users/likithnaidu/Desktop/AQUQ-SENTINEL/DATASET"
OUTPUT_DIR = "/Users/likithnaidu/Desktop/AQUQ-SENTINEL/DATASET/yolo_ready"
IMAGE_SIZE = 256  # Standard for the provided tiles

# Class mapping
CLASSES = {
    "marine_debris": 0
}

def lonlat_to_pixel(lon, lat, zoom, tile_x, tile_y, size=256):
    """
    Converts lon/lat to pixel coordinates within a specific XYZ tile.
    """
    n = 2.0 ** zoom
    x_total = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y_total = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    
    pixel_x = (x_total - tile_x) * size
    pixel_y = (y_total - tile_y) * size
    
    return pixel_x, pixel_y

def parse_tile_filename(filename):
    """
    Extracts x, y, z from filenames like '..._16816-29821-16.jpg'
    Returns (x, y, z) or None
    """
    try:
        # Strip extension and split by '-' or '_'
        base = os.path.splitext(filename)[0]
        parts = base.replace('_', '-').split('-')
        if len(parts) >= 3:
            # Assumes format matches tile-x-tile-y-zoom
            # For 20160928_153233_0e16_16816-29821-16.jpg
            # parts[-3]=16816, parts[-2]=29821, parts[-1]=16
            return int(parts[-3]), int(parts[-2]), int(parts[-1])
    except Exception as e:
        print(f"Error parsing filename {filename}: {e}")
    return None

def convert_dataset():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Identify images
    image_files = [f for f in os.listdir(DATASET_DIR) if f.endswith(('.jpg', '.jpeg', '.tif'))]
    # Identify GeoJSONs
    geojson_files = [f for f in os.listdir(DATASET_DIR) if f.endswith('.geojson')]
    
    print(f"Found {len(image_files)} images and {len(geojson_files)} GeoJSONs.")
    
    # Map GeoJSONs by their ID prefix for faster matching
    # Example: 20170326_153234_0e26_17058-29747-16.geojson
    # We want to match by the XYZ part
    
    stats = {"converted": 0, "errors": 0, "empty": 0}
    
    for img_name in image_files:
        tile_info = parse_tile_filename(img_name)
        if not tile_info:
            continue
            
        tx, ty, tz = tile_info
        labels = []
        
        # Find matching GeoJSON
        # In this dataset, names might not match exactly, so we check coords
        # For this implementation, we assume we iterate through all geojsons for each tile
        # (Optimizable if needed)
        
        for gj_name in geojson_files:
            with open(os.path.join(DATASET_DIR, gj_name), 'r') as f:
                data = json.load(f)
            
            for feature in data.get("features", []):
                geom = feature.get("geometry", {})
                props = feature.get("properties", {})
                class_name = props.get("name", "marine_debris")
                class_id = CLASSES.get(class_name, 0)
                
                if geom.get("type") == "Polygon":
                    coords = geom["coordinates"][0] # Exterior ring
                    
                    # Convert coords to pixel and get bounds
                    px_coords = []
                    for lon, lat in coords:
                        px, py = lonlat_to_pixel(lon, lat, tz, tx, ty, IMAGE_SIZE)
                        px_coords.append((px, py))
                    
                    # Check if any point is in bounds (or partially)
                    # For YOLO we need bbox
                    xs = [p[0] for p in px_coords]
                    ys = [p[1] for p in px_coords]
                    
                    xmin, xmax = min(xs), max(xs)
                    ymin, ymax = min(ys), max(ys)
                    
                    # Clip to tile bounds
                    xmin = max(0, min(IMAGE_SIZE, xmin))
                    xmax = max(0, min(IMAGE_SIZE, xmax))
                    ymin = max(0, min(IMAGE_SIZE, ymin))
                    ymax = max(0, min(IMAGE_SIZE, ymax))
                    
                    # If valid box
                    if xmax > xmin and ymax > ymin:
                        # Convert to YOLO format (norm_center_x, norm_center_y, norm_w, norm_h)
                        w = (xmax - xmin) / IMAGE_SIZE
                        h = (ymax - ymin) / IMAGE_SIZE
                        cx = ((xmin + xmax) / 2.0) / IMAGE_SIZE
                        cy = ((ymin + ymax) / 2.0) / IMAGE_SIZE
                        
                        labels.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
        
        if labels:
            # Save YOLO label file
            label_name = os.path.splitext(img_name)[0] + ".txt"
            with open(os.path.join(OUTPUT_DIR, label_name), 'w') as f:
                f.write("\n".join(labels))
            
            # Copy image to output dir (optional, but good for YOLO organization)
            img_src = os.path.join(DATASET_DIR, img_name)
            img_dst = os.path.join(OUTPUT_DIR, img_name)
            # Use cv2 to ensure it's saved correctly if it was tif
            img_data = cv2.imread(img_src)
            cv2.imwrite(img_dst, img_data)
            
            stats["converted"] += 1
        else:
            stats["empty"] += 1
            
    print(f"Conversion complete: {stats}")

if __name__ == "__main__":
    convert_dataset()
