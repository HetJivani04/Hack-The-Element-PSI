"""
Spatial grid definitions and geospatial utilities for the Scotian Shelf ROI.

The common grid specification from architecture.md:

    Latitude:  43.68 to 44.83 at 1/12 deg step  -> 13 lat cells
    Longitude: -64.33 to -61.94 at 1/12 deg step -> 28 lon cells
    Depth:     0.49m to seafloor, 50 vertical levels (Copernicus standard)
    Total cells: 13 x 28 = 364 horizontal cells x ~25 wet depth levels

All coordinates are WGS84. All areas use great-circle or local planar
approximations appropriate for the shelf scale (~130 km across).
"""

import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass
import math

# ── ROI Definition ───────────────────────────────────────────────────────────

ROI_BOUNDS = {
    "lat_min": 43.68,
    "lat_max": 44.83,
    "lon_min": -64.33,
    "lon_max": -61.94,
}

SPATIAL_RESOLUTION = 1.0 / 12.0  # degrees (~8 km at 45 deg N)
LAT_CELLS = 13
LON_CELLS = 28
GRID_CELL_COUNT = LAT_CELLS * LON_CELLS  # 364

# Copernicus standard depth levels (first 25 that cover Scotian Shelf, ~0-200m)
DEPTH_LEVELS = np.array([
    0.49, 1.54, 2.66, 3.87, 5.19, 6.64, 8.25, 10.05, 12.08, 14.37,
    16.96, 19.90, 23.23, 27.02, 31.33, 36.23, 41.79, 48.10, 55.24,
    63.32, 72.44, 82.74, 94.35, 107.42, 122.13, 138.73, 157.35,
    178.39, 202.16, 228.98,
], dtype=np.float64)

# Constants for geospatial calculations
EARTH_RADIUS_KM = 6371.0
DEG_TO_RAD = math.pi / 180.0

# Mean latitude of ROI for local planar approximations (~44.25 deg N)
_MID_LAT_RAD = 0.5 * (ROI_BOUNDS["lat_min"] + ROI_BOUNDS["lat_max"]) * DEG_TO_RAD
_M_PER_DEG_LAT = EARTH_RADIUS_KM * 1000.0 * DEG_TO_RAD  # ~111.32 km/deg
_M_PER_DEG_LON = EARTH_RADIUS_KM * 1000.0 * DEG_TO_RAD * math.cos(_MID_LAT_RAD)  # ~79.6 km/deg


# ── Grid Indexing ─────────────────────────────────────────────────────────────

def latlon_to_grid(lat: float, lon: float) -> Tuple[int, int]:
    """
    Convert WGS84 coordinates to grid cell indices [i_lat, i_lon].

    Args:
        lat: Latitude in degrees north (43.68 to 44.83)
        lon: Longitude in degrees east (-64.33 to -61.94)

    Returns:
        (i_lat, i_lon) zero-based indices. Ranges: i_lat in [0,12], i_lon in [0,27]

    Raises:
        ValueError: If coordinates are outside the ROI.
    """
    if not is_in_roi(lat, lon):
        raise ValueError(
            f"Coordinates ({lat:.4f}N, {lon:.4f}E) are outside the ROI "
            f"({ROI_BOUNDS['lat_min']}-{ROI_BOUNDS['lat_max']}N, "
            f"{ROI_BOUNDS['lon_min']}-{ROI_BOUNDS['lon_max']}E)"
        )

    i_lat = int((lat - ROI_BOUNDS["lat_min"]) / SPATIAL_RESOLUTION)
    i_lon = int((lon - ROI_BOUNDS["lon_min"]) / SPATIAL_RESOLUTION)

    # Clamp to valid range (edge case at upper bound)
    i_lat = min(i_lat, LAT_CELLS - 1)
    i_lon = min(i_lon, LON_CELLS - 1)

    return i_lat, i_lon


