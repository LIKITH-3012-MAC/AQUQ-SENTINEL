import random
from sqlalchemy.orm import Session
from .. import models
import os

def process_debris_detection(db: Session, report_id: int, image_path: str):
    """
    Simulated AI Debris Detection Service.
    Ready for YOLOv8/OpenCV integration.
    """
    # In a real scenario, we would run:
    # model = YOLO('yolov8n-marine.pt')
    # results = model(image_path)
    
    mock_classes = [
        {"type": "Plastic Bottle", "equipment": "Surface Skimmer"},
        {"type": "Ghost Net", "equipment": "Mechanical Claw"},
        {"type": "Oil Slick", "equipment": "Containment Boom"},
        {"type": "Floating Waste", "equipment": "Manual Collection"}
    ]
    
    # Simulate 1-3 detections
    num_detections = random.randint(1, 3)
    results = []
    
    total_density = 0.0
    
    for _ in range(num_detections):
        selected = random.choice(mock_classes)
        confidence = round(random.uniform(0.75, 0.98), 2)
        density = round(random.uniform(20.0, 80.0), 2)
        total_density += density
        
        detection = models.DebrisDetection(
            report_id=report_id,
            filename=os.path.basename(image_path),
            object_type=selected["type"],
            confidence=confidence,
            bbox={"x": random.randint(0, 100), "y": random.randint(0, 100), "w": 50, "h": 50},
            density_score=density,
            recommended_equipment=selected["equipment"]
        )
        db.add(detection)
        results.append(detection)
        
    db.commit()
    
    avg_density = total_density / num_detections if num_detections > 0 else 0
    return results, avg_density

