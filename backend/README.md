# Offshore Wind Simulation Platform - Backend

This directory contains the Python FastAPI backend for the Offshore Wind Simulation Platform.

## Work Completed (Phases 1 & 2)

During the initial development phases, we set up the foundational architecture and API layer to support the interactive 3D Globe frontend. 

1. **Project Initialization**
   - Created a clean Python virtual environment.
   - Initialized the application using `FastAPI` for high-performance async endpoint handling and `Uvicorn` as the ASGI server.
   - Set up `pydantic` models for structured request/response validation.

2. **API Endpoints (Mock Implementation)**
   We implemented the endpoints defined in the API contract. Currently, they are mocked to provide the necessary data structure for frontend integration testing:
   - `GET /api/region`: Returns the spatial and temporal bounds for the Scotian Shelf focus area.
   - `GET /api/site/validate`: Validates latitude/longitude points and checks parameters like bathymetry depth.
   - `GET /api/tools`: Lists available simulation tools.
   - `GET /api/tools/{tool_id}`: Returns the dynamic JSON schema parameters required for a specific tool (e.g., Lagrangian Particle Tracking).
   - `POST /api/jobs`: Accepts simulation parameters and initiates an async background job.
   - `GET /api/jobs/{job_id}`: Polls the status of a running simulation job (progress percentages and mock trajectories).

3. **Routing Architecture**
   Organized the backend into logical routers under `api/routes/`:
   - `region.py`
   - `site.py`
   - `tools.py`
   - `jobs.py`

## Running Locally

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Development Server**
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
   
   The API will be available at `http://127.0.0.1:8000`. You can also view the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.
