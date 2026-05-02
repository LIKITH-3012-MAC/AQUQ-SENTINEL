import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5MjhkZmYxNC05ZTQ4LTRlM2YtYjY0Mi1hYzA0MWYxODAyMWIiLCJlbWFpbCI6InRlc3RfYzFiNmU2YzJAZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlciIsImV4cCI6MTc3ODMxMzU3N30.VTsquMYfRDEHLB3vDFVR64k3eOdsnxhUnlUmvyPCLKQ"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_profile():
    print("\n1. Testing Profile Retrieval...")
    r = requests.get(f"{BASE_URL}/profile/me", headers=HEADERS)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")

def test_profile_update():
    print("\n2. Testing Profile Update...")
    data = {
        "full_name": "Likith Naidu",
        "state": "Andhra Pradesh",
        "city": "Kavali",
        "bio": "Marine monitoring enthusiast and protector of the oceans.",
        "phone": "+91 9876543210"
    }
    r = requests.patch(f"{BASE_URL}/profile/me", headers=HEADERS, json=data)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")

if __name__ == "__main__":
    test_profile()
    test_profile_update()
