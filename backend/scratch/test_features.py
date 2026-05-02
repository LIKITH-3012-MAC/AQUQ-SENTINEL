import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0YzAyZThiNS1kZTExLTQ1ZjQtYjRlZS0wNTAwYzAwNmI2MzgiLCJlbWFpbCI6InRlc3RfNzk1NTkzMGJAZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlciIsImV4cCI6MTc3ODMxMzI2N30.0T_aPD1cLqiVL87xV27FW51pBdSbYlXppkrFkNYc1ZQ"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_health_score():
    print("\n1. Testing Ocean Health Score...")
    r = requests.get(f"{BASE_URL}/health/score?lat=12.97&lon=80.24", headers=HEADERS)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

def test_hyperlocal():
    print("\n2. Testing Hyperlocal Intelligence...")
    r = requests.get(f"{BASE_URL}/hyperlocal/intelligence?lat=12.97&lon=80.24", headers=HEADERS)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

def test_predictions():
    print("\n3. Testing Debris Hotspot Prediction...")
    r = requests.get(f"{BASE_URL}/predictions/hotspots?lat=12.97&lon=80.24", headers=HEADERS)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

def test_ai_analyze():
    print("\n4. Testing AI Report Analysis Preview...")
    data = {
        "title": "Test Debris",
        "description": "Large cluster of plastic bottles near the shore.",
        "latitude": 12.97,
        "longitude": 80.24,
        "report_type": "plastic_waste",
        "severity": "High"
    }
    r = requests.post(f"{BASE_URL}/reports/analyze", headers=HEADERS, json=data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

def test_weather():
    print("\n5. Testing Marine Weather...")
    r = requests.get(f"{BASE_URL}/weather/marine?lat=12.97&lon=80.24", headers=HEADERS)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    test_health_score()
    test_hyperlocal()
    test_predictions()
    test_ai_analyze()
    test_weather()
