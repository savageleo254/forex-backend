import requests

API_URL = "http://127.0.0.1:8000/trade/override"
API_KEY = "savage"

payload = {
    "trade_id": "TEST-001",
    "action": "close"
}

headers = {
    "x-api-key": API_KEY
}

response = requests.post(API_URL, json=payload, headers=headers)
print("Status:", response.status_code)
print("Response:", response.json())
