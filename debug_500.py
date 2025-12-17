
import requests

try:
    response = requests.get('http://127.0.0.1:8002/')
    print(f"Status: {response.status_code}")
    print(response.text)
except Exception as e:
    print(e)
