import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api/auth"

def test_auth():
    print("--- STARTING AUTH TESTS ---")
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePassword123!"
    
    # 1. Register
    print(f"\n1. Testing Register with {test_email}...")
    reg_data = {
        "full_name": "Test User",
        "email": test_email,
        "password": test_password,
        "security_question": "What is your favorite marine species?",
        "security_answer": "Dolphin"
    }
    r = requests.post(f"{BASE_URL}/register", json=reg_data)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "Registration failed"
    
    # 1b. Duplicate Register
    print("\n1b. Testing Duplicate Register...")
    r = requests.post(f"{BASE_URL}/register", json=reg_data)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 400, "Duplicate registration should fail"
    
    # 2. Login
    print("\n2. Testing Login...")
    login_data = {"email": test_email, "password": test_password}
    r = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "Login failed"
    token = r.json().get("access_token")
    assert token, "No token returned"
    
    # 2b. Bad Login
    print("\n2b. Testing Bad Login...")
    r = requests.post(f"{BASE_URL}/login", json={"email": test_email, "password": "wrong"})
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 401, "Bad login should fail"
    
    # 3. GET /me
    print("\n3. Testing GET /me...")
    r = requests.get(f"{BASE_URL}/me", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "GET /me failed"
    
    # 4. Forgot Password Question
    print("\n4. Testing Forgot Password Question...")
    r = requests.post(f"{BASE_URL}/forgot-password/question", json={"email": test_email})
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "Forgot password question failed"
    
    # 5. Forgot Password Verify
    print("\n5. Testing Forgot Password Verify...")
    r = requests.post(f"{BASE_URL}/forgot-password/verify", json={"email": test_email, "security_answer": "Dolphin"})
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "Forgot password verify failed"
    reset_token = r.json().get("reset_token")
    assert reset_token, "No reset token returned"
    
    # 6. Forgot Password Reset
    print("\n6. Testing Forgot Password Reset...")
    r = requests.post(f"{BASE_URL}/forgot-password/reset", json={
        "email": test_email, 
        "reset_token": reset_token, 
        "new_password": "NewSecurePassword123!"
    })
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "Forgot password reset failed"
    
    # 7. Login with new password
    print("\n7. Testing Login with new password...")
    r = requests.post(f"{BASE_URL}/login", json={"email": test_email, "password": "NewSecurePassword123!"})
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "Login with new password failed"
    new_token = r.json().get("access_token")
    
    # 8. Logout
    print("\n8. Testing Logout...")
    r = requests.post(f"{BASE_URL}/logout", headers={"Authorization": f"Bearer {new_token}"})
    print(f"Status: {r.status_code}, Response: {r.text}")
    assert r.status_code == 200, "Logout failed"
    
    print("\n--- ALL BACKEND TESTS PASSED ---")

if __name__ == "__main__":
    test_auth()
