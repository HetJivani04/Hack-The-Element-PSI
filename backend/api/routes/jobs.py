# pyrefly: ignore [missing-import]
from fastapi import APIRouter, BackgroundTasks, HTTPException
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import os
import json
import uuid
import sys
from datetime import datetime, timezone

# Ensure marine_platform is accessible (up 4 levels from this file to reach the root)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, root_dir)

from marine_platform.engine import Orchestrator, TurbineSpecification
from marine_platform.cube.reader import DataCube


router = APIRouter()

class JobRequest(BaseModel):
    tool_id: str
    site: Dict[str, Any]
    variables: Dict[str, bool]
    params: Dict[str, Any]


JOBS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "job_results")
os.makedirs(JOBS_DIR, exist_ok=True)
DB_PATH = os.path.join(JOBS_DIR, "db.json")

def load_db() -> Dict[str, dict]:
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_db(db: Dict[str, dict]):
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

# Initialize DB if empty
if not os.path.exists(DB_PATH):
    save_db({})

import queue
import threading

# Global job queue and worker
job_queue = queue.Queue()

def job_worker():
    while True:
        job_id, request_data = job_queue.get()
        print(f"Worker picked up job {job_id}")
        # Execute the heavy process
        process_job_task(job_id, request_data)
        job_queue.task_done()

# Start worker thread
worker_thread = threading.Thread(target=job_worker, daemon=True)
worker_thread.start()

def process_job_task(job_id: str, request_data: dict):
    """Actual worker task that processes the job with a minimum 30s delay."""
    db = load_db()
    if job_id not in db:
        return
        
    db[job_id]["status"] = "running"
    db[job_id]["start_time"] = datetime.now(timezone.utc).strftime("%b %d, %I:%M %p")
    save_db(db)
    
    start_time = time.time()
    
    try:
        if Orchestrator is None:
            raise ImportError("marine_platform could not be imported")

        # Parse site
        site_lat = request_data['site'].get('lat', 44.0)
        site_lon = request_data['site'].get('lon', -63.0)
        
        # Parse params
        params = request_data.get('params', {})
        turb_spec = TurbineSpecification(
            rated_power_MW=params.get('turbine_rating', 15.0),
            rotor_diameter_m=params.get('rotor_diameter', 240.0),
            hub_height_m=params.get('hub_height', 150.0)
        )

        cube = DataCube()
        orchestrator = Orchestrator(cube, turb_spec, site_lat, site_lon)
        
        tool_id = request_data['tool_id']
        if tool_id == "lagrangian_tracking":
            target_tools = ["C1_lagrangian", "A1_baseline"]
        elif tool_id == "all":
            target_tools = None 
        else:
            target_tools = None 

        print(f"[{job_id}] Starting Orchestrator pipeline for site ({site_lat}, {site_lon})...")
        results = orchestrator.run_all(tool_ids=target_tools)
        
        job_dir = os.path.join(JOBS_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        final_results = {}
        for t_id, t_res in results.items():
            final_results[t_id] = {
                "status": t_res.status,
                "outputs": t_res.outputs,
                "statistics": [{"name": s.name, "value": s.value, "unit": s.unit} for s in t_res.statistics],
                "warnings": t_res.warnings,
                "timing_s": t_res.timing_s
            }
            
        with open(os.path.join(job_dir, "result.json"), 'w') as f:
            json.dump(final_results, f, indent=2)

        # Enforce minimum 30 second delay for UX simulation
        elapsed = time.time() - start_time
        if elapsed < 30.0:
            print(f"[{job_id}] finished early ({elapsed:.1f}s), waiting {30.0 - elapsed:.1f}s to enforce 30s minimum...")
            time.sleep(30.0 - elapsed)

        db = load_db()
        db[job_id]["status"] = "completed"
        db[job_id]["runtime_seconds"] = round(time.time() - start_time, 2)
        db[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        db[job_id]["method"] = request_data.get('tool_id', 'Simulation')
        save_db(db)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[{job_id}] FAILED: {str(e)}")
        # Enforce minimum 30 second delay even on failure
        elapsed = time.time() - start_time
        if elapsed < 30.0:
            time.sleep(30.0 - elapsed)

        db = load_db()
        db[job_id]["status"] = "failed"
        db[job_id]["error"] = str(e)
        db[job_id]["runtime_seconds"] = round(time.time() - start_time, 2)
        save_db(db)


@router.post("/jobs")
def create_job(request: JobRequest):
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    
    # Generate a descriptive name
    tool_map = {
        "lagrangian_tracking": "Particle Drift Analysis",
        "nsga2_optimization": "Siting Optimization",
        "all": "Full Pipeline Assessment"
    }
    desc = tool_map.get(request.tool_id, f"Simulation {job_id[:4]}")
    
    db = load_db()
    db[job_id] = {
        "job_id": job_id,
        "description": desc,
        "tool_id": request.tool_id,
        "method": "Marine Engine",
        "status": "queued",
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "start_time": "",
        "estimated_runtime_seconds": 60,
    }
    save_db(db)
    
    # Send to background worker queue
    job_queue.put((job_id, request.dict()))
    
    return db[job_id]


@router.get("/jobs/history")
def get_job_history():
    """Return all jobs for the Job Management dashboard."""
    db = load_db()
    jobs = list(db.values())
    # Sort newest first
    jobs.sort(key=lambda x: x.get('queued_at', ''), reverse=True)
    return jobs


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Poll for job status."""
    db = load_db()
    if job_id not in db:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = db[job_id]
    
    if job["status"] in ["queued", "running"]:
        # Mock some progress
        return {
            "job_id": job_id,
            "status": job["status"],
            "progress": {
                "timesteps_completed": 84,
                "timesteps_total": 168,
                "percent": 50,
            }
        }
        
    if job["status"] == "completed":
        return job
        
    if job["status"] == "failed":
        return job

@router.get("/jobs/{job_id}/result")
def get_job_result(job_id: str):
    """Fetch the detailed simulation output JSON."""
    result_path = os.path.join(JOBS_DIR, job_id, "result.json")
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result not found or job incomplete")
        
    with open(result_path, 'r') as f:
        return json.load(f)
