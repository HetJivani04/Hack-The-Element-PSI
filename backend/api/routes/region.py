from fastapi import APIRouter

router = APIRouter()

@router.get("/region")
def get_region():
    return {
        "region": {
            "name": "Scotian Shelf",
            "bounds": {
                "southwest": {"lat": 43.68, "lon": -64.33},
                "northeast": {"lat": 44.83, "lon": -61.94}
            },
            "grid": {
                "spatial_resolution": "1/12 degree (~8 km)",
                "lat_cells": 13,
                "lon_cells": 28,
                "depth_levels": 50
            }
        },
        "temporal_coverage": {
            "earliest": "1993-01-01T00:00:00Z",
            "latest": "2026-05-23T00:00:00Z",
            "reanalysis_end": "2023-12-31T00:00:00Z",
            "nrt_start": "2024-01-01T00:00:00Z"
        },
        "variable_summary": {
            "total_variables": 169,
            "domains": [
                {"name": "3D Physics", "count": 25, "id": "physics"},
                {"name": "Waves & Stokes", "count": 28, "id": "waves"},
                {"name": "Atmosphere", "count": 23, "id": "atmosphere"},
                {"name": "Biogeochemistry", "count": 23, "id": "bgc"},
                {"name": "Biology & Species", "count": 9, "id": "biology"},
                {"name": "Seafloor", "count": 5, "id": "seafloor"},
                {"name": "Human Activity", "count": 6, "id": "human"},
                {"name": "Governance", "count": 9, "id": "governance"}
            ]
        }
    }
