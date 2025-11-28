import requests
import json

# Test the backend API directly
url = "http://localhost:8000/api/v1/analyze"
payload = {"claim": "The Earth is round"}

print("🔵 Testing Backend API...")
print(f"URL: {url}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"\n📊 Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"\n❌ Error: {e}")
