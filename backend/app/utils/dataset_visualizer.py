import os
import cv2
import numpy as np

# --- CONFIGURATION ---
YOLO_DIR = "/Users/likithnaidu/Desktop/AQUQ-SENTINEL/DATASET/yolo_ready"
OUTPUT_DIR = "/Users/likithnaidu/Desktop/AQUQ-SENTINEL/DATASET/visual_checks"

def draw_yolo_labels(image_path, label_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
        
    h, w, _ = img.shape
    
    if not os.path.exists(label_path):
        return img
        
    with open(label_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue
            
        cls_id = int(parts[0])
        cx, cy, bw, bh = map(float, parts[1:])
        
        # Convert back to pixels
        x1 = int((cx - bw/2) * w)
        y1 = int((cy - bh/2) * h)
        x2 = int((cx + bw/2) * w)
        y2 = int((cy + bh/2) * h)
        
        # Draw box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"Class {cls_id}", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
    return img

def run_visual_check():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    if not os.path.exists(YOLO_DIR):
        print("YOLO directory not found. Run converter first.")
        return
        
    images = [f for f in os.listdir(YOLO_DIR) if f.endswith(('.jpg', '.jpeg', '.tif'))]
    
    print(f"Checking {len(images)} images in {YOLO_DIR}...")
    
    for img_name in images:
        img_path = os.path.join(YOLO_DIR, img_name)
        label_path = os.path.join(YOLO_DIR, os.path.splitext(img_name)[0] + ".txt")
        
        overlay = draw_yolo_labels(img_path, label_path)
        if overlay is not None:
            cv2.imwrite(os.path.join(OUTPUT_DIR, f"check_{img_name}"), overlay)
            
    print(f"Visual checks saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_visual_check()
