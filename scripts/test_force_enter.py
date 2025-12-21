import requests
import json

url = "http://localhost:8080/api/v1/forceenter"
auth = ("admin", "pass789")
payload = {
    "pair": "ADA/USDT",
    "side": "long",
    "stakeamount": 5.0
}

try:
    response = requests.post(url, json=payload, auth=auth)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