def grid_to_latlon(i_lat: int, i_lon: int) -> Tuple[float, float]:
    """
    Convert grid cell indices to the cell center coordinates.

    Args:
        i_lat: Latitude index [0, 12]
        i_lon: Longitude index [0, 27]

    Returns:
        (lat, lon) cell center in WGS84 degrees.
    """
    lat = ROI_BOUNDS["lat_min"] + (i_lat + 0.5) * SPATIAL_RESOLUTION
    lon = ROI_BOUNDS["lon_min"] + (i_lon + 0.5) * SPATIAL_RESOLUTION
    return lat, lon


def is_in_roi(lat: float, lon: float) -> bool:
    """Check if coordinates fall within the ROI bounding box."""
    return (
        ROI_BOUNDS["lat_min"] <= lat <= ROI_BOUNDS["lat_max"]
        and ROI_BOUNDS["lon_min"] <= lon <= ROI_BOUNDS["lon_max"]
    )


def flatten_grid_index(i_lat: int, i_lon: int) -> int:
    """Convert 2D grid index to flat index (row-major)."""
    return i_lat * LON_CELLS + i_lon


def unflatten_grid_index(flat_idx: int) -> Tuple[int, int]:
    """Convert flat index back to 2D grid index."""
    return flat_idx // LON_CELLS, flat_idx % LON_CELLS


# ── Spatial Metrics ───────────────────────────────────────────────────────────

def grid_cell_area_km2(i_lat: int, i_lon: int) -> float:
    """
    Compute the area of a grid cell in km^2 at the cell's latitude.

    Uses the spherical approximation: dA = R^2 * dlat * dlon * cos(lat).

    Args:
        i_lat: Latitude index
        i_lon: Longitude index (unused, area depends only on latitude)

    Returns:
        Cell area in km^2.
    """
    lat_rad = grid_to_latlon(i_lat, i_lon)[0] * DEG_TO_RAD
    dlat_rad = SPATIAL_RESOLUTION * DEG_TO_RAD
    dlon_rad = SPATIAL_RESOLUTION * DEG_TO_RAD
    area_m2 = EARTH_RADIUS_KM**2 * 1e6 * dlat_rad * dlon_rad * math.cos(lat_rad)
    return area_m2 / 1e6  # km^2


def distance_between_cells(i1: Tuple[int, int], i2: Tuple[int, int]) -> float:
    """
    Haversine distance between two grid cell centers in km.

    Args:
        i1: (i_lat, i_lon) of first cell
        i2: (i_lat, i_lon) of second cell

    Returns:
        Distance in km.
    """
    lat1, lon1 = grid_to_latlon(*i1)
    lat2, lon2 = grid_to_latlon(*i2)

    dlat = (lat2 - lat1) * DEG_TO_RAD
    dlon = (lon2 - lon1) * DEG_TO_RAD
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1 * DEG_TO_RAD)
        * math.cos(lat2 * DEG_TO_RAD)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def distance_to_shore_km(lat: float, lon: float, coastline_mask: np.ndarray) -> float:
    """
    Compute minimum distance from a point to the nearest shoreline cell.

    Args:
        lat, lon: Point coordinates in WGS84
        coastline_mask: 2D boolean array (13x28), True where cell contains coastline
                        (derived from GEBCO bathymetry at 0m contour)

    Returns:
        Distance in km to nearest coastline cell.
    """
    if not is_in_roi(lat, lon):
        return -1.0  # outside ROI

    coast_indices = np.argwhere(coastline_mask)
    if len(coast_indices) == 0:
        return 999.0  # no coastline in ROI (should not happen)

    i_lat, i_lon = latlon_to_grid(lat, lon)
    distances = np.array([
        distance_between_cells((i_lat, i_lon), (ci, cj))
        for ci, cj in coast_indices
    ])
    return float(np.min(distances))


# ── Grid Mesh Construction ────────────────────────────────────────────────────

@dataclass
class GridMesh:
    """Container for the full ROI grid mesh arrays."""
    lat_centers: np.ndarray    # shape (13, 28)
    lon_centers: np.ndarray    # shape (13, 28)
    lat_edges: np.ndarray      # shape (14,)
    lon_edges: np.ndarray      # shape (29,)
    cell_areas_km2: np.ndarray # shape (13, 28)
    flat_indices: np.ndarray   # shape (13, 28) — flattened cell index

    @property
    def shape(self) -> Tuple[int, int]:
        return self.lat_centers.shape


