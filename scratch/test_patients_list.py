import sys
import os

# Add backend directory to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from src.database.patients_list import patients_list

try:
    print("Running patients_list(5)...")
    res = patients_list(5)
    print(f"Result length: {len(res)}")
    for patient in res:
        print(patient)
except Exception as e:
    print(f"Exception raised: {e}", file=sys.stderr)
