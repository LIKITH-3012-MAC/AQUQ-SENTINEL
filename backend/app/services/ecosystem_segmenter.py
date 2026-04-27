import random

def segment_ecosystem(image_path: str):
    """
    Mock Ecosystem Segmentation Service.
    In a real app, this would use a U-Net or DeepLab model
    to classify pixels into water, coral, algae, debris, etc.
    """
    # Generate percentages that sum up to roughly 100
    water = random.uniform(50.0, 75.0)
    algae = random.uniform(5.0, 20.0)
    coral = random.uniform(5.0, 15.0)
    debris = random.uniform(2.0, 15.0)
    
    remaining = 100.0 - (water + algae + coral + debris)
    turbid_water = max(0.0, remaining) # ensure non-negative
    
    degradation_score = (algae * 1.5) + (debris * 2) + (turbid_water * 1.2) - (coral * 0.5)
    degradation_score = max(0.0, min(100.0, degradation_score))
    
    return {
        "water": round(water, 2),
        "algae": round(algae, 2),
        "coral": round(coral, 2),
        "debris": round(debris, 2),
        "turbid_water": round(turbid_water, 2),
        "ecosystem_degradation_score": round(degradation_score, 2)
    }
