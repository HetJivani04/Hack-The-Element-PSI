# Ocean Data APIs — Scotian Shelf Region

**Region of Interest (ROI):**
- Southwest: `43.675818°N, -64.328234°W`
- Northeast: `44.831526°N, -61.943675°W`
- Area: Scotian Shelf, Halifax approaches, Eastern Shore, Sable Island waters

**Last updated:** 2026-05-24 (verified with actual downloads)

---

## Download Results Summary (2026-05-23/24 Session)

**What worked — data successfully downloaded to `data/`:**

| Source | Status | Details |
|--------|--------|---------|
| Copernicus GLORYS12 (reanalysis) | ✅ Full success | 2016-2023, daily, 13×28 grid, 26 levels. thetao, so, uo, vo, zos, mlotst, ice — ALL variables in ONE dataset (`cmems_mod_glo_phy_my_0.083deg_P1D-m`) |
| Copernicus NRT 3D T/S/U/V | ✅ Full success | 2024-2026, 6-hourly, split datasets: `_phy-thetao_`, `_phy-so_`, `_phy-cur_` |
| Copernicus NRT Merged UV | ✅ Full success | 2024-2026, HOURLY surface Euler+Stokes+tide, 20,953 timesteps |
| Copernicus Surface 2D | ✅ Partial | 2022-2026 only (NRT starts 2022-06). GLORYS12 covers 2016-2023 surface too. |
| Copernicus SST Anomaly | ✅ Full success | 2023-2026, daily |
| Copernicus Global WAV | ✅ Full success | 2024-2026, 19 wave vars incl. Stokes drift, 3-hourly |
| Copernicus WAVERYS | ✅ Full success | 2016-2023, 8 core wave vars, 3-hourly. NOTE: coarser 0.2° grid. |
| Copernicus BGC | ✅ Full success | 2024-2026, 14 vars (chl, O2, nutrients, pH, DIC, Alk, pCO2, NPP, phyc, zooc, kd). 0.25° grid. |
| Copernicus Static Bathymetry | ✅ Full success | 1/12°, 50 levels, 8-266m depth |
| CDS ERA5 Atmosphere | ⏳ In progress | 5/10 years downloaded (2016-2020). Wind 10m+100m u/v, T2m, MSLP, SST, precip, BLH, u* |
| CDS ERA5 Waves | ⏳ In progress | 3/10 years downloaded (2016-2018). Hs, Tp, Dp, wind sea, swell, Stokes drift |
| HYCOM Reanalysis | ✅ Partial | 1994-2015 available, downloaded sample periods. THREDDS timeouts for full. |
| HYCOM GOFS 3.1 | ✅ Partial | 2018-2024 available, downloaded Jul-2020+surface samples. |
| CIOOS ERDDAP — SMA Halifax | ✅ Full success | 160k records 2016-2025. Wind, waves, SST, pressure. Also current profiles at 9 depth levels. |
| CIOOS ERDDAP — SMA Fairview | ✅ Full success | 49k records 2024. Wind station. |
| CIOOS ERDDAP — SMA Pier 9C | ✅ Full success | 46k records 2024. Tide + wind station. |
| CIOOS ERDDAP — BBMP | ✅ Full success | 3,296 records 2016-2024. Nutrients, chlorophyll, oxygen, HPLC pigments. |
| CIOOS ERDDAP — AZMP CTD | ✅ Full success | 1.13M records available. Downloaded 2020 sample (17.5k records). |
| OBIS Species | ✅ Full success | 50,000 records, 1,111 species. 501,900 total available in ROI. |
| GFW Vessel Presence | ✅ Full success | 1 entry with gridded data downloaded for 2023 ROI. |
| DFO Scotian Shelf MPA | ✅ Full success | 119 GeoJSON layers from EGISP ArcGIS REST. |
| Open-Meteo Marine | ✅ Full success | 91k hourly rows 2016-2026 at center point. 14 variables. |
| Open-Meteo Atmosphere | ✅ Partial | 92 days recent wind at 10m+100m. Archive API unreachable from this network. |

**What did NOT work or had issues:**

| Source | Issue | Resolution |
|--------|-------|------------|
| Copernicus v2 dataset IDs | v2 splits variables into separate datasets. Old combined IDs (`_PT6H-i`) are deprecated. | Use per-variable IDs: `_phy-thetao_`, `_phy-so_`, `_phy-cur_` |
| CDS API key | Old key was rejected (403). New key works. | User refreshed at https://cds.climate.copernicus.eu/ |
| CDS license | ERA5 license must be accepted on CDS website before API works. | Accepted at https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download |
| CDS cost limits | Full 10-year request too large ("cost limits exceeded"). | Split into yearly requests at 6-hourly resolution. |
| Open-Meteo Archive API | `archive-api.open-meteo.com` unreachable from this network (IP 5.9.98.184, no route to host). | Used CDS ERA5 for historical atmosphere. Open-Meteo forecast API works for recent data. |
| HYCOM THREDDS timeouts | Large subset requests timeout. | Use small time slices (<1 month), load into memory immediately. |
| DFO ArcGIS (`gisp.dfo-mpo.gc.ca`) | DNS resolution failed. | Used EGISP ArcGIS server instead (`egisp.dfo-mpo.gc.ca`) — works. |
| CIOOS ERDDAP variable names | Variable names differ from expected. `tide_ht_avg` not in SMA_halifax, `Temperature_CTD_1990` not in BBMP. | Query `.das` endpoint first to discover actual variable names before downloading. |
| CIOOS ERDDAP CSV format | CSV format has metadata line that needs to be skipped. JSON format avoids this issue. | Use `.json` endpoint when possible for cleaner data. |
| GEBCO direct download | Subsetting service 404. Global file 1.5 GB. | Used Copernicus 1/12° static bathymetry instead. Sufficient for shelf-scale modeling. |
| Argo floats in ROI | No Argo profiles in our shallow shelf bounding box (too shallow, <200m). | Not a gap — Argo requires deep water. Use AZMP CTD for in-situ profiles. |

---

## Auth Quick-Answer

| API | Auth Required? | Cost | How to Get |
|-----|---------------|------|------------|
| **Copernicus Marine** | **YES — mandatory** for all access (toolbox, OPeNDAP, everything) | **Free** | Register at https://data.marine.copernicus.eu/register |
| **HYCOM** | No | Free | Open OPeNDAP |
| **CIOOS Atlantic ERDDAP** | No | Free | Open REST |
| **CanWIN Buoy ERDDAP** | No | Free | Open REST |
| **Argo (argopy)** | No | Free | Open |
| **NOAA CO-OPS** | No | Free | Open REST |
| **ONC Oceans 3.0** | Yes (free token) | Free | https://data.oceannetworks.ca |
| **OBIS** | No | Free | Open REST |
| **GEBCO** | No | Free | Open download |
| **DFO MEDS/ISDM** | No (guest login) | Free | `GUEST/GUEST/GUEST` |
| **MSC GeoMet** | No | Free | Open REST |
| **AIS Stream** | Yes (free key) | Free tier | https://aisstream.io |
| **Open-Meteo Atmosphere** | No | Free | Open REST (archive + forecast) |
| **Open-Meteo Marine** | No | Free | Open REST (archive + forecast) |
| **Global Fishing Watch** | Yes (free API token) | Free | https://globalfishingwatch.org/apis |

