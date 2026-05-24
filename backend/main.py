from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import region, site, tools, jobs

app = FastAPI(
    title="Marine Digital Twin Platform API",
    description="API for the Offshore Wind Simulation System",
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(region.router, prefix="/api", tags=["Region"])
app.include_router(site.router, prefix="/api", tags=["Site Validation"])
app.include_router(tools.router, prefix="/api", tags=["Simulation Tools"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])

@app.get("/")
def root():
    return {"message": "Marine Digital Twin Platform API is running"}
