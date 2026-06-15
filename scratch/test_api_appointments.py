import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

try:
    print("Requesting /patients_appointments/?id_employees=5...")
    response = client.get("/patients_appointments/?id_employees=5")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Exception raised: {e}", file=sys.stderr)
