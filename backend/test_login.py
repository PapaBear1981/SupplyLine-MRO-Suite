import requests
import json

# API endpoint
url = "http://localhost:5000/api/auth/login"

# Login credentials
payload = {
    "employee_number": "ADMIN001",
    "password": "admin123"
}

# Make the request
try:
    response = requests.post(url, json=payload)
    
    # Print response status and content
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Content: {response.text}")
    
    # If successful, parse the JSON response
    if response.status_code == 200:
        data = response.json()
        print("\nParsed Response:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
