import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def get_token():
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@aquasentinel.ai",
        "password": "Admin@123"
    })
    print(f"Login Response: {r.status_code}")
    print(r.text)
    return r.json().get("access_token")

if __name__ == "__main__":
    get_token()