**Copernicus is mandatory auth but totally free.** Without login, every `copernicusmarine` call raises `CredentialsCannotBeNone`.

> **Copernicus v2 dataset IDs (verified working as of 2026-05-23):**
> 
> **NRT (2020-present, 6-hourly 3D):**
> - `cmems_mod_glo_phy-thetao_anfc_0.083deg_PT6H-i` — temperature
> - `cmems_mod_glo_phy-so_anfc_0.083deg_PT6H-i` — salinity
> - `cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i` — currents (uo, vo)
> - `cmems_mod_glo_phy_anfc_0.083deg_P1D-m` — 2D surface (zos, mlotst, ice, tob, sob)
> - `cmems_mod_glo_phy_anfc_merged-uv_PT1H-i` — hourly surface (Euler+Stokes+tide)
> - `cmems_mod_glo_phy_anfc_0.083deg-sst-anomaly_P1D-m` — SST anomaly
> 
> **Reanalysis (1993-2023, daily):**
> - `cmems_mod_glo_phy_my_0.083deg_P1D-m` — ALL variables in ONE dataset (thetao, so, uo, vo, zos, mlotst, bottomT, ice) ← **preferred for historical**
> 
> **Waves:**
> - `cmems_mod_glo_wav_anfc_0.083deg_PT3H-i` — NRT waves 2022-present (19 vars)
> - `cmems_mod_glo_wav_my_0.2deg_PT3H-i` — WAVERYS reanalysis 1980-2023 (8 vars, 0.2°)
> 
> **BGC (2024-2026, daily, 0.25°):**
> - `cmems_mod_glo_bgc-bio_anfc_0.25deg_P1D-m` — NPP, O2
> - `cmems_mod_glo_bgc-nut_anfc_0.25deg_P1D-m` — NO3, PO4, Si, Fe
> - `cmems_mod_glo_bgc-car_anfc_0.25deg_P1D-m` — DIC, pH, Alkalinity
> - `cmems_mod_glo_bgc-co2_anfc_0.25deg_P1D-m` — surface pCO2
> - `cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m` — chlorophyll, phytoplankton carbon
> - `cmems_mod_glo_bgc-plankton_anfc_0.25deg_P1D-m` — zooplankton carbon
> - `cmems_mod_glo_bgc-optics_anfc_0.25deg_P1D-m` — light attenuation (kd)
> 
> **ERA5 Atmosphere via CDS (2016-2025, 6-hourly):**
> - Dataset: `reanalysis-era5-single-levels`
> - Variables: `10m_u_component_of_wind`, `10m_v_component_of_wind`, `100m_u_component_of_wind`, `100m_v_component_of_wind`, `2m_temperature`, `mean_sea_level_pressure`, `sea_surface_temperature`, `total_precipitation`, `boundary_layer_height`, `friction_velocity`
> - CDS API requires: licence acceptance on website + valid API key in `~/.cdsapirc`
> - Year-by-year download recommended (cost limits prevent full 10-year single request)
> - Files download as ZIP containing NetCDF. Instant and accumulated variables in separate files.
> 
> **ERA5 Waves via CDS (same dataset, different variables):**
> - Variables: `significant_height_of_combined_wind_waves_and_swell`, `mean_wave_direction`, `mean_wave_period`, `peak_wave_period`, wave and swell partitions, `u_component_stokes_drift`, `v_component_stokes_drift`

---

## Complete Variable Catalog by Scientific Domain

### PHYSICAL OCEANOGRAPHY

#### Temperature

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `thetao` (sea_water_potential_temperature) | °C | Copernicus Global PHY (analysis/forecast) | ~Nov 2020–present (+10d forecast) | 1/12° (~8 km), 50 levels |
| `thetao` | °C | Copernicus Global PHY Reanalysis (GLORYS12) | Jan 1993–Apr 2026 | 1/12° (~8 km), 50 levels |
| `water_temp` | °C | HYCOM ESPC-D-V02 | Aug 2024–present (+8d forecast) | 1/12° (~6×3 km at 45N), 41 hybrid layers |
| `water_temp` | °C | HYCOM GOFS 3.1 | Dec 2018–Sep 2024 | 1/12°, 41 layers |
| `water_temp` | °C | HYCOM GOFS 3.1 Reanalysis (GLBv0.08) | Jan 1994–Dec 2015 | 1/12°, 3-hourly |
| `TEMPPR01` / `TEMPP901` / `TEMPS901` | °C | CIOOS: AZMP/Ecosystem CTD rosette profiles | Sep 1996–Aug 2025 (ecosystem), Apr 1997–Apr 2026 (AZMP) | Point stations, ~1-2 m vertical in casts |
| `TEMPPR01` / `TEMPP901` | °C | CIOOS: AZMP Moored CTD | Sep 2000–Aug 2023 | Fixed moorings, continuous |
| `TEMPPR01` / `TEMPP901` / `POTM_01` | °C | CIOOS: Historical coastal/offshore moored | May 1967–May 2022 | Fixed moorings |
| `TEMPPR01` / `TEMPP901` | °C | CIOOS: OTN moored, Cetacean moored, RAPID moored | 2006–2023 | Fixed moorings |
| `Temperature_CTD_1968` / `Temp_CTD_1990` | °C | CIOOS: BBMP Bedford Basin bottle | Jan 1992–Dec 2024 | 44.69N, -63.64W (biweekly) |
| `surface_temp_avg` | °C | CIOOS: SMA Halifax (Herring Cove) buoy | Nov 2013–present | 44.5559N, -63.5445W, real-time |
| `TEMP` / `thetao` | °C | Copernicus In-Situ NRT (ISAS) | Jan 2015–present | 0.5°, 152 levels (0–2000 dbar) |
| `temp` / `temp_adjusted` | °C | Argo floats (argopy / GDAC) | ~2000–present (broader NW Atlantic) | Profiling floats, 0–2000m |
| `avg_sea_sfc_temp_pst10mts` | °C | ECCC MSC Buoys (CanWIN) | Varies by buoy | Buoy stations |

