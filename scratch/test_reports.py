import urllib.request
import json
import sys

url = "http://localhost:8000/reports/?id_employees=5"

try:
    print(f"Requesting local reports data: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        status = response.status
        body = response.read().decode('utf-8')
        print(f"Status: {status}")
        data = json.loads(body)
        print("Response structure keys:", list(data.keys()))
        print("Week total:", data["week"]["total"])
        print("Month total:", data["month"]["total"])
        print("Year total:", data["year"]["total"])
        print("Month types:", data["month"]["types"])
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
