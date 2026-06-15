import urllib.request
import json
import sys

url = "http://localhost:8000/login/"
data = json.dumps({"username": "Dra.Carmen", "password": "Gab2cardi"}).encode('utf-8')

try:
    print(f"Requesting local login: {url}")
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
    with urllib.request.urlopen(req) as response:
        status = response.status
        body = response.read().decode('utf-8')
        print(f"Status: {status}")
        print(f"Response: {body}")
except Exception as e:
    print(f"Error logging in locally: {e}", file=sys.stderr)
