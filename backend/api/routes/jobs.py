# pyrefly: ignore [missing-import]
from fastapi import APIRouter, BackgroundTasks
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Dict, Any
import time

router = APIRouter()

class JobRequest(BaseModel):
    tool_id: str
    site: Dict[str, Any]
    variables: Dict[str, bool]
    params: Dict[str, Any]

# In-memory mock jobs db
jobs_db = {}

def mock_processing(job_id: str):
    # Simulate a quick processing for demo purposes
    time.sleep(5) 
    jobs_db[job_id]["status"] = "completed"

@router.post("/jobs")
def create_job(request: JobRequest, background_tasks: BackgroundTasks):
    import uuid
    from datetime import datetime, timezone
    
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    
    # Store initial status
    jobs_db[job_id] = {
        "job_id": job_id,
        "tool_id": request.tool_id,
        "tool_name": "Simulation Tool",
        "status": "queued",
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "estimated_runtime_seconds": 30,
        "poll_interval_ms": 2000
    }
    
    # Start background process
    background_tasks.add_task(mock_processing, job_id)
    
    return jobs_db[job_id]

@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs_db:
        return {"error": "Job not found"}
        
    job = jobs_db[job_id]
    
    if job["status"] == "queued" or job["status"] == "running":
        # We can update the status to running if it was queued
        if job["status"] == "queued":
             job["status"] = "running"
        return {
            "job_id": job_id,
            "status": "running",
            "progress": {
                "timesteps_completed": 84,
                "timesteps_total": 168,
                "percent": 50,
                "particles_active": 487,
                "particles_beached": 13
            }
        }
        
    if job["status"] == "completed":
        from datetime import datetime, timezone
        return {
            "job_id": job_id,
            "status": "completed",
            "runtime_seconds": 5.0,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "result": {
                "scalars": {
                    "mean_displacement_km": {
                        "value": 34.2,
                        "unit": "km",
                        "interpretation": "Average distance particles traveled"
                    },
                    "particles_beached": {
                        "value": 13,
                        "unit": "count",
                        "interpretation": "Particles hit coastline"
                    }
                },
                "data_sources_used": {
                    "currents": "Copernicus PHY + HYCOM ensemble",
                    "tides": "DFO WebTide",
                    "bathymetry": "GEBCO 2026"
                }
            }
        }
