import os
from ultralytics import YOLO

# --- CONFIGURATION ---
DATASET_PATH = "/Users/likithnaidu/Desktop/AQUQ-SENTINEL/DATASET/yolo_ready"
MODEL_TYPE = "yolov8n.pt"  # Nano for speed and CPU feasibility
PROJECT_NAME = "AquaSentinel_Debris"

def create_yolo_yaml():
    yaml_content = f"""
path: {DATASET_PATH}
train: .
val: .
test: .

names:
  0: marine_debris
"""
    yaml_path = os.path.join(DATASET_PATH, "data.yaml")
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    return yaml_path

def train_model():
    # 1. Prepare data config
    yaml_path = create_yolo_yaml()
    
    # 2. Check if data exists
    image_count = len([f for f in os.listdir(DATASET_PATH) if f.endswith(('.jpg', '.jpeg', '.tif'))])
    if image_count == 0:
        print(f"BLOCKER: No images found in {DATASET_PATH}. Please provide matched imagery to start training.")
        return None
    
    # 3. Load model
    print(f"Loading {MODEL_TYPE}...")
    model = YOLO(MODEL_TYPE)
    
    # 4. Train
    print(f"Starting training baseline on {image_count} images...")
    results = model.train(
        data=yaml_path,
        epochs=10,  # Baseline
        imgsz=256,
        project=PROJECT_NAME,
        name="real_debris_detection",
        device="cpu"  # Force CPU for local stability
    )
    
    print(f"Training complete. Results saved to {results.save_dir}")
    return results

if __name__ == "__main__":
    train_model()
