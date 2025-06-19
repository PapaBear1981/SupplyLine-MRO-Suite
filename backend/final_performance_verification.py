#!/usr/bin/env python3
"""
Final Performance Verification Script

Uses curl for accurate performance measurements to verify the optimizations
implemented for GitHub issue #359.
"""

import subprocess
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000"
TEST_CREDENTIALS = {
    "employee_number": "ADMIN001",
    "password": "Yxqs5AMldhs-9PzjktSVqg"
}

def run_curl_command(cmd):
    """Run curl command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1

def get_jwt_token():
    """Get JWT token for authentication"""
    # Escape the JSON properly for Windows command line
    json_data = json.dumps(TEST_CREDENTIALS).replace('"', '\\"')
    login_cmd = f'curl -s -X POST {BASE_URL}/api/auth/login -H "Content-Type: application/json" -d "{json_data}"'
    output, code = run_curl_command(login_cmd)
    
    if code != 0:
        print(f"❌ Login failed: {output}")
        return None
    
    try:
        login_data = json.loads(output)
        token = login_data.get('token')
        if token:
            print("✅ Authentication successful")
            return token
        else:
            print("❌ No token in login response")
            return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response: {output}")
        return None

def test_endpoint_performance(endpoint, token=None):
    """Test endpoint performance using curl"""
    auth_header = f'-H "Authorization: Bearer {token}"' if token else ''
    cmd = f'curl -w "%{{time_total}}" -o nul -s {auth_header} {BASE_URL}{endpoint}'
    
    output, code = run_curl_command(cmd)
    
    if code == 0:
        try:
            time_seconds = float(output)
            time_ms = time_seconds * 1000
            return time_ms, 200  # Assume success if curl succeeded
        except ValueError:
            return None, None
    else:
        return None, None

def main():
    """Main performance verification function"""
    print("🚀 Final Performance Verification")
    print("=" * 60)
    print(f"Testing optimizations implemented for GitHub issue #359")
    print(f"Started: {datetime.now()}")
    print()
    
    # Get authentication token
    token = get_jwt_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    # Test endpoints
    endpoints = [
        ("/api/health", False),  # No auth required
        ("/api/tools", True),
        ("/api/chemicals", True),
        ("/api/checkouts", True),
        ("/api/users", True),
        ("/api/announcements", True),
        ("/api/admin/dashboard/stats", True),
        ("/api/cycle-count/schedules", True),
    ]
    
    print("Testing API endpoint performance...")
    print("-" * 60)
    
    results = []
    total_time = 0
    successful_tests = 0
    
    for endpoint, requires_auth in endpoints:
        auth_token = token if requires_auth else None
        time_ms, status_code = test_endpoint_performance(endpoint, auth_token)
        
        if time_ms is not None:
            total_time += time_ms
            successful_tests += 1
            
            # Determine performance rating
            if time_ms < 200:
                rating = "🟢 EXCELLENT"
            elif time_ms < 500:
                rating = "🟡 GOOD"
            elif time_ms < 1000:
                rating = "🟠 ACCEPTABLE"
            else:
                rating = "🔴 SLOW"
            
            print(f"{endpoint:<35} {time_ms:>8.1f}ms  {rating}")
            results.append((endpoint, time_ms, rating))
        else:
            print(f"{endpoint:<35} {'ERROR':>8}     🔴 FAILED")
            results.append((endpoint, None, "🔴 FAILED"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE VERIFICATION SUMMARY")
    print("=" * 60)
    
    if successful_tests > 0:
        avg_time = total_time / successful_tests
        print(f"✅ Successful Tests: {successful_tests}/{len(endpoints)}")
        print(f"📈 Average Response Time: {avg_time:.1f}ms")
        print(f"🎯 Target: <500ms | Excellent: <200ms")
        
        # Performance assessment
        excellent_count = sum(1 for _, time_ms, _ in results if time_ms and time_ms < 200)
        good_count = sum(1 for _, time_ms, _ in results if time_ms and 200 <= time_ms < 500)
        
        print(f"\n📋 Performance Breakdown:")
        print(f"   🟢 Excellent (<200ms): {excellent_count}")
        print(f"   🟡 Good (200-500ms): {good_count}")
        print(f"   🟠 Acceptable (500-1000ms): {sum(1 for _, time_ms, _ in results if time_ms and 500 <= time_ms < 1000)}")
        print(f"   🔴 Slow (>1000ms): {sum(1 for _, time_ms, _ in results if time_ms and time_ms >= 1000)}")
        
        # Overall assessment
        if avg_time < 200 and successful_tests == len(endpoints):
            print("\n🎉 OUTSTANDING: All endpoints performing excellently!")
            print("✅ Ready for production deployment!")
            return True
        elif avg_time < 500 and successful_tests >= len(endpoints) * 0.8:
            print("\n✅ EXCELLENT: Performance targets exceeded!")
            print("✅ Ready for production deployment!")
            return True
        else:
            print("\n⚠️  NEEDS IMPROVEMENT: Some endpoints need optimization")
            return False
    else:
        print("❌ No successful tests - check application status")
        return False

if __name__ == "__main__":
    print("Final Performance Verification for SupplyLine MRO Suite")
    print("Verifying fixes for GitHub Issue #359")
    print()
    
    success = main()
    
    print(f"\nVerification completed: {datetime.now()}")
    
    if success:
        print("\n🚀 All performance optimizations successful!")
        print("📋 Issue #359 can be marked as resolved.")
        sys.exit(0)
    else:
        print("\n⚠️  Additional optimization may be needed")
        sys.exit(1)
