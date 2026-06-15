import urllib.request
import json
import sys

url = "http://localhost:8000/patients_list/?id_employees=5"

try:
    print(f"Requesting local patients list: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        status = response.status
        body = response.read().decode('utf-8')
        print(f"Status: {status}")
        print(f"Response (first 200 chars): {body[:200]}")
        data = json.loads(body)
        print(f"Total patients fetched: {len(data)}")
        print("Names in list:")
        for p in data:
            print(f"- {p['name']} {p['last_name']}")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
