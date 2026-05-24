"""Build the fused data cube from all downloaded data files."""
import os, json, pickle, zipfile, glob
import numpy as np
import xarray as xr

DATA_DIR = '/Users/anandlo/Elements/Hack-The-Element-PSI/data'

def build_cube_metadata() -> dict:
    """Scan data directory and build metadata mapping every file to variables."""
    cube = {
        'grid': {'lat_min': 43.68, 'lat_max': 44.83, 'lon_min': -64.33, 'lon_max': -61.94,
                 'resolution_deg': 1/12, 'description': '1/12° (~8km) common grid over Scotian Shelf ROI'},
        'sources': {}
    }

    def _add(src_id, file_path, variables, time_range, time_res, spatial_res, quality):
        cube['sources'][src_id] = {
            'file': file_path, 'variables': variables,
            'time_range': time_range, 'time_resolution': time_res,
            'spatial_resolution': spatial_res, 'quality_flag': quality
        }

    # GLORYS12 reanalysis
    _add('glorys_physics', f'{DATA_DIR}/glorys_physics_2016_2023.nc',
         ['thetao','so','uo','vo','zos','mlotst','bottomT','siconc','sithick','usi','vsi'],
         '2016-2023','daily','1/12°',2)

    # NRT 3D
    for vname, fname in [('thetao','thetao_nrt_2024_2026.nc'),('so','so_nrt_2024_2026.nc'),
                          ('cur','cur_nrt_2024_2026.nc')]:
        if os.path.exists(f'{DATA_DIR}/{fname}'):
            _add(f'{vname}_nrt', f'{DATA_DIR}/{fname}', [vname], '2024-2026', '6-hourly', '1/12°', 3)

    # Merged UV
    _add('merged_uv_nrt', f'{DATA_DIR}/merged_uv_nrt_2024_2026.nc',
         ['utotal','vtotal','utide','vtide','vsdx','vsdy'], '2024-2026', 'hourly', '1/12°', 2)

    # Surface 2D
    _add('surface_2d', f'{DATA_DIR}/surface_2d_2016_2026.nc',
         ['zos','mlotst','tob','sob','siconc','sithick','ist','pbo','siage','sialb','sisnthick','sivelo','usi','vsi'],
         '2022-2026','daily','1/12°',2)

    # SST anomaly
    _add('sst_anomaly', f'{DATA_DIR}/sst_anomaly_2023_2026.nc',
         ['sea_surface_temperature_anomaly'], '2023-2026', 'daily', '1/12°', 2)

    # Bathymetry
    _add('bathymetry', f'{DATA_DIR}/bathymetry_copernicus.nc',
         ['deptho','deptho_lev','mask'], 'static', 'static', '1/12°', 3)

    # Waves NRT
    _add('waves_nrt', f'{DATA_DIR}/waves_copernicus_2024_2026.nc',
         ['VHM0','VTPK','VMDR','VTM10','VTM02','VCMX','VMXL','VPED',
          'VHM0_WW','VMDR_WW','VTM01_WW','VHM0_SW1','VMDR_SW1','VTM01_SW1',
          'VHM0_SW2','VMDR_SW2','VTM01_SW2','VSDX','VSDY'],
         '2024-2026','3-hourly','1/12°',2)

    # Waves reanalysis
    _add('waves_reanalysis', f'{DATA_DIR}/waves_waverys_2016_2023.nc',
         ['VHM0','VTPK','VMDR','VTM02','VHM0_WW','VMDR_WW','VHM0_SW1','VHM0_SW2'],
         '2016-2023','3-hourly','0.2°',4)

    # BGC
    for bgc_var, fname in [('bio','bgc_bio_2024_2026.nc'),('nut','bgc_nut_2024_2026.nc'),
                            ('car','bgc_car_2024_2026.nc'),('co2','bgc_co2_2024_2026.nc'),
                            ('pft','bgc_pft_2024_2026.nc'),('plankton','bgc_plankton_2024_2026.nc'),
                            ('optics','bgc_optics_2024_2026.nc')]:
        path = f'{DATA_DIR}/{fname}'
        if os.path.exists(path):
            ds = xr.open_dataset(path)
            _add(f'bgc_{bgc_var}', path, list(ds.data_vars.keys()), '2024-2026', 'daily', '0.25°', 3)
            ds.close()

    # ERA5 atmosphere
    era5_files = sorted(glob.glob(f'{DATA_DIR}/era5_atmosphere_*.nc'))
    if era5_files:
        _add('era5_atmosphere', era5_files,
             ['u10','v10','u100','v100','t2m','msl','sst','blh','zust','tp'],
             '2016-2025','6-hourly','0.25°',3)

    # In-situ
    _add('sma_halifax', f'{DATA_DIR}/SMA_halifax_full_2016_2026.csv',
         ['wind_spd_avg','wind_dir_avg','wind_spd_max','air_temp_avg','air_pressure_avg',
          'surface_temp_avg','wave_ht_sig','wave_ht_max','wave_period_max','wave_dir_avg','wave_spread_avg','tide_ht_avg'],
         '2016-2026','~10min','point',1)

    _add('bbmp', f'{DATA_DIR}/bbmp_bedford_basin_2016_2024.csv',
         ['Chlorophyll_A','Ammonia','Nitrite','Nitrate','Phosphate','Silicate','Oxygen_CTD_mLL','Salinity_PSS','POC','PON','pH'],
         '2016-2024','biweekly','point',1)

    # Species
    _add('obis', f'{DATA_DIR}/obis_occurrences_full.pkl',
         ['scientificName','decimalLatitude','decimalLongitude','eventDate','depth','individualCount'],
         '1960s-present','event','point',1)

    # GFW
    _add('gfw', f'{DATA_DIR}/gfw_vessel_presence.json',
         ['hours','vessel_class','gear_type','lat','lon'],
         '2012-present','monthly','0.01°',2)

    # Governance
    _add('governance', f'{DATA_DIR}/governance/',
         ['mpa_boundary','fisheries','ecological_habitat','species_richness','functional_groups'],
         'current','static','polygon',2)

    # HYCOM
    for hy_file in glob.glob(f'{DATA_DIR}/hycom_*.nc'):
        label = os.path.basename(hy_file).replace('.nc','')
        ds = xr.open_dataset(hy_file)
        _add(label, hy_file, list(ds.data_vars.keys()), 'various', '3-hourly', '1/12°', 3)
        ds.close()

    # Open-Meteo
    _add('openmeteo_marine', f'{DATA_DIR}/marine_openmeteo_2016_2026.pkl',
         ['wave_height','wave_direction','wave_period','wave_peak_period','sea_surface_temperature',
          'ocean_current_velocity','ocean_current_direction','sea_level_height_msl'],
         '2016-2026','hourly','0.25°',4)

    # Save metadata
    os.makedirs(f'{DATA_DIR}/../cube', exist_ok=True)
    with open(f'{DATA_DIR}/../cube/cube_metadata.json','w') as f:
        json.dump(cube, f, indent=2, default=str)

    total_vars = sum(len(s['variables']) for s in cube['sources'].values())
    print(f"✓ Cube metadata: {len(cube['sources'])} sources, {total_vars} variables mapped")
    return cube

if __name__ == '__main__':
    build_cube_metadata()
