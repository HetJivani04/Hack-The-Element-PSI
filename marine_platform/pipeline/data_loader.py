"""Unified data loader — extracts ALL 155+ variables for a site.

Loads every registered variable from the DataCube, computes derived variables,
and returns a SiteData dataclass organized by domain. Uses FusedCubeReader
(bilinear interpolation) as primary path, DataCube (nearest-neighbor) as fallback.

No hardcoded variable lists — driven entirely by the registry.
"""

import numpy as np
import xarray as xr
import pandas as pd
from typing import Dict, Optional, List, Any, Tuple
from dataclasses import dataclass, field
import sys, os, time, warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from marine_platform.cube.reader import DataCube, FusedCubeReader
from marine_platform.variables.registry import (
    VARIABLES, Variable, get_variable, get_variables_for_tool,
)
from marine_platform.pipeline.derived import DerivedVariables

warnings.filterwarnings('ignore')


@dataclass
class SiteData:
    """All environmental data for a single site, organized by domain.

    Every variable from the registry is loaded if the data source exists.
    Missing variables are tracked with reason codes.
    """

    site_name: str = ""
    site_lat: float = 0.0
    site_lon: float = 0.0
    depth_m: float = 0.0

    # Organized by domain — each is a dict of var_name → value
    physics: Dict[str, Any] = field(default_factory=dict)
    surface: Dict[str, Any] = field(default_factory=dict)
    waves: Dict[str, Any] = field(default_factory=dict)
    atmosphere: Dict[str, Any] = field(default_factory=dict)
    bgc: Dict[str, Any] = field(default_factory=dict)
    species: Dict[str, Any] = field(default_factory=dict)
    seafloor: Dict[str, Any] = field(default_factory=dict)
    human: Dict[str, Any] = field(default_factory=dict)
    governance: Dict[str, Any] = field(default_factory=dict)
    derived: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    loaded_var_ids: List[str] = field(default_factory=list)
    missing_var_ids: List[Tuple[str, str]] = field(default_factory=list)  # (id, reason)
    load_stats: Dict[str, int] = field(default_factory=dict)

    # Convenience accessors
    @property
    def total_loaded(self) -> int:
        return len(self.loaded_var_ids)

    @property
    def total_missing(self) -> int:
        return len(self.missing_var_ids)

    def get_var(self, var_id: str) -> Optional[Any]:
        """Get a variable by ID from any domain."""
        for domain_dict in [self.physics, self.surface, self.waves, self.atmosphere,
                            self.bgc, self.species, self.seafloor, self.human,
                            self.governance, self.derived]:
            if var_id in domain_dict:
                return domain_dict[var_id]
        return None

    def print_summary(self):
        """Print loading summary."""
        n_total = self.total_loaded + self.total_missing
        print(f"\n  Site: {self.site_name} ({self.site_lat:.4f}N, {abs(self.site_lon):.4f}W)")
        print(f"  Depth: {self.depth_m:.1f}m")
        print(f"  Variables loaded: {self.total_loaded}/{n_total} ({100*self.total_loaded/max(n_total,1):.0f}%)")
        if self.missing_var_ids:
            print(f"  Missing: {self.total_missing}")
            # Group by reason
            reasons = {}
            for vid, reason in self.missing_var_ids:
                reasons[reason] = reasons.get(reason, 0) + 1
            for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
                print(f"    {count}: {reason}")