#### Salinity

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `so` (sea_water_salinity) | PSU (1e-3) | Copernicus Global PHY (analysis/forecast) | ~Nov 2020–present (+10d forecast) | 1/12°, 50 levels |
| `so` | PSU | Copernicus Global PHY Reanalysis (GLORYS12) | Jan 1993–Apr 2026 | 1/12°, 50 levels |
| `salinity` | PSU | HYCOM ESPC-D-V02 | Aug 2024–present (+8d) | 1/12°, 41 hybrid layers |
| `salinity` | PSU | HYCOM GOFS 3.1 / Reanalysis | 1994–Sep 2024 | 1/12°, 41 layers |
| `PSLTZZ01` / `PSALST01` / `PSLTZZ02` | 1e-3 (PSU) | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2026 | Point stations, ~1-2m vertical |
| `PSLTZZ01` | 1e-3 | CIOOS: All moored CTD datasets | 1967–2023 | Fixed moorings |
| `Salinity_CTD` / `Salinity_PSS` | PSS | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `PSAL` | PSS-78 | Copernicus In-Situ NRT (ISAS) | Jan 2015–present | 0.5°, 152 levels |
| `psal` / `psal_adjusted` | PSU | Argo floats | ~2000–present | Profiling floats |

#### Ocean Currents (Velocity)

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `uo` (eastward) / `vo` (northward) | m/s | Copernicus Global PHY (analysis/forecast) | ~Nov 2020–present | 1/12°, 50 levels |
| `uo` / `vo` (hourly surface) | m/s | Copernicus SMOC surface currents | ~Nov 2020–present | 1/12°, surface only, **hourly** |
| `utotal`/`vtotal` (Eulerian+Stokes+tide) | m/s | Copernicus SMOC surface currents | ~Nov 2020–present | 1/12°, surface, hourly |
| `utide`/`vtide` (tide-induced) | m/s | Copernicus SMOC | ~Nov 2020–present | 1/12°, surface, hourly |
| `vsdx`/`vsdy` (Stokes drift) | m/s | Copernicus SMOC (from wave model) | ~Nov 2020–present | 1/12°, surface, hourly |
| `water_u` / `water_v` | m/s | HYCOM ESPC-D-V02 / GOFS 3.1 / Reanalysis | 1994–present | 1/12°, 41 layers |
| `water_u_bottom` / `water_v_bottom` | m/s | HYCOM ESPC-D-V02 (bottom) | Aug 2024–present | 1/12°, bottom layer only |
| `u_barotropic_velocity` / `v_barotropic_velocity` | m/s | HYCOM (surface, 1-hourly) | Dec 2018–Sep 2024 | 1/12°, depth-averaged |
| `curr_spd1_avg` through `curr_spd20_avg` | mm/s | CIOOS: SMA Halifax Herring Cove buoy | Nov 2013–present | 20 depth levels at buoy |
| `curr_dir1_avg` through `curr_dir20_avg` | degree | CIOOS: SMA Halifax Herring Cove buoy | Nov 2013–present | 20 depth levels at buoy |
| `wo` (upward velocity) | m/s | Copernicus Global PHY (daily/monthly mean) | ~Nov 2020–present | 1/12°, 50 levels |

#### Sea Surface Height / Sea Level

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `zos` (sea_surface_height_above_geoid) | m | Copernicus Global PHY (analysis/forecast & reanalysis) | 1993–present | 1/12° |
| `surf_el` | m | HYCOM ESPC-D-V02 / GOFS 3.1 | 1994–present | 1/12° |
| `steric_ssh` | m | HYCOM ESPC-D-V02 (1-hourly) | Aug 2024–present | 1/12° |
| `tide_ht_avg` | m | CIOOS: SMA Halifax pier9c | Nov 2014–present | 44.6748N, -63.6097W |

#### Mixed Layer / Boundary Layer

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `mlotst` (ocean_mixed_layer_thickness_defined_by_sigma_theta) | m | Copernicus Global PHY | 1993–present | 1/12° |
| `mixed_layer_thickness` | m | HYCOM (1-hourly surface) | Dec 2018–Sep 2024 | 1/12° |
| `surface_boundary_layer_thickness` | m | HYCOM (1-hourly surface) | Dec 2018–Sep 2024 | 1/12° |

#### Density

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `SIGTEQ01` (sigma-theta) | kg/m³ | CIOOS: all moored CTD datasets | 1967–2024 | Fixed moorings |

#### Bottom Temperature/Salinity

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `bottomT` (sea_water_potential_temperature_at_sea_floor) | °C | Copernicus Global PHY | 1993–present | 1/12° |
| `sobot` (sea_water_potential_salinity_at_sea_floor) | 1e-3 | Copernicus Global PHY Reanalysis | 1993–2026 | 1/12° |
| `water_temp_bottom` | °C | HYCOM ESPC-D-V02 (bottom) | Aug 2024–present | 1/12° |
| `salinity_bottom` | PSU | HYCOM ESPC-D-V02 (bottom) | Aug 2024–present | 1/12° |

#### Bathymetry

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `bathymetry` (sea_floor_depth_below_geoid) | m | Copernicus Global PHY (static) | Static | 1/12° (~8 km) |
| `elevation` | m | GEBCO 2026 | One-time grid | 15 arc-sec (~450 m) |

---

### WAVES

