import requests
import json

url = "http://localhost:8000/api/v1/analyze"
payload = {"claim": "RAHUL GANDHI MEETS CONGRESS LEADERS Rahul Gandhi reportedly held meetings with Karnataka leaders"}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
