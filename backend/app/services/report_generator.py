import json
import os
from datetime import datetime
from typing import Dict, Any

def generate_simple_report(data: Dict[str, Any], output_dir: str = "uploads/reports") -> str:
    """
    Generates a simple JSON report.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        
    return filepath