#### Global Wave Model (Copernicus + HYCOM Surface Flux)

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `VHM0` (significant wave height, Hm0) | m | Copernicus Global WAV | Nov 2022–present (+10d forecast) | 0.083° (~8 km), 3-hourly |
| `VTPK` (peak wave period, Tp) | s | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VTM10` (energy period, Tm-10) | s | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VTM02` (mean period, Tm02) | s | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VMDR` (mean wave direction) | degree | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VPED` (peak wave direction) | degree | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VCMX` (maximum crest-trough height) | m | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VMXL` (maximum crest height) | m | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VSDX` / `VSDY` (Stokes drift) | m/s | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VHM0_WW` (wind sea significant height) | m | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VTM01_WW` (wind sea mean period) | s | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VMDR_WW` (wind sea direction) | degree | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VHM0_SW1` (primary swell significant height) | m | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VTM01_SW1` (primary swell mean period) | s | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VMDR_SW1` (primary swell direction) | degree | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VHM0_SW2` (secondary swell significant height) | m | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VTM01_SW2` (secondary swell mean period) | s | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |
| `VMDR_SW2` (secondary swell direction) | degree | Copernicus Global WAV | Nov 2022–present | 0.083°, 3-hourly |

**Wave Reanalysis:**
| All above wave variables | Same units | Copernicus Global WAV Reanalysis (WAVERYS) | Jan 1980–present | 0.2° (~22 km), 3-hourly + monthly |
| `surfx` / `surfy` (surface wind stress) | N/m² | HYCOM (ice files, 3-hourly) | 1994–present | 1/12° |
| `qtot` (net surface heat flux) | W/m² | HYCOM (surface, 1-hourly) | Dec 2018–Sep 2024 | 1/12° |
| `emp` (evaporation minus precipitation) | m/s | HYCOM (surface, 1-hourly) | Dec 2018–Sep 2024 | 1/12° |

#### Buoy-Measured Waves — Scotian Shelf proximity

| Variable Name(s) | Units | Source(s) | Temporal Span | Notes |
|---|---|---|---|---|
| `wave_ht_sig` (significant wave height) | m | CIOOS: SMA Halifax Herring Cove buoy | Nov 2013–present | **INSIDE ROI** (44.56N, -63.54W) |
| `wave_ht_max` (maximum wave height) | m | CIOOS: SMA Halifax buoy | Nov 2013–present | Inside ROI |
| `wave_period_max` | s | CIOOS: SMA Halifax buoy | Nov 2013–present | Inside ROI |
| `wave_dir_avg` | degree | CIOOS: SMA Halifax buoy | Nov 2013–present | Inside ROI |
| `wave_spread_avg` | degree | CIOOS: SMA Halifax buoy | Nov 2013–present | Inside ROI |
| `VCAR` (characteristic significant wave height) | m | CanWIN: DFO MEDS buoys | varies | Region's offshore buoys (44137, 44150) — NOT in ROI box but nearby |
| `VWH` (buoy-reported wave height) | m | CanWIN: DFO MEDS buoys | varies | Offshore buoys |
| `VCMX` (max zero-crossing wave height) | m | CanWIN: DFO MEDS buoys | varies | Offshore buoys |
| `VTP` / `VTPK` (wave spectrum peak period) | s | CanWIN: DFO MEDS buoys | varies | Offshore buoys |
| `sig_wave_hgt_pst20mts` (20-min sig. wave height) | m | CanWIN: ECCC MSC buoys | varies | Offshore buoys |
| `pk_wave_hgt_pst20mts` | m | CanWIN: ECCC MSC buoys | varies | Offshore buoys |
| `avg_wave_dir_pst20mts` | degree | CanWIN: ECCC MSC buoys | varies | Offshore buoys |
| `spetrl_wave_enrgy_pd_pst20mts` (spectral energy period) | s | CanWIN: ECCC MSC buoys | varies | Offshore buoys |

---

### SEA ICE

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `siconc` (sea_ice_area_fraction) | 0–1 | Copernicus Global PHY | 1993–present | 1/12° |
| `sithick` (sea_ice_thickness) | m | Copernicus Global PHY | 1993–present | 1/12° |
| `usi` / `vsi` (ice velocity) | m/s | Copernicus Global PHY | 1993–present | 1/12° |
| `sivelo` (sea_ice_speed) | m/s | Copernicus Global PHY | Nov 2022–present | 1/12° |
| `ist` (sea_ice_surface_temperature) | K | Copernicus Global PHY | Nov 2022–present | 1/12° |
| `sialb` (sea_ice_albedo) | — | Copernicus Global PHY | Nov 2022–present | 1/12° |
| `sisnthick` (surface_snow_thickness) | m | Copernicus Global PHY | Nov 2022–present | 1/12° |
| `siage` (age_of_sea_ice) | days | Copernicus Global PHY | Nov 2022–present | 1/12° |
| `sic` (sea ice concentration) | 0–1 | HYCOM | 1994–present | 1/12° |
| `sih` (sea ice thickness) | m | HYCOM | 1994–present | 1/12° |
| `siu` / `siv` (sea ice velocity) | m/s | HYCOM | 1994–present | 1/12° |

Note: Scotian Shelf is mostly ice-free except occasional sea ice in late winter in northern/nearshore areas.

---

### BIOGEOCHEMISTRY — WATER COLUMN

#### Global Biogeochemistry Model (Copernicus)

| Variable Name(s) | Units | Source(s) | Temporal Span | Spatial Resolution |
|---|---|---|---|---|
| `chl` (chlorophyll-a mass concentration) | mg/m³ | Copernicus Global BGC (analysis/forecast) | ~Oct 2021–present (+10d forecast) | 0.25° (~27 km), 50 levels |
| `chl` | mg/m³ | Copernicus Global BGC Reanalysis (BIORYS) | Jan 1993–Mar 2026 | 0.25°, 75 levels |
| `no3` (nitrate) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `po4` (phosphate) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `o2` (dissolved oxygen) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `si` (silicate) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `fe` (dissolved iron) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `phyc` (phytoplankton as carbon) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `nppv` (net primary production) | mmol/m³/s | Copernicus Global BGC | 1993–present | 0.25° |
| `dissic` (dissolved inorganic carbon) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `talk` (alkalinity) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25° |
| `ph` (pH total scale) | — | Copernicus Global BGC | 1993–present | 0.25° |
| `spco2` (surface pCO2) | Pa | Copernicus Global BGC | 1993–present | 0.25° |
| `ze` (light attenuation) | m⁻¹ | Copernicus Global BGC | 1993–present | 0.25° |
| `zoo` (zooplankton — monthly only) | mmol/m³ | Copernicus Global BGC | 1993–present | 0.25°, monthly |

#### In-Situ Biogeochemistry — DFO Bedford Basin / Scotian Shelf

| Variable Name(s) | Units | Source(s) | Temporal Span | Location |
|---|---|---|---|---|
| `DOXYZZ01` / `DOXYZZ02` (dissolved oxygen by sensor) | ml/L | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `Oxygen_CTD_mLL` | ml/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `Oxygen_Winkler_Auto` | ml/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `CPHLPR01` / `CPHLPR02` (chlorophyll-a by fluorometer) | mg/m³ | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `Chlorophyll_A` (fluorometric) | mg/m³ | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `CHL_SENSOR_insitu` | µg/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `Phaeophytin` | mg/m³ | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `PHXXZZ01` (pH total scale) | — | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `pH` | — | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `Ammonia` | µmol/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `Nitrite` | µmol/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `Nitrate` | µmol/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `Phosphate` | µmol/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `Silicate` | µmol/L | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `POC` (particulate organic carbon) | mg/m³ | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `PON` (particulate organic nitrogen) | mg/m³ | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |
| `CDOMZZ01` / `CDOMZZ02` (coloured dissolved organic matter) | mg/m³ | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `TURBNTU01` (turbidity) | NTU | CIOOS: AZMP CTD profiles | 1997–2026 | Scotian Shelf stations |

#### HPLC Phytoplankton Pigments — BBMP Bedford Basin (18 variables)

| Variable (all from BBMP) | Source | Temporal Span |
|---|---|---|
| `HPLC_alpha_Carotene`, `HPLC_alloxanthin`, `HPLC_astaxanthin`, `HPLC_beta-carotene`, `HPLC_19-butanoyloxyfucoxanthin`, `HPLC_chlorophyll-a`, `HPLC_chlorophyll-b`, `HPLC_chlorophyll-c1`, `HPLC_chlorophyll-c2`, `HPLC_chlorophyll-c3`, `HPLC_chlorophyllide`, `HPLC_diadinoxanthin`, `HPLC_diatoxanthin`, `HPLC_fucoxanthin`, `HPLC_19-hexanoyloxyfucoxanthin`, `HPLC_HEXLIKE`, `HPLC_peridinin`, `HPLC_phaeophorbide+phaeophytin`, `HPLC_prasinoxanthin`, `HPLC_pyrophaeophorbide`, `HPLC_violaxanthin`, `HPLC_zeaxanthin` | CIOOS: BBMP | 1992–2024, 44.69N, -63.64W |

---

### OPTICAL PROPERTIES

| Variable Name(s) | Units | Source(s) | Temporal Span | Location |
|---|---|---|---|---|
| `IRRDSV01` (surface PAR) | µEinsteins/s/m² | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `IRRDUV01` (downwelling PAR) | µEinsteins/s/m² | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `VSCTXX01` (volume scattering) | m⁻¹/sr | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `ATTNZS01` (beam attenuation) | 1/m | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `OPTCPS01` (transmittance) | % | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `CNDCST01` / `CNDCST02` (electrical conductivity) | S/m | CIOOS: AZMP/Ecosystem CTD profiles | 1996–2025 | Scotian Shelf stations |
| `conductivity_CTD` | S/m | CIOOS: BBMP Bedford Basin | 1992–2024 | 44.69N, -63.64W |

---

### ATMOSPHERIC / SURFACE METEOROLOGY

#### Inside the ROI — SMA Halifax Buoy Network

| Variable Name(s) | Units | Source(s) | Temporal Span | Location |
|---|---|---|---|---|
| `wind_spd_avg` | m/s | SMA Halifax (Herring Cove, Fairview, Pier 9C) | 2013–present | Multiple Halifax stations inside ROI |
| `wind_spd_max` (gust) | m/s | SMA Halifax | 2013–present | Inside ROI |
| `wind_dir_avg` | degree | SMA Halifax | 2013–present | Inside ROI |
| `air_temp_avg` | °C | SMA Halifax (Herring Cove, Fairview, Pier 9C) | 2013–present | Inside ROI |
| `air_pressure_avg` | mbar | SMA Halifax | 2013–present | Inside ROI |
| `air_dewpoint_avg` | °C | SMA Halifax Fairview, Pier 9C | 2015–present | Inside ROI |
| `air_humidity_avg` | relative | SMA Halifax Fairview, Pier 9C | 2015–present | Inside ROI |
| `humidex` / `wind_chill` | °C | SMA Halifax Fairview, Pier 9C | 2015–present | Inside ROI |

#### Offshore Buoys (Near ROI)

| Variable Name(s) | Units | Source(s) | Temporal Span | Notes |
|---|---|---|---|---|
| `WDIR` / `WSPD` / `GSPD` | °, m/s, m/s | CanWIN: DFO MEDS buoys | varies | Offshore buoys 44137, 44150 |
| `ATMS` (atmospheric pressure) | mbar | CanWIN: DFO MEDS buoys | varies | Offshore buoys |
| `DRYT` (dry bulb temperature) | °C | CanWIN: DFO MEDS buoys | varies | Offshore buoys |
| `SSTP` (sea surface temp) | °C | CanWIN: DFO MEDS buoys | varies | Offshore buoys |
| `avg_air_temp_pst10mts` | °C | CanWIN: ECCC MSC buoys | varies | Offshore buoys |
| `avg_mslp_pst10mts` | hPa | CanWIN: ECCC MSC buoys | varies | Offshore buoys |

---

### BIODIVERSITY / SPECIES

#### OBIS — 501,900 occurrence records in ROI

| Field | Description | API |
|---|---|---|
| `scientificName` | Species (e.g., *Homarus americanus*, *Gadus morhua*, *Scomber scombrus*, *Thysanoessa inermis*) | OBIS REST API / `robis` R package |
| `decimalLatitude` / `decimalLongitude` | Position | OBIS |
| `eventDate` | Date of observation | OBIS |
| `individualCount` | Count/abundance | OBIS |
| `depth` | Observation depth (m) | OBIS |
| `AphiaID` | WoRMS taxonomy identifier | OBIS |

**Key Scotian Shelf OBIS datasets:**
- Maritimes Spring RV Surveys — 650,166 records, bottom trawl, 273 species
- Atlantic Reference Centre Museum — 139,730 records, 1,978 species (invertebrates + fishes + ichthyoplankton)

**Note:** No measurement/fact (MoF) data (fish length, weight, sex, maturity) within the exact ROI bounding box. Those are likely in DFO BioChem database rather than OBIS directly.

#### OTN Acoustic Animal Detections (broader NW Atlantic)

| Variable | Description | Source |
|---|---|---|
| `detection_id` / `transmitter_id` | Tag/detection identifiers | OTN ERDDAP (members.oceantrack.org/erddap/) |
| `latitude` / `longitude` / `depth` | Detection position | OTN |
| `sensor_data` | Sensor values (e.g., temperature, depth from tag) | OTN |
| `platform_name` / `bottom_depth` | Receiver metadata | OTN |
| `project_name` / `project_pi` / `project_doi` | Project provenance | OTN |

---

### WHAT IS INSIDE vs OUTSIDE THE ROI BOUNDING BOX

**INSIDE the bounding box (43.68–44.83°N, -64.33 to -61.94°W):**

| Data Source | What's Inside |
|---|---|
| SMA Halifax (Herring Cove) buoy | Waves (Hs, Hmax, T, Dir, spread), wind, SST, air temp/pressure, **current profiles at 20 depth levels** |
| SMA Halifax Fairview | Wind, air temp, dewpoint, humidity, pressure |
| SMA Halifax pier9c | Wind, air temp, dewpoint, humidity, pressure, **tide height** |
| SMA Halifax anemometer1 | Wind speed, direction, gusts |
| BBMP Bedford Basin bottle | 30+ years of biweekly: nutrients (ammonia, nitrite, nitrate, phosphate, silicate), oxygen, chl-a, HPLC pigments (18 types), POC/PON, pH |
| AZMP/Ecosystem CTD profiles | Some stations within box — full water column profiles: T, S, O2, chl, CDOM, nutrients, PAR, transmittance |
| Copernicus Global PHY/WAV/BGC | Global model data subset to ROI |
| HYCOM | Global model data subset to ROI |
| GEBCO | Bathymetry |
| OBIS | 501,900 species occurrence records |

**OUTSIDE / NOT in the bounding box:**

| Data Source | Why Not |
|---|---|
| Argo floats | ROI too shallow (<200m shelf). **ZERO Argo profiles.** Nearest: ~2,235 profiles in NW Atlantic deep water east of shelf break |
| DFO MEDS buoys (44137, 44150) | Too far offshore/south (42.28–42.50°N) — not in ROI |
| Halifax Harbour buoy (44258) | At 44.50°N, -63.40°W — this IS inside the box! Check data availability |
| HF radar | None found on Scotian Shelf. Nearest: US Gulf of Maine |
| Glider data | Not found on CIOOS ERDDAP for this region |
| SLGO buoys | Gulf of St. Lawrence, north of ROI |
| ONC cabled observatories | Pacific / Arctic only |
| OBIS MoF (fish length/weight) | Not in this specific bounding box |

---

### TEMPORAL COVERAGE SUMMARY

```
1967 ────────────────────────────────────────────────────────────── 2026
│     │         │         │         │         │         │         │
│     │         │         │         │         │         │         │
├─────┤ Historical coastal moored CTD (1967–2017)                   │
│     │         │         │         │         │         │         │
├─────┤ Historical coastal CTD profiles (1969–2023)                  │
│     │         │         │         │         │         │         │
│     ├─────────┤ BBMP Bedford Basin bottle (1992–2024)              │
│     │         │         │         │         │         │         │
│     ├─────────┤ Copernicus PHY+BGC Reanalysis (1993–2026)          │
│     │         │         │         │         │         │         │
│     ├─────────┤ HYCOM Reanalysis (1994–2015)                       │
│     │         │         │         │         │         │         │
│     ├─────────┤ AZMP/Ecosystem CTD (1996–2026)                     │
│     │         │         │         │         │         │         │
│     │         │    ├────┤ Copernicus WAV Reanalysis (1980–present) │
│     │         │         ├──┤ SMA Halifax buoys (2013–present)      │
│     │         │         │   ├──┤ AZMP Moored CTD (2000–2023)      │
│     │         │         │         ├────┤ HYCOM GOFS 3.1 (2018–2024)│
│     │         │         │         │   ├────┤ Copernicus PHY NRT    │
│     │         │         │         │   │    │ (2020–present)        │
│     │         │         │         │   │    ├───┤ HYCOM ESPC-D-V02  │
│     │         │         │         │   │    │   │ (2024–present)    │
1967  1975    1985      1995      2005      2015      2025
```

---

### SPATIAL RESOLUTION SUMMARY (finest to coarsest)

| Resolution | Source | Type |
|---|---|---|
| **~1–2 m vertical** | CIOOS CTD rosette profiles | In-situ casts |
| **Point stations** | SMA Halifax buoys, BBMP, moored CTD | In-situ continuous |
| **15 arc-sec (~450 m)** | GEBCO 2026 | Bathymetry grid |
| **1/12° (~6–8 km at 45°N)** | Copernicus Global PHY/WAV, HYCOM | Model grid |
| **0.25° (~27 km)** | Copernicus Global BGC | Model grid |
| **0.5° (~55 km)** | Copernicus In-Situ NRT ISAS | Optimal interpolation |

---

### DEPTH LEVELS

**Copernicus Global PHY (50 levels, meters, positive down):**
0.49, 1.54, 2.66, 3.87, 5.19, 6.64, 8.25, 10.05, 12.08, 14.37, 16.96, 19.90, 23.23, 27.02, 31.33, 36.23, 41.79, 48.10, 55.24, 63.32, 72.44, 82.74, 94.35, 107.42, 122.13, 138.73, 157.35, 178.39, 202.16, 228.98, 259.24, 293.36, 331.84, 375.26, 424.23, 479.51, 541.93, 612.44, 692.13, 782.23, 884.08, 999.15, 1128.96, 1274.94, 1438.20, 1619.40, 1818.50, 2034.50, 2265.20, 2507.50, ..., 5727.92

**HYCOM (41 hybrid isopycnal-z-sigma layers):**
0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 125, 150, 200, 250, 300, 350, 400, 500, 600, 700, 800, 900, 1000, 1250, 1500, 2000, 2500, 3000, 4000, 5000, **bottom** (terrain-following)

For Scotian Shelf (depths ~50–200 m on shelf, >1000 m at shelf break): upper ~10–20 HYCOM layers are above the seafloor on the shelf.

---

### OPEN-METEO MARINE API — ICON Wave Forecast (DWD)

**What it is:** Open-Meteo Marine API provides hourly ocean wave, surface current, SST, and sea level data. Backed by the German Weather Service (DWD) ICON wave model. **No auth required.** Archive goes back to 2000. Forecast up to 6 days.

**Base URL:** `https://marine-api.open-meteo.com/v1/marine`

