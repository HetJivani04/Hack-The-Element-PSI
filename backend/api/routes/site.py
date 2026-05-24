# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/site/validate")
def validate_site(lon: float = Query(...), lat: float = Query(...)):
    # Mocking validation logic for now
    return {
        "valid": True,
        "site": {
            "lon": lon,
            "lat": lat,
            "water_depth_m": 87.3,
            "grid_cell": {"lat_index": 5, "lon_index": 14}
        },
        "data_availability": {
            "in_cube": True,
            "coverage_start": "1993-01-01",
            "coverage_end": "2026-05-23",
            "nearest_buoy": {
                "id": "SMA_halifax",
                "name": "Halifax Herring Cove Buoy",
                "distance_km": 28.4,
                "variables": ["waves", "wind", "SST", "current_profiles"]
            },
            "nearest_ctd_station": {
                "id": "AZMP_HL2",
                "name": "Halifax Line Station 2",
                "distance_km": 15.7,
                "profile_count": 47
            }
        },
        "governance_check": {
            "inside_mpa": False,
            "nearest_mpa_km": 12.3,
            "nearest_mpa_name": "The Gully Marine Protected Area",
            "inside_lease_block": False
        },
        "data_quality_summary": {
            "physics_3d": "multi-model (Copernicus + HYCOM), buoy 28.4 km away",
            "waves": "3-model ensemble (Copernicus WAV + ERA5 + DWD ICON), buoy 28.4 km away",
            "biogeochemistry": "single-model (Copernicus BGC), nearest CTD 15.7 km away",
            "species": "OBIS records present in this grid cell",
            "sediment": "NOT AVAILABLE for this location"
        }
    }
