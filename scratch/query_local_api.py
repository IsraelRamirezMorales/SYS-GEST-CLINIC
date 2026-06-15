import urllib.request
import json
import sys

url = "http://localhost:8000/patients_appointments/?id_employees=5"

try:
    print(f"Requesting local API: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        status = response.status
        body = response.read().decode('utf-8')
        print(f"Status: {status}")
        print(f"Response: {body}")
except Exception as e:
    print(f"Error fetching from local API: {e}", file=sys.stderr)
