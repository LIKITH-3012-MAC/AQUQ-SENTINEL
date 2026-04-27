import random

def detect_debris(image_path: str):
    """
    Mock Debris Detection Service.
    In a real app, this would use OpenCV and YOLOv8 or similar models
    to detect debris in the image.
    """
    # Mock some detections
    mock_classes = ["plastic_bottle", "fishing_net", "floating_waste", "oil_like_patch"]
    detections = []
    
    num_detections = random.randint(1, 4)
    for _ in range(num_detections):
        detections.append({
            "class": random.choice(mock_classes),
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "bbox": [
                random.randint(10, 100),
                random.randint(10, 100),
                random.randint(150, 300),
                random.randint(150, 300)
            ]
        })
    
    density_score = random.randint(30, 95)
    
    summary = "High floating debris concentration detected." if density_score > 70 else "Low to moderate debris concentration."
    
    return {
        "detections": detections,
        "debris_density_score": density_score,
        "summary": summary
    }
