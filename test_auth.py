import requests
import json

BASE_URL = 'http://localhost:5001'  # Adjust if your server runs on a different port

def test_register():
    print("\nTesting Registration...")
    
    # Test data for registration
    register_data = {
        "Data": {
            "citizen_id": "1",  # Make sure this ID exists in your citizens table
            "username": "testuser",
            "password": "testpass123"
        }
    }
    
    response = requests.post(f'{BASE_URL}/register', json=register_data)
    print(f"Registration Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_login():
    print("\nTesting Login...")
    
    # Test data for login
    login_data = {
        "Data": {
            "username": "john_doe",
            "password": "hashedpassword1"
        }
    }
    
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f"Login Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_logout(access_token):
    print("\nTesting Logout...")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(f'{BASE_URL}/logout', headers=headers)
    print(f"Logout Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_protected_route(access_token):
    print("\nTesting Protected Route (Profile)...")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(f'{BASE_URL}/profile', headers=headers)
    print(f"Profile Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def run_auth_flow_test():
    print("Starting Authentication Flow Test")
    print("================================")
    
    # Step 1: Register a new user
    # register_result = test_register()
    
    # Step 2: Login with the registered user
    login_result = test_login()
    
    if 'access_token' in login_result:
        access_token = login_result['access_token']
        
        # Step 3: Test accessing a protected route
        test_protected_route(access_token)
    
    else:
        print("Login failed - could not get access token")

if __name__ == "__main__":
    run_auth_flow_test() 