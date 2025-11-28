"""Test script for the analysis endpoint."""
import requests
import json

url = "http://127.0.0.1:8000/api/v1/analyze"

# Test claim
test_claim = "Apple Vision Pro sales"

print(f"Testing claim: {test_claim}")
print("-" * 50)

try:
    response = requests.post(url, json={"claim": test_claim}, timeout=120)
    result = response.json()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