def build_grid_mesh() -> GridMesh:
    """
    Build the full 13x28 grid mesh with cell centers, edges, and areas.

    Returns:
        GridMesh with pre-computed spatial arrays.
    """
    lat_edges = np.linspace(
        ROI_BOUNDS["lat_min"],
        ROI_BOUNDS["lat_max"],
        LAT_CELLS + 1
    )
    lon_edges = np.linspace(
        ROI_BOUNDS["lon_min"],
        ROI_BOUNDS["lon_max"],
        LON_CELLS + 1
    )

    lat_centers = 0.5 * (lat_edges[:-1] + lat_edges[1:])
    lon_centers = 0.5 * (lon_edges[:-1] + lon_edges[1:])

    lon_grid, lat_grid = np.meshgrid(lon_centers, lat_centers)

    # Pre-compute cell areas
    cell_areas = np.zeros((LAT_CELLS, LON_CELLS))
    for i in range(LAT_CELLS):
        area = grid_cell_area_km2(i, 0)
        cell_areas[i, :] = area

    flat_indices = np.arange(LAT_CELLS * LON_CELLS).reshape(LAT_CELLS, LON_CELLS)

    return GridMesh(
        lat_centers=lat_grid,
        lon_centers=lon_grid,
        lat_edges=lat_edges,
        lon_edges=lon_edges,
        cell_areas_km2=cell_areas,
        flat_indices=flat_indices,
    )


# ── Depth Utilities ───────────────────────────────────────────────────────────

def find_depth_index(target_depth: float) -> int:
    """
    Find the Copernicus depth level index closest to the target depth.

    Args:
        target_depth: Depth in meters (positive down)

    Returns:
        Index into DEPTH_LEVELS array.
    """
    return int(np.argmin(np.abs(DEPTH_LEVELS - target_depth)))


def get_bottom_indices(bathymetry_field: np.ndarray) -> np.ndarray:
    """
    For each horizontal grid cell, find the deepest valid depth level above
    the seafloor.

    Args:
        bathymetry_field: 2D array (13, 28) of depth in meters (positive down)

    Returns:
        2D array (13, 28) of depth level indices.
    """
    bottom_idx = np.zeros((LAT_CELLS, LON_CELLS), dtype=int)
    for i in range(LAT_CELLS):
        for j in range(LON_CELLS):
            depth = bathymetry_field[i, j]
            if np.isnan(depth) or depth <= 0:
                bottom_idx[i, j] = 0
            else:
                valid = DEPTH_LEVELS <= depth
                bottom_idx[i, j] = np.argmax(DEPTH_LEVELS > depth) - 1 if np.any(~valid) else len(DEPTH_LEVELS) - 1
    return bottom_idx


# ── Coordinate Transform Utilities ────────────────────────────────────────────

def rotate_velocity_to_earth(u_grid: float, v_grid: float, lat: float, lon: float) -> Tuple[float, float]:
    """
    Rotate model-native velocity components to geographic east/north if needed.
    Most Copernicus and HYCOM output is already in geographic coordinates,
    so this is typically a pass-through. Included for completeness.

    Args:
        u_grid, v_grid: Raw model velocity components (m/s)
        lat, lon: Position (unused for standard lat-lon grids)

    Returns:
        (u_east, v_north) geographic velocity components.
    """
    return u_grid, v_grid


def great_circle_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute initial bearing (azimuth) from point 1 to point 2.

    Returns:
        Bearing in degrees (0 = north, 90 = east).
    """
    lat1_r, lon1_r = lat1 * DEG_TO_RAD, lon1 * DEG_TO_RAD
    lat2_r, lon2_r = lat2 * DEG_TO_RAD, lon2 * DEG_TO_RAD

    dlon = lon2_r - lon1_r
    y = math.sin(dlon) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon)
    bearing = math.atan2(y, x) / DEG_TO_RAD

    return (bearing + 360.0) % 360.0
