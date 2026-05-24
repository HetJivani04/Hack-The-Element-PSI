"""DataCube — unified lazy-loading interface to all downloaded data."""
import os, json, pickle, zipfile
import numpy as np
import xarray as xr
import pandas as pd

DATA_DIR = '/Users/anandlo/Elements/Hack-The-Element-PSI/data'

class DataCube:
    """Lazy-loading interface that extracts variables from real data files.
    Never fabricates data — returns NaN for missing cells/times.
    """
    def __init__(self, metadata_path=None):
        if metadata_path is None:
            metadata_path = f'{DATA_DIR}/../cube/cube_metadata.json'
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                self.meta = json.load(f)
        else:
            from .builder import build_cube_metadata
            self.meta = build_cube_metadata()
        self._handles = {}
        self.grid = self.meta['grid']

    def get_source(self, source_id: str):
        """Get the source entry from metadata."""
        return self.meta['sources'].get(source_id)

    def load_source(self, source_id: str):
        """Load a data source, returning xarray Dataset or DataFrame."""
        if source_id in self._handles:
            return self._handles[source_id]

        entry = self.meta['sources'][source_id]
        path = entry['file']

        # Handle list of files (e.g., ERA5 yearly)
        if isinstance(path, list):
            datasets = []
            for p in sorted(path):
                if not os.path.exists(p): continue
                if self._is_zip(p):
                    ds = self._unzip_netcdf(p)
                else:
                    ds = xr.open_dataset(p)
                datasets.append(ds)
            if datasets:
                result = xr.concat(datasets, dim='valid_time' if 'valid_time' in datasets[0].dims else 'time')
            else:
                return None
        elif path.endswith('.pkl'):
            with open(path, 'rb') as f:
                result = pickle.load(f)
        elif path.endswith('.csv'):
            result = pd.read_csv(path, skiprows=[1] if 'ERDDAP' in str(path) else None)
        elif path.endswith('.json'):
            with open(path) as f:
                result = json.load(f)
        elif os.path.isdir(path):
            result = path  # directory reference (governance layers)
        elif self._is_zip(path):
            result = self._unzip_netcdf(path)
        elif path.endswith('.nc'):
            result = xr.open_dataset(path)
        else:
            return None

        self._handles[source_id] = result
        return result

    def extract(self, variable_id: str, site_lat=None, site_lon=None, time_start=None, time_end=None):
        """Extract a variable by its catalog ID at a site or for the full ROI.
        This is the main method tools call.
        """
        from marine_platform.variables.registry import get_variable
        var = get_variable(variable_id)
        if var is None:
            raise ValueError(f"Unknown variable ID: {variable_id}")

        data = self.load_source(var.cube_source)
        if data is None:
            return None

        varname = var.cube_variable_name

        # xarray Dataset
        if isinstance(data, xr.Dataset):
            if varname not in data.data_vars and varname not in data.coords:
                return None
            da = data[varname]

            # Subset spatially
            if site_lat is not None and site_lon is not None:
                lat_dim = [d for d in da.dims if 'lat' in str(d).lower()][0] if any('lat' in str(d).lower() for d in da.dims) else None
                lon_dim = [d for d in da.dims if 'lon' in str(d).lower()][0] if any('lon' in str(d).lower() for d in da.dims) else None
                if lat_dim and lon_dim:
                    da = da.sel(**{lat_dim: site_lat, lon_dim: site_lon}, method='nearest')

            # Subset temporally
            if time_start is not None:
                time_dim = [d for d in da.dims if 'time' in str(d).lower() or 'valid_time' in str(d).lower()][0]
                da = da.sel(**{time_dim: slice(time_start, time_end)})

            return da.values if hasattr(da, 'values') else da

        # DataFrame
        elif isinstance(data, pd.DataFrame):
            if site_lat and site_lon and 'latitude' in data.columns:
                idx = ((data['latitude']-site_lat)**2 + (data['longitude']-site_lon)**2).idxmin()
                return data.iloc[idx][varname] if varname in data.columns else None
            return data[varname].values if varname in data.columns else None

        return data

    def close(self):
        for k, v in self._handles.items():
            if hasattr(v, 'close'):
                try: v.close()
                except: pass
        self._handles.clear()

    @staticmethod
    def _is_zip(path):
        if not os.path.exists(path): return False
        with open(path, 'rb') as f:
            return f.read(2) == b'PK'

    @staticmethod
    def _unzip_netcdf(zip_path):
        import tempfile, shutil
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path) as zf:
            inst = [f for f in zf.namelist() if 'instant' in f.lower()]
            if inst:
                zf.extract(inst[0], tmp)
                ds = xr.open_dataset(f'{tmp}/{inst[0]}')
            else:
                zf.extractall(tmp)
                ncs = [f for f in os.listdir(tmp) if f.endswith('.nc')]
                ds = xr.open_dataset(f'{tmp}/{ncs[0]}') if ncs else None
        shutil.rmtree(tmp, ignore_errors=True)
        return ds


