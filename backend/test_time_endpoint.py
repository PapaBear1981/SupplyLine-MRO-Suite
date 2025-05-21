import requests
import json

def test_time_endpoint():
    """Test the time endpoint to ensure it returns the correct data."""
    try:
        # Make a request to the time endpoint
        response = requests.get('http://localhost:5000/api/time-test')

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Check if the response contains the expected keys
            assert 'status' in data, "Response missing 'status' key"
            assert 'utc_time' in data, "Response missing 'utc_time' key"
            assert 'local_time' in data, "Response missing 'local_time' key"
            assert 'timezone' in data, "Response missing 'timezone' key"

            # Check if the status is 'ok'
            assert data['status'] == 'ok', f"Expected status 'ok', got '{data['status']}'"

            print("Time endpoint test passed!")
            print(f"UTC time: {data['utc_time']}")
            print(f"Local time: {data['local_time']}")
            print(f"Timezone: {data['timezone']}")

            return True
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing time endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    test_time_endpoint()