**Regional relevance:** Direct bounding box query for our ROI. Complementary to Copernicus WAV — this gives an independent model source for ensemble/validation.

**Python package:** `openmeteo-requests`

```bash
pip install openmeteo-requests requests-cache retry-requests numpy pandas
```

```python
import openmeteo_requests
import requests_cache
from retry_requests import retry

cache = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://marine-api.open-meteo.com/v1/marine"
params = {
    "hourly": [
        "wave_height", "wave_direction", "wave_period", "wave_peak_period",
        "wind_wave_height", "wind_wave_direction", "wind_wave_period",
        "wind_wave_peak_period",
        "swell_wave_height", "swell_wave_direction", "swell_wave_period",
        "swell_wave_peak_period",
        "second_swell_wave_height", "second_swell_wave_period", "second_swell_wave_direction",
        "third_swell_wave_height", "third_swell_wave_period", "third_swell_wave_direction",
        "sea_level_height_msl", "sea_surface_temperature",
        "ocean_current_velocity", "ocean_current_direction"
    ],
    "bounding_box": "43.675818,-64.328234,44.831526,-61.943675",
    "start_date": "2026-05-01",
    "end_date": "2026-05-23"
}
responses = openmeteo.weather_api(url, params=params)
```

**Variables provided:**

| Variable | Units | Description | Temporal Span | Resolution |
|---|---|---|---|---|
| `wave_height` | m | Significant wave height (all sea states) | Jan 2000–present (archive) + 6d forecast | Hourly, 0.25° (~27 km) |
| `wave_direction` | ° (from) | Mean wave direction (where waves come FROM) | Same | Hourly, 0.25° |
| `wave_period` | s | Mean wave period | Same | Hourly, 0.25° |
| `wave_peak_period` | s | Peak wave period | Same | Hourly, 0.25° |
| `wind_wave_height` | m | Wind sea significant height | Same | Hourly, 0.25° |
| `wind_wave_direction` | ° | Wind sea direction | Same | Hourly, 0.25° |
| `wind_wave_period` | s | Wind sea period | Same | Hourly, 0.25° |
| `wind_wave_peak_period` | s | Wind sea peak period | Same | Hourly, 0.25° |
| `swell_wave_height` | m | Primary swell significant height | Same | Hourly, 0.25° |
| `swell_wave_direction` | ° | Primary swell direction | Same | Hourly, 0.25° |
| `swell_wave_period` | s | Primary swell period | Same | Hourly, 0.25° |
| `swell_wave_peak_period` | s | Primary swell peak period | Same | Hourly, 0.25° |
| `secondary_swell_wave_height` | m | Secondary swell significant height | Same | Hourly, 0.25° |
| `secondary_swell_wave_period` | s | Secondary swell period | Same | Hourly, 0.25° |
| `secondary_swell_wave_direction` | ° | Secondary swell direction | Same | Hourly, 0.25° |
| `tertiary_swell_wave_height` | m | Tertiary swell significant height | Same | Hourly, 0.25° |
| `tertiary_swell_wave_period` | s | Tertiary swell period | Same | Hourly, 0.25° |
| `tertiary_swell_wave_direction` | ° | Tertiary swell direction | Same | Hourly, 0.25° |
| `ocean_current_velocity` | m/s | Surface current velocity (Eulerian + Stokes + tides) | Same | Hourly, 0.25° |
| `ocean_current_direction` | ° (to) | Surface current direction (direction current flows TOWARD) | Same | Hourly, 0.25° |
| `sea_surface_temperature` | °C | SST close to water surface | Same | Hourly, 0.25° |
| `sea_level_height_msl` | m | Sea level height (tides + IB + steric + mass) | Same | Hourly, 0.25° |
| `invert_barometer_height` | m | Inverse barometer effect on sea level | Same | Hourly, 0.25° |