# ══════════════════════════════════════════════════════════════════════════════
# FusedCubeReader — reads from regridded Zarr cube produced by builder
# ══════════════════════════════════════════════════════════════════════════════

import zarr as _zarr

CUBE_DIR = '/Users/anandlo/Elements/Hack-The-Element-PSI/cube/fused'

DOMAIN_VAR_MAP = {
    'physics_3d': ['thetao', 'so', 'uo', 'vo', 'depth'],
    'seafloor': ['elevation', 'quality_flag'],
    'governance': ['mpa_mask'],
    'surface': ['SST'],
    'atmosphere': ['u10', 'v10', 'u100', 'v100', 't2m', 'msl'],
    'waves': ['VHM0', 'VTPK', 'VMDR', 'VSDX', 'VSDY', 'VTM10',
              'VHM0_WW', 'VMDR_WW', 'VTM01_WW',
              'VHM0_SW1', 'VMDR_SW1', 'VTM01_SW1'],
    'bgc': [],
    'species': ['occurrence_count', 'vessel_hours'],
    'human_activity': ['shipping_density', 'fishing_effort'],
}


class FusedCubeReader:
    """Lazy reader for the fused/regridded Zarr data cube.

    Opens domain stores on first access, extracts variables by name
    at specific sites via bilinear interpolation.
    """

    def __init__(self, cube_dir=CUBE_DIR):
        self.cube_dir = cube_dir
        self._stores = {}
        self._meta = self._load_metadata()

    def _load_metadata(self):
        meta_path = os.path.join(self.cube_dir, 'cube_metadata.json')
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                return json.load(f)
        return None

    @property
    def grid(self):
        if self._meta and 'grid' in self._meta:
            return self._meta['grid']
        from marine_platform.science.spatial import ROI_BOUNDS, LAT_CELLS, LON_CELLS, SPATIAL_RESOLUTION
        return {
            'lat_min': ROI_BOUNDS['lat_min'], 'lat_max': ROI_BOUNDS['lat_max'],
            'lon_min': ROI_BOUNDS['lon_min'], 'lon_max': ROI_BOUNDS['lon_max'],
            'resolution_deg': SPATIAL_RESOLUTION,
            'roi_lats': np.linspace(ROI_BOUNDS['lat_min'], ROI_BOUNDS['lat_max'], LAT_CELLS).tolist(),
            'roi_lons': np.linspace(ROI_BOUNDS['lon_min'], ROI_BOUNDS['lon_max'], LON_CELLS).tolist(),
        }

    @property
    def roi_lats(self):
        return np.array(self.grid.get('roi_lats', np.linspace(43.68, 44.83, 13)))

    @property
    def roi_lons(self):
        return np.array(self.grid.get('roi_lons', np.linspace(-64.33, -61.94, 28)))

    def _get_store(self, domain):
        if domain in self._stores:
            return self._stores[domain]
        store_path = os.path.join(self.cube_dir, f'{domain}.zarr')
        if os.path.exists(store_path):
            try:
                root = _zarr.open(store_path, mode='r')
                self._stores[domain] = root
                return root
            except Exception:
                return None
        return None

    def _find_variable(self, variable_name):
        for domain, vars_list in DOMAIN_VAR_MAP.items():
            if variable_name in vars_list:
                return domain, variable_name
        for domain in DOMAIN_VAR_MAP:
            store = self._get_store(domain)
            if store is not None and variable_name in store:
                return domain, variable_name
        return None, None

    def extract_point(self, variable_name, lat, lon, depth_m=None):
        """Extract scalar value at a site via bilinear interpolation."""
        domain, key = self._find_variable(variable_name)
        if domain is None:
            return None
        store = self._get_store(domain)
        if store is None or key not in store:
            return None

        data = store[key][:]
        rlats, rlons = self.roi_lats, self.roi_lons
        nlat, nlon = len(rlats), len(rlons)
        li = max(0, min(nlat - 2, np.searchsorted(rlats, lat) - 1))
        lj = max(0, min(nlon - 2, np.searchsorted(rlons, lon) - 1))

        dy = max(0.0, min(1.0, (lat - rlats[li]) / (rlats[li + 1] - rlats[li])))
        dx = max(0.0, min(1.0, (lon - rlons[lj]) / (rlons[lj + 1] - rlons[lj])))
        w00, w01 = (1 - dy) * (1 - dx), (1 - dy) * dx
        w10, w11 = dy * (1 - dx), dy * dx

        def _interp2d(arr, i, j):
            return (arr[i, j] * w00 + arr[i, j + 1] * w01 +
                    arr[i + 1, j] * w10 + arr[i + 1, j + 1] * w11)

        if data.ndim == 2:
            val = _interp2d(data, li, lj)
            return float(val) if not np.isnan(val) else None
        elif data.ndim == 3 and depth_m is not None:
            depths = store.get('depth', None)
            if depths is not None:
                depths = depths[:]
                dk = max(0, min(len(depths) - 2, np.searchsorted(depths, depth_m) - 1))
                dd = max(0.0, min(1.0, (depth_m - depths[dk]) / (depths[dk + 1] - depths[dk])))
                vl = _interp2d(data[dk], li, lj)
                vu = _interp2d(data[dk + 1], li, lj)
                val = (1 - dd) * vl + dd * vu
                return float(val) if not np.isnan(val) else None
            else:
                val = _interp2d(data[0], li, lj)
                return float(val) if not np.isnan(val) else None
        return None

    def extract_2d_field(self, variable_name):
        """Extract full 2D (lat, lon) field for the ROI."""
        domain, key = self._find_variable(variable_name)
        if domain is None:
            return None
        store = self._get_store(domain)
        if store is None or key not in store:
            return None
        return store[key][:]

    def get_bathymetry(self):
        return self.extract_2d_field('elevation')

    def get_mpa_mask(self):
        return self.extract_2d_field('mpa_mask')

    def get_quality_flags(self):
        return self.extract_2d_field('quality_flag')

    def site_summary(self, lat, lon):
        """Comprehensive data availability summary at a site."""
        return {
            'site': {'lat': lat, 'lon': lon},
            'depth_m': self.extract_point('elevation', lat, lon),
            'in_mpa': bool(self.extract_point('mpa_mask', lat, lon) or False),
            'physics': {v: self.extract_point(v, lat, lon) for v in ['thetao', 'so', 'uo', 'vo']},
            'atmosphere': {v: self.extract_point(v, lat, lon) for v in ['u10', 'v10', 'u100', 'v100', 't2m']},
            'waves': {v: self.extract_point(v, lat, lon) for v in ['VHM0', 'VTPK', 'VMDR']},
            'species': {'occurrence_count': self.extract_point('occurrence_count', lat, lon)},
            'human': {'shipping_density': self.extract_point('shipping_density', lat, lon),
                      'fishing_effort': self.extract_point('fishing_effort', lat, lon)},
            'quality_flag': self.extract_point('quality_flag', lat, lon),
        }

    def close(self):
        for s in self._stores.values():
            if hasattr(s, 'close'):
                try: s.close()
                except: pass
        self._stores.clear()

    def __enter__(self): return self
    def __exit__(self, *args): self.close()
