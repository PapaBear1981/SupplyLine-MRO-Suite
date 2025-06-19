#!/usr/bin/env python3
"""
Manually inject authentication token into browser to bypass login form
"""

import requests
import json

def get_auth_token():
    """Get authentication token from backend"""
    
    backend_url = "https://supplylinemrosuite-454313121816.us-west1.run.app"
    
    print("🔑 Getting Authentication Token")
    print("=" * 40)
    
    login_data = {
        "employee_number": "ADMIN001",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{backend_url}/api/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            user_info = {
                'name': result.get('name'),
                'employee_number': result.get('employee_number'),
                'is_admin': result.get('is_admin'),
                'id': result.get('id')
            }
            
            print("✅ Authentication successful!")
            print(f"User: {user_info['name']}")
            print(f"Employee: {user_info['employee_number']}")
            print(f"Admin: {user_info['is_admin']}")
            print(f"Token: {token[:50]}...")
            
            return token, user_info
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def create_browser_login_script(token, user_info):
    """Create JavaScript to inject into browser"""
    
    if not token or not user_info:
        return None
    
    # Create the JavaScript code to inject authentication
    js_code = f"""
// Manual authentication injection
console.log('🔑 Injecting authentication token...');

// Store the JWT token
localStorage.setItem('authToken', '{token}');

// Store user info
const userInfo = {json.dumps(user_info)};
localStorage.setItem('user', JSON.stringify(userInfo));

// Set authentication state in Redux store if available
if (window.__REDUX_STORE__) {{
    window.__REDUX_STORE__.dispatch({{
        type: 'auth/loginSuccess',
        payload: {{
            user: userInfo,
            token: '{token}'
        }}
    }});
}}

// Trigger a page reload to apply authentication
console.log('✅ Authentication injected! Reloading page...');
setTimeout(() => {{
    window.location.href = '/dashboard';
}}, 1000);
"""
    
    return js_code

def main():
    """Main execution"""
    
    print("🚀 Manual Browser Login")
    print("This will get an auth token and provide JavaScript to inject into browser")
    
    # Get authentication token
    token, user_info = get_auth_token()
    
    if token and user_info:
        # Create browser injection script
        js_code = create_browser_login_script(token, user_info)
        
        print("\n" + "=" * 60)
        print("BROWSER INJECTION SCRIPT")
        print("=" * 60)
        print("Copy and paste this JavaScript into the browser console:")
        print("\n" + "=" * 60)
        print(js_code)
        print("=" * 60)
        
        print("\n📋 Instructions:")
        print("1. Open browser developer tools (F12)")
        print("2. Go to Console tab")
        print("3. Paste the JavaScript code above")
        print("4. Press Enter to execute")
        print("5. The page should redirect to dashboard")
        
        # Also save to file for easy copying
        with open('browser_login_script.js', 'w') as f:
            f.write(js_code)
        
        print(f"\n💾 Script also saved to: browser_login_script.js")
        
    else:
        print("\n❌ Could not get authentication token")
        print("Backend authentication is not working properly")

if __name__ == "__main__":
    main()
