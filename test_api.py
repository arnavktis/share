"""
Simple test script to verify the Flask API is working
Run this after starting the API server (python api.py)
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_summary():
    """Test summary endpoint"""
    print("\n📊 Testing Summary Endpoint...")
    response = requests.get(f"{BASE_URL}/api/summary")
    print(f"Status: {response.status_code}")
    data = response.json()
    if 'error' not in data:
        print(f"Total Records: {data.get('total_records')}")
        print(f"Total Variance: ${data.get('total_variance', 0):.2f}")
        print(f"Classification Breakdown: {data.get('classification_breakdown')}")
    else:
        print(f"Error: {data['error']}")
    return response.status_code == 200

def test_disputable():
    """Test disputable items endpoint"""
    print("\n⚠️  Testing Disputable Items Endpoint...")
    response = requests.get(f"{BASE_URL}/api/disputable-items")
    print(f"Status: {response.status_code}")
    data = response.json()
    if 'error' not in data:
        print(f"Total Disputable: {data.get('total_disputable')}")
        print(f"Total Disputable Amount: ${data.get('total_disputable_amount', 0):.2f}")
    else:
        print(f"Error: {data['error']}")
    return response.status_code == 200

def test_filter():
    """Test filter endpoint"""
    print("\n🔎 Testing Filter Endpoint...")
    filters = {
        "classification": "Disputable"
    }
    response = requests.post(
        f"{BASE_URL}/api/filter",
        json=filters,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    if 'error' not in data:
        print(f"Filtered Records: {data.get('total_records')}")
        print(f"Filters Applied: {data.get('filters_applied')}")
    else:
        print(f"Error: {data['error']}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 Flask API Test Suite")
    print("=" * 50)
    print("\nMake sure the API is running: python api.py")
    
    try:
        tests = [
            ("Health Check", test_health),
            ("Summary", test_summary),
            ("Disputable Items", test_disputable),
            ("Filter", test_filter)
        ]
        
        results = []
        for name, test_func in tests:
            try:
                success = test_func()
                results.append((name, success))
            except requests.exceptions.ConnectionError:
                print(f"\n❌ Cannot connect to API. Is it running?")
                print("Start it with: python api.py")
                return
            except Exception as e:
                print(f"\n❌ Error in {name}: {str(e)}")
                results.append((name, False))
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 Test Results Summary")
        print("=" * 50)
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {name}")
        
        passed = sum(1 for _, success in results if success)
        print(f"\n{passed}/{len(results)} tests passed")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")

if __name__ == "__main__":
    main()