**Key difference from Copernicus WAV:**
- Open-Meteo Marine has **3 swell partitions** (primary, secondary, tertiary) vs Copernicus WAV's 2 partitions
- Open-Meteo current direction flows **TOWARD** (oceanographic convention); wave direction flows **FROM** (meteorological convention)
- Open-Meteo: **0.25° resolution, hourly, 2000–present + 6d forecast**
- Copernicus WAV: **0.083° resolution, 3-hourly, 1980–present + 10d forecast**
- Open-Meteo: **no auth.** Copernicus: **requires registration.**

**Citation:** Generated using ICON Wave forecast from DWD. Attribution required. Zippenfenig, P. (2023). Open-Meteo.com [doi:10.5281/ZENODO.7970649](https://doi.org/10.5281/ZENODO.7970649)

---

### OPEN-METEO ATMOSPHERE API — ERA5-Based Weather

**What it is:** Open-Meteo Atmosphere API provides hourly atmospheric/weather data from ERA5/ERA5-Land reanalysis and GFS forecast. Wind speed at 10m AND 100m (critical for offshore wind energy). **No auth required.**

**Base URL:** `https://archive-api.open-meteo.com/v1/archive` (historical) and `https://api.open-meteo.com/v1/forecast` (forecast)

**Regional relevance:** Wind at hub height (100m) is essential for the wind energy module. Also drives ocean wave generation (wind forcing). Bounding box query works directly.

**Variables provided (hourly, for our ROI):**

| Variable | Units | Description | Temporal Span |
|---|---|---|---|
| `temperature_2m` | °C | Air temperature at 2m | 1940–present (ERA5) |
| `dew_point_2m` | °C | Dew point at 2m | Same |
| `relative_humidity_2m` | % | RH at 2m | Same |
| `apparent_temperature` | °C | Feels-like temperature | Same |
| `pressure_msl` | hPa | Mean sea level pressure | Same |
| `surface_pressure` | hPa | Surface pressure | Same |
| `precipitation` | mm | Total precipitation (preceding hour) | Same |
| `rain` | mm | Liquid precipitation | Same |
| `snowfall` | cm | Snowfall | Same |
| `snow_depth` | m | Snow depth on ground | Same |
| `cloud_cover` | % | Total cloud cover | Same |
| `cloud_cover_low` | % | Low clouds (0-2 km) | Same |
| `cloud_cover_mid` | % | Mid clouds (2-6 km) | Same |
| `cloud_cover_high` | % | High clouds (>6 km) | Same |
| **`wind_speed_10m`** | **km/h (m/s)** | **Wind speed at 10m** | **1940–present** |
| **`wind_speed_100m`** | **km/h (m/s)** | **Wind speed at 100m (hub height!)** | **1940–present** |
| **`wind_direction_10m`** | **°** | **Wind direction at 10m** | **1940–present** |
| **`wind_direction_100m`** | **°** | **Wind direction at 100m** | **1940–present** |
| `wind_gusts_10m` | km/h (m/s) | Wind gusts at 10m | Same |
| `et0_fao_evapotranspiration` | mm | Reference evapotranspiration | Same |
| `vapour_pressure_deficit` | kPa | VPD | Same |
| `weather_code` | WMO code | Weather condition | Same |
| `soil_temperature_0_to_7cm` | °C | Soil temp layer 1 | Same (ERA5-Land) |
| `soil_temperature_7_to_28cm` | °C | Soil temp layer 2 | Same |
| `soil_temperature_28_to_100cm` | °C | Soil temp layer 3 | Same |
| `soil_temperature_100_to_255cm` | °C | Soil temp layer 4 | Same |
| `soil_moisture_0_to_7cm` | m³/m³ | Soil moisture layer 1-4 | Same |

**Additional daily variables:** `temperature_2m_max/min`, `apparent_temperature_max/min`, `precipitation_sum`, `rain_sum`, `snowfall_sum`, `precipitation_hours`, `sunrise/sunset`, `sunshine_duration`, `daylight_duration`, `wind_speed_10m_max`, `wind_gusts_10m_max`, `wind_direction_10m_dominant`, `shortwave_radiation_sum`, `et0_fao_evapotranspiration`

**Additional radiation variables (hourly):** `shortwave_radiation` (W/m²), `direct_radiation`, `direct_normal_irradiance`, `diffuse_radiation`, `global_tilted_irradiance`, `sunshine_duration`

**Python access:**
```python
import openmeteo_requests

openmeteo = openmeteo_requests.Client()

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "hourly": [
        "temperature_2m", "wind_speed_10m", "wind_speed_100m",
        "wind_direction_10m", "wind_direction_100m", "wind_gusts_10m",
        "pressure_msl", "precipitation", "cloud_cover"
    ],
    "bounding_box": "43.675818,-64.328234,44.831526,-61.943675",
    "start_date": "2026-05-01",
    "end_date": "2026-05-23"
}
responses = openmeteo.weather_api(url, params=params)
```

**Spatial resolution:** 0.25° for ERA5, ~0.1° for ERA5-Land (soil variables). Forecast (GFS): 0.25°.

**Citation:** Hersbach et al. (2023) ERA5 hourly data [doi:10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47). Zippenfenig, P. (2023) Open-Meteo [doi:10.5281/ZENODO.7970649](https://doi.org/10.5281/ZENODO.7970649).

---

### GLOBAL FISHING WATCH — Gridded Vessel Activity

**What it is:** Global Fishing Watch (GFW) provides gridded vessel presence and fishing effort data via the 4Wings API. Uses AIS data to compute hours of vessel presence per grid cell, classified by vessel type (fishing, cargo, tanker, passenger, etc.) and flag state. **Free API token required.**

**Token:** Your friend already has a valid token. Register at https://globalfishingwatch.org/apis

**API Base:** `https://gateway.api.globalfishingwatch.org/v3/4wings/report`

**Regional relevance:** Directly quantifies human pressure (fishing effort, shipping traffic) on the Scotian Shelf ecosystem. Essential for:
1. Ship strike risk layer (for whale/NARW models)
2. Fishing pressure layer for marine spatial planning
3. Noise pollution proxy
4. Validation of Lagrangian drift against real vessel tracks

**Variables provided (per grid cell):**

| Field | Description |
|---|---|
| `hours` | Total vessel presence hours in grid cell over selected period |
| `vessel_class` | Fishing, Cargo, Tanker, Passenger, Tug, etc. |
| `flag` | Vessel flag state (country) |
| `gear_type` | Fishing gear type (trawler, longliner, purse seine, etc.) — fishing vessels only |
| `lat` / `lon` | Grid cell center |
| `date_range` | Temporal aggregation window |

**Spatial resolution options:** `LOW` (0.1°) or `HIGH` (0.01°) — for our ROI use `HIGH`

**Python access (from your friend's code, refined):**

```python
import requests
import time
import pandas as pd

api_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtpZEtleSJ9..."

url = "https://gateway.api.globalfishingwatch.org/v3/4wings/report"
headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

params = {
    "spatial-resolution": "LOW",
    "temporal-resolution": "ENTIRE",
    "spatial-aggregation": "false",
    "datasets[0]": "public-global-presence:latest",
    "date-range": "2023-07-01,2023-07-31",
    "format": "JSON"
}

payload = {
    "geojson": {
        "type": "Polygon",
        "coordinates": [[[-64.33, 43.68], [-61.94, 43.68],
                         [-61.94, 44.83], [-64.33, 44.83],
                         [-64.33, 43.68]]]
    }
}

response = requests.post(url, headers=headers, params=params, json=payload)

if response.status_code in [200, 201]:
    data = response.json()
    print(f"Got {len(data.get('entries', []))} grid cells")
elif response.status_code == 202:
    # Poll for async result
    job_id = response.json()["id"]
    while True:
        time.sleep(10)
        r = requests.get(f"https://gateway.api.globalfishingwatch.org/v3/4wings/report/{job_id}", headers=headers)
        if r.status_code == 200:
            data = r.json()
            break
```

**Key endpoints:**

| Endpoint | Purpose |
|---|---|
| `POST /v3/4wings/report` | Create gridded report (async for large areas) |
| `GET /v3/4wings/report/{id}` | Poll report status |
| `GET /v3/vessels/search` | Search vessel by MMSI or name |
| `GET /v3/vessels/{id}/tracks` | Get vessel track (individual) |

**Free tier limits:** ~1000 API calls/day. Our ROI requires per query. For continuous monitoring, use AIS Stream (real-time WebSocket) + GFW (gridded historical aggregates).

---

### RECOMMENDED INGESTION PRIORITY (Hackathon MVP)

| Priority | Source | What You Get | Setup Time |
|---|---|---|---|
| **1** | Copernicus Marine (register free account NOW) | T, S, U, V, SSH, waves (wind sea + 2 swell partitions), MLD, ice | ~15 min registration + `pip install copernicusmarine` |
| **2** | GEBCO 2026 | Bathymetry (one-time download) | 5 min download |
| **3** | **Open-Meteo Marine** | Waves (3 swell partitions), SST, surface currents — NO AUTH, hourly since 2000 | `pip install openmeteo-requests`, 1 min |
| **4** | **Open-Meteo Atmosphere** | Wind at 10m & 100m (hub height!), air temp, pressure, precipitation — ERA5 since 1940 | Same package, 1 min |
| **5** | HYCOM ESPC-D-V02 | 3D T, S, U, V from different model → ensemble/validation | Open OPeNDAP, no auth |
| **6** | CIOOS Atlantic ERDDAP | In-situ CTD (T, S, O2, chl, nutrients), SMA Halifax buoy (waves + current profiles at 20 depths) | Open REST, no auth |
| **7** | Copernicus BGC | Chl, NO3, PO4, O2, pH, pCO2, NPP, phytoplankton carbon | Same Copernicus account |
| **8** | OBIS | 501,900 species occurrences for habitat/risk modeling | Open REST |
| **9** | **Global Fishing Watch** | Gridded fishing/shipping pressure — direct human-activity layer | Free token (your friend has one) |

---

### REGION BOUNDING BOX (for API queries)

```
# WGS84 (-180 to 180)
Latitude:  43.68 to 44.83
Longitude: -64.33 to -61.94

# WGS84 (0 to 360 — used by HYCOM, GEBCO, some CMEMS)
Longitude: 295.67 to 298.06
```

### QUICK-START: Copernicus Access + First Data Pull (v2 API)

```bash
# 1. Register at https://data.marine.copernicus.eu/register (FREE)
# 2. Install toolbox
pip install copernicusmarine

# 3. Login (caches creds at ~/.copernicusmarine/)
# CLI path may be: ~/Library/Python/3.13/bin/copernicusmarine login
copernicusmarine login
```

```python
import copernicusmarine as cm

# Pull 3D temperature, salinity, currents for Scotian Shelf
# In Copernicus v2, 3D variables are split into separate datasets.

# Temperature (50 levels)
ds_thetao = cm.open_dataset(
    dataset_id="cmems_mod_glo_phy-thetao_anfc_0.083deg_PT6H-i",
    start_datetime="2026-05-22T00:00:00",
    end_datetime="2026-05-22T18:00:00",
    minimum_longitude=-64.33, maximum_longitude=-61.94,
    minimum_latitude=43.68, maximum_latitude=44.83,
    minimum_depth=0.49, maximum_depth=200.0,
)

# Salinity (50 levels)
ds_so = cm.open_dataset(
    dataset_id="cmems_mod_glo_phy-so_anfc_0.083deg_PT6H-i",
    start_datetime="2026-05-22T00:00:00",
    end_datetime="2026-05-22T18:00:00",
    minimum_longitude=-64.33, maximum_longitude=-61.94,
    minimum_latitude=43.68, maximum_latitude=44.83,
    minimum_depth=0.49, maximum_depth=200.0,
)

# Currents uo, vo (50 levels)
ds_cur = cm.open_dataset(
    dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i",
    start_datetime="2026-05-22T00:00:00",
    end_datetime="2026-05-22T18:00:00",
    minimum_longitude=-64.33, maximum_longitude=-61.94,
    minimum_latitude=43.68, maximum_latitude=44.83,
    minimum_depth=0.49, maximum_depth=200.0,
)

# Merge into one xarray Dataset
ds = cm.merge(ds_thetao, ds_so, ds_cur)

# Surface/2D fields (SSH, MLD, ice, bottom T/S)
ds_2d = cm.open_dataset(
    dataset_id="cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
    start_datetime="2026-05-20",
    end_datetime="2026-05-23",
    minimum_longitude=-64.33, maximum_longitude=-61.94,
    minimum_latitude=43.68, maximum_latitude=44.83,
)

print(f"3D variables: {list(ds.data_vars.keys())}")
print(f"2D variables: {list(ds_2d.data_vars.keys())}")
# Output: 3D: ['thetao', 'so', 'uo', 'vo']
# Output: 2D: ['zos', 'mlotst', 'tob', 'sob', 'siconc', 'sithick', ...]
```
