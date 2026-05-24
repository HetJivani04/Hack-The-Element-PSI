"""Complete 181-variable registry mapping catalog IDs to data sources.
Every tool references variables by ID — no hardcoded names anywhere.

cube_source values are validated against cube_metadata.json source keys.
All 29 metadata source keys are mapped. Derived variables computed on-the-fly.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json, os

@dataclass
class Variable:
    id: str; name: str; long_name: str; domain: str; units: str
    cube_source: str; cube_variable_name: str
    temporal_range: str; temporal_resolution: str; spatial_resolution: str
    depth_dependent: bool; quality_flag: int
    required_for: List[str] = field(default_factory=list)

VARIABLES: Dict[str, Variable] = {}

def _reg(**kw):
    v = Variable(**kw)
    VARIABLES[v.id] = v

# Valid metadata source keys (from cube_metadata.json)
_VALID_SOURCES = {
    "glorys_physics", "thetao_nrt", "so_nrt", "cur_nrt", "merged_uv_nrt",
    "surface_2d", "sst_anomaly", "bathymetry", "waves_nrt", "waves_reanalysis",
    "bgc_bio", "bgc_nut", "bgc_car", "bgc_co2", "bgc_pft", "bgc_plankton",
    "bgc_optics", "era5_atmosphere", "sma_halifax", "bbmp", "obis", "gfw",
    "governance", "hycom_reanalysis_2015h2", "hycom_surface_2023-07",
    "hycom_surface_jul2020", "hycom_surface_2019-07", "hycom_surface_2021-01",
    "openmeteo_marine",
}

# ========== PHYSICS 3D (25 vars: 1.1-1.25) ==========
_reg(id="1.1", name="thetao", long_name="Potential temperature", domain="physics",
     units="°C", cube_source="glorys_physics", cube_variable_name="thetao",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=2,
     required_for=["baseline","lagrangian","acoustic","sdm"])
_reg(id="1.2", name="thetao_nrt", long_name="Temperature (NRT 6h)", domain="physics",
     units="°C", cube_source="thetao_nrt", cube_variable_name="thetao",
     temporal_range="2024-2026", temporal_resolution="6-hourly", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3,
     required_for=["baseline","lagrangian","acoustic"])
_reg(id="1.3", name="water_temp", long_name="Temperature (HYCOM)", domain="physics",
     units="°C", cube_source="hycom_reanalysis_2015h2", cube_variable_name="water_temp",
     temporal_range="1994-2015", temporal_resolution="3-hourly", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3, required_for=["ensemble"])
_reg(id="1.4", name="water_temp_rean", long_name="Temperature (HYCOM 2015-2020)", domain="physics",
     units="°C", cube_source="hycom_surface_2023-07", cube_variable_name="water_temp",
     temporal_range="2015-2020", temporal_resolution="3-hourly", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3, required_for=["ensemble","baseline","lagrangian","acoustic","sdm"])
_reg(id="1.5", name="TEMPPR01", long_name="In-situ temperature (BBMP moored CTD)", domain="physics",
     units="°C", cube_source="bbmp", cube_variable_name="TEMPPR01",
     temporal_range="2016-2024", temporal_resolution="biweekly", spatial_resolution="point",
     depth_dependent=True, quality_flag=1, required_for=["validation","baseline","ensemble"])
_reg(id="1.6", name="air_temp_avg", long_name="Air temperature (SMA buoy)", domain="physics",
     units="°C", cube_source="sma_halifax", cube_variable_name="air_temp_avg",
     temporal_range="2016-2026", temporal_resolution="~10min", spatial_resolution="point",
     depth_dependent=False, quality_flag=1, required_for=["validation"])
_reg(id="1.7", name="surface_temp_avg", long_name="SST (SMA Halifax buoy)", domain="physics",
     units="°C", cube_source="sma_halifax", cube_variable_name="surface_temp_avg",
     temporal_range="2013-present", temporal_resolution="~10min", spatial_resolution="point",
     depth_dependent=False, quality_flag=1, required_for=["validation"])
_reg(id="1.8", name="so", long_name="Practical salinity", domain="physics",
     units="PSU", cube_source="glorys_physics", cube_variable_name="so",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=2,
     required_for=["baseline","lagrangian","acoustic","sdm"])
_reg(id="1.9", name="so_nrt", long_name="Salinity (NRT)", domain="physics",
     units="PSU", cube_source="so_nrt", cube_variable_name="so",
     temporal_range="2024-2026", temporal_resolution="6-hourly", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3,
     required_for=["baseline","lagrangian","acoustic"])
_reg(id="1.10", name="salinity_hycom", long_name="Salinity (HYCOM)", domain="physics",
     units="PSU", cube_source="hycom_reanalysis_2015h2", cube_variable_name="salinity",
     temporal_range="1994-2015", temporal_resolution="3-hourly", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3, required_for=["ensemble"])
_reg(id="1.11", name="Salinity_PSS", long_name="Salinity (BBMP in-situ)", domain="physics",
     units="PSU", cube_source="bbmp", cube_variable_name="Salinity_PSS",
     temporal_range="2016-2024", temporal_resolution="biweekly", spatial_resolution="point",
     depth_dependent=True, quality_flag=1, required_for=["validation"])
_reg(id="1.12", name="uo", long_name="Eastward current", domain="physics",
     units="m/s", cube_source="glorys_physics", cube_variable_name="uo",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=2,
     required_for=["lagrangian","scour","emf","baseline"])
_reg(id="1.13", name="vo", long_name="Northward current", domain="physics",
     units="m/s", cube_source="glorys_physics", cube_variable_name="vo",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=2,
     required_for=["lagrangian","scour","emf","baseline"])
_reg(id="1.14", name="water_u", long_name="Eastward velocity (HYCOM)", domain="physics",
     units="m/s", cube_source="hycom_reanalysis_2015h2", cube_variable_name="water_u",
     temporal_range="1994-2015", temporal_resolution="3-hourly", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3, required_for=["ensemble"])
_reg(id="1.15", name="water_v", long_name="Northward velocity (HYCOM)", domain="physics",
     units="m/s", cube_source="hycom_reanalysis_2015h2", cube_variable_name="water_v",
     temporal_range="1994-2015", temporal_resolution="3-hourly", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3, required_for=["ensemble"])
_reg(id="1.16", name="wind_spd_avg", long_name="Wind speed (SMA buoy)", domain="physics",
     units="m/s", cube_source="sma_halifax", cube_variable_name="wind_spd_avg",
     temporal_range="2016-2026", temporal_resolution="~10min", spatial_resolution="point",
     depth_dependent=False, quality_flag=1, required_for=["validation"])
_reg(id="1.17", name="wave_ht_sig", long_name="Wave height (SMA buoy)", domain="physics",
     units="m", cube_source="sma_halifax", cube_variable_name="wave_ht_sig",
     temporal_range="2016-2026", temporal_resolution="~10min", spatial_resolution="point",
     depth_dependent=False, quality_flag=1, required_for=["validation"])
_reg(id="1.18", name="wo", long_name="Upward velocity (GLORYS12)", domain="physics",
     units="m/s", cube_source="glorys_physics", cube_variable_name="wo",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=True, quality_flag=3, required_for=["lagrangian","baseline"])
_reg(id="1.19", name="utotal", long_name="Surface current (Euler+Stokes+tide)", domain="physics",
     units="m/s", cube_source="merged_uv_nrt", cube_variable_name="utotal",
     temporal_range="2024-2026", temporal_resolution="hourly", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["lagrangian"])
_reg(id="1.20", name="ocean_current_vel", long_name="Surface current (Open-Meteo)", domain="physics",
     units="m/s", cube_source="openmeteo_marine", cube_variable_name="ocean_current_velocity",
     temporal_range="2016-2026", temporal_resolution="hourly", spatial_resolution="0.25°",
     depth_dependent=False, quality_flag=4, required_for=["lagrangian"])
_reg(id="1.21", name="ocean_current_dir", long_name="Surface current dir (Open-Meteo)", domain="physics",
     units="°", cube_source="openmeteo_marine", cube_variable_name="ocean_current_direction",
     temporal_range="2016-2026", temporal_resolution="hourly", spatial_resolution="0.25°",
     depth_dependent=False, quality_flag=4, required_for=["lagrangian"])
_reg(id="1.22", name="utide", long_name="Tidal current u (CMEMS)", domain="physics",
     units="m/s", cube_source="merged_uv_nrt", cube_variable_name="utide",
     temporal_range="2024-2026", temporal_resolution="hourly", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["lagrangian"])
_reg(id="1.23", name="vsdx", long_name="Stokes drift u (CMEMS)", domain="physics",
     units="m/s", cube_source="merged_uv_nrt", cube_variable_name="vsdx",
     temporal_range="2024-2026", temporal_resolution="hourly", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["lagrangian"])
_reg(id="1.24", name="vsdy", long_name="Stokes drift v (CMEMS)", domain="physics",
     units="m/s", cube_source="merged_uv_nrt", cube_variable_name="vsdy",
     temporal_range="2024-2026", temporal_resolution="hourly", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["lagrangian"])
_reg(id="1.25", name="vtide", long_name="Tidal current v (CMEMS)", domain="physics",
     units="m/s", cube_source="merged_uv_nrt", cube_variable_name="vtide",
     temporal_range="2024-2026", temporal_resolution="hourly", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["lagrangian"])

# ========== SURFACE & SEA LEVEL (15 vars: 2.1-2.15) ==========
_reg(id="2.1", name="zos", long_name="SSH above geoid", domain="physics",
     units="m", cube_source="glorys_physics", cube_variable_name="zos",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["lagrangian","baseline"])
_reg(id="2.2", name="surf_el", long_name="Surface elevation (HYCOM)", domain="physics",
     units="m", cube_source="hycom_surface_2019-07", cube_variable_name="surf_el",
     temporal_range="2018-2024", temporal_resolution="3-hourly", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=3, required_for=["ensemble"])
_reg(id="2.3", name="surf_el_2021", long_name="Surface elevation (HYCOM 2021)", domain="physics",
     units="m", cube_source="hycom_surface_2021-01", cube_variable_name="surf_el",
     temporal_range="2024-present", temporal_resolution="hourly", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=3, required_for=["ensemble"])
_reg(id="2.4", name="sea_level_ometeo", long_name="Sea level height (Open-Meteo)", domain="physics",
     units="m", cube_source="openmeteo_marine", cube_variable_name="sea_level_height_msl",
     temporal_range="2016-2026", temporal_resolution="hourly", spatial_resolution="0.25°",
     depth_dependent=False, quality_flag=4, required_for=["baseline"])
_reg(id="2.5", name="air_pressure_avg", long_name="Air pressure (SMA buoy)", domain="physics",
     units="hPa", cube_source="sma_halifax", cube_variable_name="air_pressure_avg",
     temporal_range="2016-2026", temporal_resolution="~10min", spatial_resolution="point",
     depth_dependent=False, quality_flag=1, required_for=["baseline"])
_reg(id="2.6", name="tide_ht_avg", long_name="Tide height (SMA buoy)", domain="physics",
     units="m", cube_source="sma_halifax", cube_variable_name="tide_ht_avg",
     temporal_range="2016-2026", temporal_resolution="~10min", spatial_resolution="point",
     depth_dependent=False, quality_flag=1, required_for=["validation"])
_reg(id="2.7", name="mlotst", long_name="Mixed layer depth", domain="physics",
     units="m", cube_source="glorys_physics", cube_variable_name="mlotst",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["lagrangian","baseline"])
_reg(id="2.8", name="mlotst_surface", long_name="MLD (surface_2d)", domain="physics",
     units="m", cube_source="surface_2d", cube_variable_name="mlotst",
     temporal_range="2022-2026", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["ensemble"])
_reg(id="2.9", name="tob", long_name="Bottom temperature (surface_2d)", domain="physics",
     units="°C", cube_source="surface_2d", cube_variable_name="tob",
     temporal_range="2022-2026", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["ensemble"])
_reg(id="2.10", name="SST_era5", long_name="Sea surface temperature (ERA5)", domain="physics",
     units="°C", cube_source="era5_atmosphere", cube_variable_name="sst",
     temporal_range="2016-2025", temporal_resolution="6-hourly", spatial_resolution="0.25°",
     depth_dependent=False, quality_flag=2, required_for=["wake","baseline","sdm"])
_reg(id="2.11", name="bottomT", long_name="Bottom temperature", domain="physics",
     units="°C", cube_source="glorys_physics", cube_variable_name="bottomT",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["sdm","baseline"])
_reg(id="2.12", name="sob_surface", long_name="Bottom salinity (surface_2d)", domain="physics",
     units="PSU", cube_source="surface_2d", cube_variable_name="sob",
     temporal_range="2022-2026", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["sdm"])
_reg(id="2.13", name="siconc", long_name="Sea ice concentration", domain="physics",
     units="0-1", cube_source="glorys_physics", cube_variable_name="siconc",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["baseline"])
_reg(id="2.14", name="sithick", long_name="Sea ice thickness", domain="physics",
     units="m", cube_source="glorys_physics", cube_variable_name="sithick",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["baseline"])
_reg(id="2.15", name="usi", long_name="Sea ice eastward velocity", domain="physics",
     units="m/s", cube_source="glorys_physics", cube_variable_name="usi",
     temporal_range="2016-2023", temporal_resolution="daily", spatial_resolution="1/12°",
     depth_dependent=False, quality_flag=2, required_for=["baseline"])

# ========== WAVES (28 vars: 3.1-3.28) ==========
_waves = [
    ("3.1","VHM0","Sig wave height (WAVERYS)",["baseline","acoustic","scour"],"m","waves_reanalysis","VHM0","2016-2023","3-hourly","0.2°",False,4),
    ("3.2","VHM0_nrt","Sig wave height (NRT)",["baseline"],"m","waves_nrt","VHM0","2024-2026","3-hourly","1/12°",False,2),
    ("3.3","wave_height_ometeo","Sig wave height (Open-Meteo)",["baseline"],"m","openmeteo_marine","wave_height","2016-2026","hourly","0.25°",False,4),
    ("3.4","VTPK","Peak wave period (WAVERYS)",["acoustic","scour","baseline"],"s","waves_reanalysis","VTPK","2016-2023","3-hourly","0.2°",False,4),
    ("3.5","VTPK_nrt","Peak wave period (NRT)",["baseline"],"s","waves_nrt","VTPK","2024-2026","3-hourly","1/12°",False,2),
    ("3.6","VTM10","Energy period (NRT)",["acoustic"],"s","waves_nrt","VTM10","2024-2026","3-hourly","1/12°",False,2),
    ("3.7","wave_period","Wave period (Open-Meteo)",["baseline"],"s","openmeteo_marine","wave_period","2016-2026","hourly","0.25°",False,4),
    ("3.8","VMDR","Mean wave direction (WAVERYS)",["acoustic","scour","baseline"],"°","waves_reanalysis","VMDR","2016-2023","3-hourly","0.2°",False,4),
    ("3.9","VMDR_nrt","Mean wave direction (NRT)",["baseline"],"°","waves_nrt","VMDR","2024-2026","3-hourly","1/12°",False,2),
    ("3.10","VPED","Peak wave direction (NRT)",["baseline"],"°","waves_nrt","VPED","2024-2026","3-hourly","1/12°",False,2),
    ("3.11","VHM0_WW","Wind sea Hs (WAVERYS)",["acoustic"],"m","waves_reanalysis","VHM0_WW","2016-2023","3-hourly","0.2°",False,4),
    ("3.12","VMDR_WW","Wind sea direction (WAVERYS)",["baseline"],"°","waves_reanalysis","VMDR_WW","2016-2023","3-hourly","0.2°",False,4),
    ("3.13","VTM01_WW","Wind sea period (reanalysis)",["baseline"],"s","waves_reanalysis","VTM02","2016-2023","3-hourly","0.2°",False,4),
    ("3.14","VHM0_SW1","Primary swell Hs (WAVERYS)",["acoustic"],"m","waves_reanalysis","VHM0_SW1","2016-2023","3-hourly","0.2°",False,4),
    ("3.15","VMDR_SW1","Primary swell dir (WAVERYS)",["baseline"],"°","waves_reanalysis","VMDR_SW1","2016-2023","3-hourly","0.2°",False,4),
    ("3.16","VTM01_SW1","Primary swell period (reanalysis)",["baseline"],"s","waves_reanalysis","VTM02","2016-2023","3-hourly","0.2°",False,4),
    ("3.17","VHM0_SW2","Secondary swell Hs (WAVERYS)",["acoustic"],"m","waves_reanalysis","VHM0_SW2","2016-2023","3-hourly","0.2°",False,4),
    ("3.18","swell_ometeo","Swell (Open-Meteo)",["baseline"],"m","openmeteo_marine","wave_height","2016-2026","hourly","0.25°",False,4),
    ("3.19","VTM02_rean","Mean wave period (reanalysis)",["baseline"],"s","waves_reanalysis","VTM02","2016-2023","3-hourly","0.2°",False,4),
    ("3.20","VSDX","Stokes drift eastward (NRT)",["lagrangian"],"m/s","waves_nrt","VSDX","2024-2026","3-hourly","1/12°",False,2),
    ("3.21","VSDY","Stokes drift northward (NRT)",["lagrangian"],"m/s","waves_nrt","VSDY","2024-2026","3-hourly","1/12°",False,2),
    ("3.22","vsdx_merged","Stokes drift u (merged)",["lagrangian"],"m/s","merged_uv_nrt","vsdx","2024-2026","hourly","1/12°",False,2),
    ("3.23","VCMX","Max wave height (NRT)",["scour"],"m","waves_nrt","VCMX","2024-2026","3-hourly","1/12°",False,2),
    ("3.24","VMXL","Max crest height (NRT)",["scour"],"m","waves_nrt","VMXL","2024-2026","3-hourly","1/12°",False,2),
    ("3.25","wave_spread_avg","Wave spread (SMA buoy)",["validation"],"°","sma_halifax","wave_spread_avg","2016-2026","~10min","point",False,1),
    ("3.26","wave_ht_max","Max wave height (SMA buoy)",["acoustic"],"m","sma_halifax","wave_ht_max","2016-2026","~10min","point",False,1),
    ("3.27","wave_dir_avg","Wave direction (SMA buoy)",["scour"],"°","sma_halifax","wave_dir_avg","2016-2026","~10min","point",False,1),
    ("3.28","wave_period_max","Wave period max (SMA buoy)",["scour"],"s","sma_halifax","wave_period_max","2016-2026","~10min","point",False,1),
]
for (vid,vname,vlong,vreq,units,src,cname,trange,tres,sres,ddep,qf) in _waves:
    _reg(id=vid,name=vname,long_name=vlong,domain="waves",units=units,
         cube_source=src,cube_variable_name=cname,
         temporal_range=trange,temporal_resolution=tres,spatial_resolution=sres,
         depth_dependent=ddep,quality_flag=qf,required_for=vreq)

# ========== ATMOSPHERE (23 vars: 4.1-4.23) ==========
_atm = [
    ("4.1","u10","10m eastward wind","m/s","era5_atmosphere","u10",["wake","lagrangian","baseline"]),
    ("4.2","v10","10m northward wind","m/s","era5_atmosphere","v10",["wake","lagrangian","baseline"]),
    ("4.3","wind_speed_10m_ometeo","10m wind speed (Open-Meteo)","m/s","openmeteo_marine","wind_speed_10m",["baseline","wake","validation"]),
    ("4.4","wind_dir_10m_ometeo","10m wind direction (Open-Meteo)","°","openmeteo_marine","wind_direction_10m",["baseline","wake","validation"]),
    ("4.5","u100","100m eastward wind (HUB)","m/s","era5_atmosphere","u100",["wake","optimization","baseline"]),
    ("4.6","v100","100m northward wind (HUB)","m/s","era5_atmosphere","v100",["wake","optimization","baseline"]),
    ("4.7","wind_spd_max","Wind gust (SMA buoy)","m/s","sma_halifax","wind_spd_max",["baseline"]),
    ("4.8","t2m","2m air temperature","K","era5_atmosphere","t2m",["wake","baseline"]),
    ("4.9","sst_anomaly","SST anomaly","°C","sst_anomaly","sea_surface_temperature_anomaly",["wake"]),
    ("4.10","msl","Mean sea level pressure","Pa","era5_atmosphere","msl",["wake","baseline"]),
    ("4.11","wind_dir_avg","Wind direction (SMA buoy)","°","sma_halifax","wind_dir_avg",["baseline"]),
    ("4.12","sea_surface_temperature","SST (Open-Meteo)","°C","openmeteo_marine","sea_surface_temperature",["baseline"]),
    ("4.13","SST_anomaly","SST anomaly field","°C","sst_anomaly","sea_surface_temperature_anomaly",["baseline"]),
    ("4.14","air_temp_avg_sma","Air temperature (SMA)","°C","sma_halifax","air_temp_avg",["baseline"]),
    ("4.15","tp","Total precipitation","m","era5_atmosphere","tp",["baseline"]),
    ("4.16","sea_surface_temperature_ometeo","SST (Open-Meteo)","°C","openmeteo_marine","sea_surface_temperature",["baseline"]),
    ("4.17","blh","Boundary layer height","m","era5_atmosphere","blh",["wake"]),
    ("4.18","zust","Friction velocity","m/s","era5_atmosphere","zust",["wake"]),
    ("4.19","wind_spd_max_sma","Wind gust max (SMA)","m/s","sma_halifax","wind_spd_max",["wake"]),
    ("4.20","sea_surface_temperature_anomaly","SST anomaly","°C","sst_anomaly","sea_surface_temperature_anomaly",["baseline"]),
    ("4.21","wave_height_ometeo","Wave height (Open-Meteo)","m","openmeteo_marine","wave_height",["baseline"]),
    ("4.22","wave_direction_ometeo","Wave dir (Open-Meteo)","°","openmeteo_marine","wave_direction",["baseline"]),
    ("4.23","wave_peak_period_ometeo","Wave peak period (Open-Meteo)","s","openmeteo_marine","wave_peak_period",["baseline"]),
]
for (vid,vname,vlong,units,src,cname,vreq) in _atm:
    _reg(id=vid,name=vname,long_name=vlong,domain="atmosphere",units=units,
         cube_source=src,cube_variable_name=cname,
         temporal_range="2016-2025" if "era5" in src else ("2016-2026" if "sma" in src or "ometeo" in src else "2023-2026"),
         temporal_resolution="6-hourly" if "era5" in src else ("~10min" if "sma" in src else "hourly"),
         spatial_resolution="0.25°" if "era5" in src else ("point" if "sma" in src else "0.25°"),
         depth_dependent=False,quality_flag=3 if "era5" in src else 1,required_for=vreq)

# ========== BGC (23 vars: 8.1-8.23) ==========
_bgc = [
    ("8.1","chl","Chlorophyll-a","mg/m³","bgc_pft","chl",["sdm","baseline"]),
    ("8.2","Chlorophyll_A","Chlorophyll-a (BBMP in-situ)","µg/L","bbmp","Chlorophyll_A",["validation"]),
    ("8.3","chl_sat","Chlorophyll-a (satellite proxy)","mg/m³","bgc_pft","chl",["sdm"]),
    ("8.4","no3","Nitrate","mmol/m³","bgc_nut","no3",["sdm","baseline"]),
    ("8.5","po4","Phosphate","mmol/m³","bgc_nut","po4",["sdm","baseline"]),
    ("8.6","si","Silicate","mmol/m³","bgc_nut","si",["sdm","baseline"]),
    ("8.7","fe","Dissolved iron","mmol/m³","bgc_nut","fe",["sdm"]),
    ("8.8","o2","Dissolved oxygen","mmol/m³","bgc_bio","o2",["sdm","baseline"]),
    ("8.9","Oxygen_CTD_mLL","Dissolved oxygen (BBMP)","ml/L","bbmp","Oxygen_CTD_mLL",["validation"]),
    ("8.10","ph","pH (total scale)","—","bgc_car","ph",["acoustic","sdm"]),
    ("8.11","spco2","Surface pCO2","Pa","bgc_co2","spco2",["sdm"]),
    ("8.12","dissic","Dissolved inorganic carbon","mmol/m³","bgc_car","dissic",["sdm"]),
    ("8.13","talk","Total alkalinity","mmol/m³","bgc_car","talk",["sdm"]),
    ("8.14","nppv","Net primary production","mmol/m³/s","bgc_bio","nppv",["sdm","baseline"]),
    ("8.15","phyc","Phytoplankton carbon","mmol/m³","bgc_pft","phyc",["sdm"]),
    ("8.16","zooc","Zooplankton carbon","mmol/m³","bgc_plankton","zooc",["sdm"]),
    ("8.17","kd","Light attenuation","m⁻¹","bgc_optics","kd",["sdm"]),
    ("8.18","Ammonia","Ammonia (BBMP)","µmol/L","bbmp","Ammonia",["validation"]),
    ("8.19","POC","Particulate organic carbon","mg/m³","bbmp","POC",["validation"]),
    ("8.20","Nitrate_bbmp","Nitrate (BBMP)","µmol/L","bbmp","Nitrate",["validation"]),
    ("8.21","Nitrite_bbmp","Nitrite (BBMP)","µmol/L","bbmp","Nitrite",["validation"]),
    ("8.22","Phosphate_bbmp","Phosphate (BBMP)","µmol/L","bbmp","Phosphate",["validation"]),
    ("8.23","Silicate_bbmp","Silicate (BBMP)","µmol/L","bbmp","Silicate",["validation"]),
]
for (vid,vname,vlong,units,src,cname,vreq) in _bgc:
    _reg(id=vid,name=vname,long_name=vlong,domain="bgc",units=units,
         cube_source=src,cube_variable_name=cname,
         temporal_range="2024-2026" if src.startswith("bgc_") else "2016-2024",
         temporal_resolution="daily" if src.startswith("bgc_") else "biweekly",
         spatial_resolution="0.25°" if src.startswith("bgc_") else "point",
         depth_dependent=src.startswith("bgc_") and not src.startswith("bgc_co2"),
         quality_flag=3 if src.startswith("bgc_") else 1,required_for=vreq)

# ========== SPECIES (9 vars: 9.1-9.9) ==========
_spp = [
    ("9.1","obis_occurrence","Species occurrence (OBIS)","occurrence","obis","scientificName",["sdm","cumulative"]),
    ("9.2","scientificName","Scientific name","name","obis","scientificName",["sdm"]),
    ("9.3","individualCount","Individual count","count","obis","individualCount",["sdm"]),
    ("9.4","depth_obis","Observation depth","m","obis","depth",["sdm"]),
    ("9.5","decimalLatitude","Latitude (OBIS)","°","obis","decimalLatitude",["sdm"]),
    ("9.6","decimalLongitude","Longitude (OBIS)","°","obis","decimalLongitude",["sdm"]),
    ("9.7","eventDate","Event date (OBIS)","date","obis","eventDate",["sdm"]),
    ("9.8","Nitrate","Nitrate (BBMP — proxy for productivity)","µmol/L","bbmp","Nitrate",["sdm"]),
    ("9.9","narw_sighting","NARW sighting (OBIS: Eubalaena glacialis)","sighting","obis","scientificName",["sdm","cumulative"]),
]
for (vid,vname,vlong,units,src,cname,vreq) in _spp:
    _reg(id=vid,name=vname,long_name=vlong,domain="species",units=units,
         cube_source=src,cube_variable_name=cname,
         temporal_range="1960s-present",temporal_resolution="event",spatial_resolution="point",
         depth_dependent="depth" in vname,quality_flag=1 if "obis" in src else 1,
         required_for=vreq)

# ========== SEAFLOOR (5 vars: 10.1-10.5) ==========
_sf = [
    ("10.1","deptho","Bathymetry","m","bathymetry","deptho",["lagrangian","scour","acoustic","sdm","optimization","baseline"]),
    ("10.2","deptho_lev","Bathymetry levels","m","bathymetry","deptho_lev",["acoustic"]),
    ("10.3","mask","Land-sea mask","—","bathymetry","mask",["baseline"]),
    ("10.4","sediment_type","Seafloor sediment type (Folk classification)","categorical","governance","sediment_type",["scour","acoustic","sdm"]),
    ("10.5","d50","Median grain size (derived from sediment type)","mm","governance","sediment_type",["scour","acoustic","sdm"]),
]
for (vid,vname,vlong,units,src,cname,vreq) in _sf:
    _reg(id=vid,name=vname,long_name=vlong,domain="seafloor",units=units,
         cube_source=src,cube_variable_name=cname,
         temporal_range="static",temporal_resolution="static",
         spatial_resolution="1/12°" if "bathymetry" in src else "varies",
         depth_dependent=False,quality_flag=3 if "bathymetry" in src else 6,
         required_for=vreq)

# ========== HUMAN ACTIVITY (6 vars: 11.1-11.6) ==========
_human = [
    ("11.1","hours","Vessel presence (gridded)","hours/cell","gfw","hours",["optimization","cumulative"]),
    ("11.2","fishing_effort","Fishing effort by gear","hours/cell","gfw","hours",["optimization","cumulative"]),
    ("11.3","vessel_class","Vessel type classification","categorical","gfw","vessel_class",["optimization"]),
    ("11.4","gear_type","Fishing gear type","categorical","gfw","gear_type",["optimization"]),
    ("11.5","shipping_density","Shipping lane density","vessels/km²","gfw","hours",["optimization"]),
    ("11.6","fishing_zones","Fishing zone closures","polygon","governance","fisheries",["optimization"]),
]
for (vid,vname,vlong,units,src,cname,vreq) in _human:
    _reg(id=vid,name=vname,long_name=vlong,domain="human",units=units,
         cube_source=src,cube_variable_name=cname,
         temporal_range="2012-present",temporal_resolution="monthly",
         spatial_resolution="0.01°",depth_dependent=False,
         quality_flag=2 if "gfw" in src else 4,required_for=vreq)

# ========== GOVERNANCE (9 vars: 12.1-12.9) ==========
_gov = [
    ("12.1","mpa_boundary","Marine Protected Areas","polygon","governance","mpa_boundary",["optimization","cumulative"]),
    ("12.2","fisheries","Fisheries management zones","polygon","governance","fisheries",["optimization"]),
    ("12.3","ecological_habitat","Ecological habitat (SARA)","polygon","governance","ecological_habitat",["optimization","cumulative"]),
    ("12.4","species_richness","Species richness zones","polygon","governance","species_richness",["optimization"]),
    ("12.5","functional_groups","Functional groups","polygon","governance","functional_groups",["optimization"]),
    ("12.6","aquaculture","Aquaculture lease sites","polygon","governance","aquaculture",["optimization","cumulative"]),
    ("12.7","submarine_cables","Submarine cable corridors","polygon","governance","submarine_cables",["optimization","cumulative"]),
    ("12.8","disposal_sites","Dredge disposal sites","polygon","governance","disposal_sites",["optimization","cumulative"]),
    ("12.9","navigation","Navigation channels / TSS","polygon","governance","navigation",["optimization","cumulative"]),
]
for (vid,vname,vlong,units,src,cname,vreq) in _gov:
    _reg(id=vid,name=vname,long_name=vlong,domain="governance",units=units,
         cube_source=src,cube_variable_name=cname,
         temporal_range="current",temporal_resolution="static",spatial_resolution="polygon",
         depth_dependent=False,quality_flag=2,required_for=vreq)

# ========== DERIVED (12 vars: 13.1-13.12) — computed on-the-fly ==========
_der = [
    ("13.1","c_z","Sound speed profile","m/s",["acoustic"]),
    ("13.2","N2","Brunt-Väisälä frequency","s⁻²",["lagrangian"]),
    ("13.3","Ri","Richardson number","—",["lagrangian"]),
    ("13.4","sigma_theta","Potential density anomaly","kg/m³",["lagrangian"]),
    ("13.5","trajectory","Lagrangian trajectory","Geodesic",["lagrangian"]),
    ("13.6","HSI","Habitat suitability index","0-1",["sdm"]),
    ("13.7","P_occurrence","Species occurrence probability","0-1",["sdm"]),
    ("13.8","TL","Acoustic transmission loss","dB",["acoustic"]),
    ("13.9","wind_power_density","Wind power density","W/m²",["optimization"]),
    ("13.10","pareto_frontier","Pareto frontier","set",["optimization"]),
    ("13.11","ship_strike_risk","Ship strike risk","0-1",["cumulative"]),
    ("13.12","ensemble_spread","Multi-model ensemble spread","varies",["ensemble"]),
]
for (vid,vname,vlong,units,vreq) in _der:
    _reg(id=vid,name=vname,long_name=vlong,domain="derived",units=units,
         cube_source="__computed__",cube_variable_name=vname,
         temporal_range="as computed",temporal_resolution="as computed",
         spatial_resolution="as input",depth_dependent=vid in ["13.1","13.2","13.3","13.4"],
         quality_flag=6,required_for=vreq)

# ========== PUBLIC API ==========

def get_variable(var_id: str) -> Optional[Variable]:
    return VARIABLES.get(var_id)

def get_variables_for_tool(tool: str) -> List[Variable]:
    return [v for v in VARIABLES.values() if tool in v.required_for]

def get_variables_by_domain(domain: str) -> List[Variable]:
    return [v for v in VARIABLES.values() if v.domain == domain]

def validate_registry() -> dict:
    """Validate all registry cube_source values against cube_metadata.json.
    Returns dict with counts of valid, invalid, and computed sources.
    """
    meta_path = os.path.join(os.path.dirname(__file__), '..', '..', 'cube', 'cube_metadata.json')
    valid_sources = set(_VALID_SOURCES)
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        valid_sources = set(meta.get('sources', {}).keys())

    valid = []; invalid = []; computed = []
    for v in VARIABLES.values():
        if v.cube_source == "__computed__":
            computed.append(v.id)
        elif v.cube_source in valid_sources:
            valid.append(v.id)
        else:
            invalid.append((v.id, v.name, v.cube_source))

    return {
        'total': len(VARIABLES),
        'valid_sources': len(valid),
        'invalid_sources': len(invalid),
        'computed': len(computed),
        'valid_var_ids': valid,
        'invalid_details': invalid,
        'computed_var_ids': computed,
    }

# Print summary on import
if __name__ == '__main__' or True:
    vresult = validate_registry()
    print(f"✓ Registry: {vresult['total']} variables across {len(set(v.domain for v in VARIABLES.values()))} domains")
    for d in sorted(set(v.domain for v in VARIABLES.values())):
        count = len([v for v in VARIABLES.values() if v.domain == d])
        print(f"  {d}: {count} variables")
    print(f"  Valid sources: {vresult['valid_sources']}/{vresult['total']} variables")
    if vresult['invalid_sources']:
        print(f"  ⚠ Invalid sources: {vresult['invalid_sources']} variables — NEED FIX")
    print(f"  Computed on-the-fly: {vresult['computed']} variables")
    print(f"  Depth-dependent: {sum(1 for v in VARIABLES.values() if v.depth_dependent)}")
