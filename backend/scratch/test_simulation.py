import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def get_token():
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@aquasentinel.ai",
        "password": "Admin@123"
    })
    if r.status_code != 200:
        print(f"Login failed: {r.text}")
        return None
    return r.json()["access_token"]

def test_simulation():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print("\n1. Creating Simulated Debris Event...")
    data = {
        "scenario_title": "Judge Evaluation: Plastic Patch Near Kavali",
        "debris_type": "plastic_waste",
        "latitude": 14.91,
        "longitude": 80.02,
        "severity": "High",
        "density_score": 92.5,
        "affected_radius": 12.0,
        "health_impact_enabled": True,
        "alert_broadcast_enabled": True,
        "mission_flow_enabled": True,
        "judge_note": "Demonstrating high-density plastic accumulation near coastal zones.",
        "duration_minutes": 30
    }
    r = requests.post(f"{BASE_URL}/admin/simulations/", headers=headers, json=data)
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))

    print("\n2. Checking Side Effects (Alerts)...")
    r = requests.get(f"{BASE_URL}/alerts/user", headers=headers)
    print(f"Status: {r.status_code}")
    try:
        alerts = r.json()
        print(f"Alerts Found: {len(alerts)}")
        for a in alerts:
            print(f"- {a.get('title', 'No Title')}: {a.get('message', 'No Message')}")
    except Exception as e:
        print(f"Error parsing alerts: {e}")
        print(f"Raw Response: {r.text}")

if __name__ == "__main__":
    test_simulation()
