import requests
import time

res = requests.post("http://127.0.0.1:8000/api/jobs", json={
    "tool_id": "lagrangian_tracking",
    "site": {"lat": 44.0, "lon": -63.0},
    "variables": {},
    "params": {}
})
job = res.json()
print("Created job:", job)
job_id = job["job_id"]

for i in range(10):
    res = requests.get(f"http://127.0.0.1:8000/api/jobs/{job_id}")
    status = res.json()
    print("Status:", status)
    if status.get("status") in ["completed", "failed"]:
        break
    time.sleep(2)

if status.get("status") == "completed":
    res = requests.get(f"http://127.0.0.1:8000/api/jobs/{job_id}/result")
    print("Result keys:", res.json().keys())
