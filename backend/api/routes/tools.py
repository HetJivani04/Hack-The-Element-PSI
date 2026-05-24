# pyrefly: ignore [missing-import]
from fastapi import APIRouter

router = APIRouter()

# Mocking the tool catalog
LAGRANGIAN_TOOL = {
    "tool_id": "lagrangian_tracking",
    "name": "Lagrangian Particle Tracking",
    "category": "physics_simulation",
    "description": "Release virtual particles at the windmill site and track their paths under real ocean currents, waves, tides, and wind. See where a spill, sediment plume, or larvae would drift.",
    "tier": 3,
    "expected_runtime_seconds": {
        "100_particles_24h": 5,
        "500_particles_7d": 30,
        "1000_particles_30d": 120,
        "5000_particles_90d": 600
    },
    "required_inputs": [
        {
            "variable_id": "1.12",
            "variable_name": "Eastward current velocity (uo)",
            "description": "Moves particles east-west at each depth",
            "source": "Copernicus PHY + HYCOM ensemble",
            "source_quality": "multi-model"
        },
        {
            "variable_id": "1.13",
            "variable_name": "Northward current velocity (vo)",
            "description": "Moves particles north-south at each depth",
            "source": "Copernicus PHY + HYCOM ensemble",
            "source_quality": "multi-model"
        }
    ],
    "optional_inputs": [
        {
            "variable_id": "3.20",
            "variable_name": "Stokes drift — eastward (VSDX)",
            "description": "Wave-driven surface transport. Important for surface releases.",
            "source": "Copernicus WAV",
            "included_by_default": True
        },
        {
            "variable_id": "3.21",
            "variable_name": "Stokes drift — northward (VSDY)",
            "description": "Wave-driven surface transport.",
            "source": "Copernicus WAV",
            "included_by_default": True
        },
        {
            "variable_id": "4.1",
            "variable_name": "Wind speed at 10m — eastward",
            "description": "Windage effect — wind pushes surface particles ~1-3% of wind speed",
            "source": "ERA5",
            "included_by_default": False
        },
        {
            "variable_id": "6.2",
            "variable_name": "Tidal currents (u/v constituents)",
            "description": "Adds tidal oscillation to particle paths. Important in coastal waters.",
            "source": "DFO WebTide",
            "included_by_default": True
        },
        {
            "variable_id": "2.1",
            "variable_name": "Sea surface height (zos)",
            "description": "Barotropic component — sea level variations drive shelf currents",
            "source": "Copernicus PHY",
            "included_by_default": True
        },
        {
            "variable_id": "2.7",
            "variable_name": "Mixed layer depth (mlotst)",
            "description": "Constrains vertical movement — particles stay within mixed layer",
            "source": "Copernicus PHY",
            "included_by_default": True
        },
        {
            "variable_id": "10.1",
            "variable_name": "Bathymetry",
            "description": "Land boundary — particles reflect off or beach on coastline",
            "source": "GEBCO 2026",
            "included_by_default": True
        }
    ],
    "user_parameters": [
        {
            "name": "n_particles",
            "label": "Number of particles",
            "type": "integer",
            "default": 500,
            "min": 10,
            "max": 10000,
            "description": "More particles = smoother density maps, slower runtime"
        },
        {
            "name": "release_depth_m",
            "label": "Release depth (m)",
            "type": "float",
            "default": 0,
            "min": 0,
            "max": 87,
            "max_source": "site_water_depth",
            "description": "0 = surface. Max is water depth at site (87m)."
        },
        {
            "name": "duration_hours",
            "label": "Simulation duration (hours)",
            "type": "integer",
            "default": 168,
            "min": 1,
            "max": 2160,
            "description": "168h = 1 week. Max 90 days."
        },
        {
            "name": "start_date",
            "label": "Release date",
            "type": "date",
            "default": "2025-06-01",
            "min": "1993-01-01",
            "max": "2026-05-23",
            "description": "What date to release particles. Different seasons = different currents."
        },
        {
            "name": "diffusivity_mode",
            "label": "Diffusion model",
            "type": "select",
            "options": [
                {"value": "auto", "label": "Auto-compute from stratification (recommended)"},
                {"value": "manual", "label": "Manual coefficient"}
            ],
            "default": "auto"
        }
    ],
    "outputs": [
        {"type": "geojson", "name": "particle_trajectories", "description": "All particle positions at each timestep for map animation"},
        {"type": "spatial_grid", "name": "particle_density", "description": "Probability of particle presence per grid cell"},
        {"type": "scalar", "name": "mean_displacement_km", "unit": "km"},
        {"type": "scalar", "name": "max_displacement_km", "unit": "km"},
        {"type": "scalar", "name": "residence_time_hours", "unit": "hours", "description": "Median time particles stay within 10km of site"},
        {"type": "time_series", "name": "displacement_timeseries", "unit": "km", "description": "Mean distance from site over time"},
        {"type": "time_series", "name": "dispersion_ellipse", "description": "Major/minor axis of particle cloud over time"},
        {"type": "grid", "name": "connectivity_matrix", "description": "Fraction of particles from site that reach each surrounding cell"},
        {"type": "figure", "name": "trajectory_map", "description": "PNG: trajectories overlaid on bathymetry"},
        {"type": "figure", "name": "displacement_plot", "description": "PNG: mean displacement vs time with uncertainty band"}
    ]
}

@router.get("/tools")
def get_tools():
    return [
        {
            "tool_id": "lagrangian_tracking",
            "name": "Lagrangian Particle Tracking",
            "category": "physics_simulation",
            "description": "Release virtual particles at the windmill site...",
            "tier": 3
        }
    ]

@router.get("/tools/{tool_id}")
def get_tool(tool_id: str):
    if tool_id == "lagrangian_tracking":
        return LAGRANGIAN_TOOL
    return {"error": "Tool not found"}