class DataLoader:
    """Unified data loader for a single site.

    Extracts every registered variable from the DataCube using the
    registry's cube_source and cube_variable_name mappings.
    Falls back gracefully when data is unavailable.
    """

    # Domain mapping for organizing loaded data
    _DOMAIN_MAP: Dict[str, str] = None

    def __init__(self, cube: DataCube, fused_reader: Optional[FusedCubeReader] = None):
        self.cube = cube
        self.fused = fused_reader

    def load_all(self, site_lat: float, site_lon: float,
                 site_name: str = "") -> SiteData:
        """Load all registered variables for a site.

        Returns SiteData with all successfully loaded variables.
        Variables that cannot be loaded are tracked in missing_var_ids.
        """
        t0 = time.time()
        site = SiteData(site_name=site_name, site_lat=site_lat, site_lon=site_lon)

        # Load depth first (needed for depth-dependent variables)
        depth_val = self._extract_var("10.1", site_lat, site_lon)
        if depth_val is not None:
            if hasattr(depth_val, '__len__'):
                site.depth_m = float(np.nanmean(np.asarray(depth_val)))
            else:
                site.depth_m = float(depth_val)
        site.seafloor['10.1'] = site.depth_m
        site.loaded_var_ids.append('10.1')

        # Iterate ALL registered variables
        for var_id, var in sorted(VARIABLES.items()):
            if var_id == '10.1':  # already loaded
                continue

            # Determine target domain dict
            domain = var.domain
            domain_dict = self._get_domain_dict(site, domain)

            # Skip computed variables — handled separately
            if var.cube_source == '__computed__':
                continue

            try:
                val = self._extract_var(var_id, site_lat, site_lon)
                if val is not None:
                    domain_dict[var_id] = val
                    site.loaded_var_ids.append(var_id)
                else:
                    site.missing_var_ids.append((var_id, f"no_data_for_{var.name}"))
            except Exception as e:
                site.missing_var_ids.append((var_id, f"extract_error:{str(e)[:50]}"))

        # Compute derived variables
        try:
            derived_vars = self._compute_derived(site)
            site.derived = derived_vars
        except Exception as e:
            site.missing_var_ids.append(('13.x', f"derived_compute_error:{str(e)[:50]}"))

        # Build stats
        site.load_stats = {
            'total_registry': len(VARIABLES),
            'loaded': site.total_loaded,
            'missing': site.total_missing,
            'load_time_s': time.time() - t0,
        }

        return site

    def _extract_var(self, var_id: str, lat: float, lon: float) -> Optional[Any]:
        """Extract a single variable from the cube.

        Uses FusedCubeReader for bilinear interpolation if available,
        falls back to DataCube.extract() for nearest-neighbor.
        """
        var = get_variable(var_id)
        if var is None or var.cube_source == '__computed__':
            return None

        # Try FusedCubeReader first (bilinear interpolation)
        if self.fused is not None:
            try:
                depth = 0.0 if not var.depth_dependent else None
                val = self.fused.extract_point(
                    var.cube_variable_name, lat, lon, depth=depth
                )
                if val is not None:
                    return val
            except Exception:
                pass

        # Fall back to DataCube (nearest-neighbor)
        try:
            return self.cube.extract(var_id, lat, lon)
        except Exception:
            return None

    def _get_domain_dict(self, site: SiteData, domain: str) -> Dict:
        """Get the appropriate domain dictionary for a variable."""
        domain_map = {
            'physics': site.physics,
            'waves': site.waves,
            'atmosphere': site.atmosphere,
            'bgc': site.bgc,
            'species': site.species,
            'seafloor': site.seafloor,
            'human': site.human,
            'governance': site.governance,
        }
        return domain_map.get(domain, site.physics)

    def _compute_derived(self, site: SiteData) -> Dict[str, Any]:
        """Compute derived variables from loaded data."""
        dv = DerivedVariables()

        # Build T/S profiles from loaded physics data
        T_arr = self._to_array(site.get_var('1.1'))
        S_arr = self._to_array(site.get_var('1.8'))
        u_arr = self._to_array(site.get_var('1.12'))
        v_arr = self._to_array(site.get_var('1.13'))

        if T_arr is not None and S_arr is not None:
            n_levels = min(len(T_arr), len(S_arr), 20)
            dv.T_profile = np.asarray(T_arr, dtype=float).ravel()[:n_levels]
            dv.S_profile = np.asarray(S_arr, dtype=float).ravel()[:n_levels]
            dv.depth_profile = np.linspace(0, site.depth_m, n_levels)

        if u_arr is not None and v_arr is not None and dv.depth_profile is not None:
            n_u = min(len(u_arr), len(v_arr), len(dv.depth_profile))
            dv.u_profile = np.asarray(u_arr, dtype=float).ravel()[:n_u]
            dv.v_profile = np.asarray(v_arr, dtype=float).ravel()[:n_u]
            dv.depth_profile = dv.depth_profile[:n_u]

        # Wind speed at hub height
        u100 = self._to_scalar(site.get_var('4.5'))
        v100 = self._to_scalar(site.get_var('4.6'))
        if u100 is not None and v100 is not None:
            dv.wind_speed_100m = float(np.sqrt(u100**2 + v100**2))
        else:
            dv.wind_speed_100m = None

        results = dv.compute_all()

        # Store descriptive results
        derived = {}
        for var_id in ['13.1', '13.2', '13.3', '13.4', '13.9']:
            if var_id in results:
                val = results[var_id]
                if isinstance(val, np.ndarray):
                    derived[var_id] = {'mean': float(np.nanmean(val)),
                                      'min': float(np.nanmin(val)),
                                      'max': float(np.nanmax(val)),
                                      'profile': val.tolist()[:10]}
                else:
                    derived[var_id] = val

        derived['_summary'] = dv.summary()
        return derived

    @staticmethod
    def _to_array(val: Any) -> Optional[np.ndarray]:
        """Safely convert a value to a numpy array."""
        if val is None:
            return None
        try:
            if isinstance(val, (xr.DataArray, xr.Dataset)):
                return val.values if hasattr(val, 'values') else np.asarray(val)
            return np.asarray(val)
        except Exception:
            return None

    @staticmethod
    def _to_scalar(val: Any) -> Optional[float]:
        """Safely convert a value to a scalar float."""
        if val is None:
            return None
        try:
            if hasattr(val, '__len__'):
                return float(np.nanmean(np.asarray(val)))
            return float(val)
        except Exception:
            return None
