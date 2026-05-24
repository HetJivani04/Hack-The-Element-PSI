# Tool Execution Specification — Marine Digital Twin

**Every tool defined with: exact input variables (from our catalog), exact processing steps, exact output format.**

---

## INPUT: Windmill Parameters (from Client/User)

These are the variables the user provides through the frontend:

| # | Parameter | Type | Default | Description |
|---|-----------|------|---------|-------------|
| W1 | `site_lon` | float | — | Windmill longitude (-64.33 to -61.94) |
| W2 | `site_lat` | float | — | Windmill latitude (43.68 to 44.83) |
| W3 | `hub_height_m` | float | 150 | Hub height above sea surface |
| W4 | `rotor_diameter_m` | float | 236 | Rotor diameter (15 MW class) |
| W5 | `rated_power_mw` | float | 15 | Rated power |
| W6 | `cut_in_wind_ms` | float | 3.5 | Cut-in wind speed |
| W7 | `rated_wind_ms` | float | 11.0 | Rated wind speed |
| W8 | `cut_out_wind_ms` | float | 25.0 | Cut-out wind speed |
| W9 | `thrust_coefficient_curve` | dict | — | Ct as function of wind speed: {u: Ct} from manufacturer |
| W10 | `power_coefficient_curve` | dict | — | Cp as function of wind speed: {u: Cp} from manufacturer |
| W11 | `foundation_type` | enum | monopile | monopile / jacket / floating |
| W12 | `foundation_diameter_m` | float | 10 | Foundation/pile diameter |
| W13 | `cable_voltage_kv` | float | 66 | Export cable voltage |
| W14 | `cable_current_a` | float | 138 | Export cable current per turbine |
| W15 | `cable_burial_depth_m` | float | 2 | Cable burial depth |
| W16 | `n_turbines` | int | 1 | Number of turbines (1 for MVP) |
| W17 | `time_start` | date | — | Simulation start date |
| W18 | `time_end` | date | — | Simulation end date |
| W19 | `n_particles` | int | 500 | Number of Lagrangian particles |
| W20 | `release_depth_m` | float | 10 | Particle release depth |
| W21 | `diffusivity_mode` | enum | auto | auto (compute from stratification) / manual (user value) |
| W22 | `include_windage` | bool | True | Include wind drift on surface particles |
| W23 | `include_tides` | bool | True | Include tidal currents |
| W24 | `include_stokes` | bool | True | Include Stokes drift |
| W25 | `noise_source_type` | enum | operational | operational / construction / both |
| W26 | `frequency_bands_hz` | list | [50, 200, 500, 1000] | Acoustic frequency bands to compute |

---

## TOOL 1: BASELINE CHARACTERIZATION

**Purpose:** Extract and characterize the pre-windmill environment at the site.

### Input Variables (from our data cube)

| ID | Variable | Source | Cube Path |
|----|----------|--------|-----------|
| 1.1 | `thetao` | GLORYS12 + NRT | `physics_3d.zarr/thetao` |
| 1.8 | `so` | GLORYS12 + NRT | `physics_3d.zarr/so` |
| 1.12 | `uo` | GLORYS12 + NRT | `physics_3d.zarr/uo` |
| 1.13 | `vo` | GLORYS12 + NRT | `physics_3d.zarr/vo` |
| 2.1 | `zos` | GLORYS12 + NRT | `surface.zarr/zos` |
| 2.7 | `mlotst` | GLORYS12 + NRT | `surface.zarr/mlotst` |
| 3.1 | `VHM0` | Copernicus WAV + WAVERYS | `waves.zarr/VHM0` |
| 3.4 | `VTPK` | Copernicus WAV + WAVERYS | `waves.zarr/VTPK` |
| 3.8 | `VMDR` | Copernicus WAV + WAVERYS | `waves.zarr/VMDR` |
| 4.5 | Wind 100m u/v | ERA5 | `atmosphere.zarr/u100,v100` |
| 4.1 | Wind 10m u/v | ERA5 | `atmosphere.zarr/u10,v10` |
| 4.8 | T2m | ERA5 | `atmosphere.zarr/t2m` |
| 8.1 | `chl` | Copernicus BGC | `bgc.zarr/chl` |
| 10.1 | `elevation` | GEBCO | `seafloor.zarr/elevation` |

### Processing Steps

**Step 1 — Point Extraction:**
Extract time series at the exact windmill site (W1, W2). For gridded variables: bilinear interpolation from 4 nearest grid cells. For point data: nearest station. Time range: W17 to W18.

**Step 2 — Climatology Computation:**
For each variable over the full time series:
- Monthly mean ± 1σ (seasonal cycle)
- Overall mean, median, min, max, 5th/95th percentiles
- Long-term trend: Mann-Kendall test + Sen's slope
- Extremes: Fit GEV distribution to annual maxima → 10-year, 50-year, 100-year return levels

**Step 3 — Vertical Profiles:**
Extract T(z), S(z), u(z), v(z) at the site for each month → mean T(z) profile, mean S(z) profile, mean current profile.

**Step 4 — Wind/Wave Climate:**
- Wind rose: directional frequency distribution at 100m from hourly ERA5
- Wave rose: directional frequency distribution from hourly Copernicus WAV
- Joint probability distribution: Hs vs Tp scatter, Hs vs Wind speed scatter

**Step 5 — Data Quality Report:**
For every variable: temporal coverage %, source quality flag distribution, nearest real observation station distance, missing periods listed.

### Output

```
{
  "site": {"lon": -63.45, "lat": 44.12, "depth_m": 87.3},
  "time_range": {"start": "2016-01-01", "end": "2026-05-23"},

  "climatology": {
    "temperature": {
      "annual_mean_c": 9.47,
      "annual_range_c": {"min": 0.8, "max": 20.3},
      "monthly_means": {"Jan": 2.1, "Feb": 1.3, ..., "Aug": 17.8},
      "monthly_std": {"Jan": 1.2, "Feb": 0.9, ..., "Aug": 2.1},
      "trend_c_per_decade": 0.31,
      "trend_p_value": 0.003,
      "extremes": {"10yr_return_c": 22.1, "50yr_return_c": 23.8}
    },
    "salinity": { ... },
    "currents": {
      "surface": {"mean_u_ms": 0.08, "mean_v_ms": -0.12, "max_speed_ms": 0.89},
      "near_bed": {"mean_u_ms": 0.03, "mean_v_ms": -0.05}
    },
    "waves": {
      "mean_hs_m": 1.9,
      "max_hs_m": 9.5,
      "mean_tp_s": 8.3,
      "dominant_direction_deg": 210,
      "extreme_hs": {"10yr_m": 10.2, "50yr_m": 11.8, "100yr_m": 12.5}
    },
    "wind_100m": {
      "mean_speed_ms": 8.7,
      "max_speed_ms": 32.1,
      "dominant_direction_deg": 245,
      "weibull_shape_k": 2.3,
      "weibull_scale_c": 9.8,
      "wind_power_density_wm2": 612
    },
    "mixed_layer": {"mean_mld_m": 25.3, "max_mld_m": 87.3, "summer_mean_m": 12.1}
  },

  "profiles": {
    "temperature": [[0, 15.2], [10, 14.1], [20, 9.8], [50, 5.2], [87, 3.1]],
    "salinity": [[0, 31.2], [10, 31.5], [20, 32.1], [50, 32.8], [87, 33.2]],
    "sound_speed": [[0, 1495], [10, 1490], [20, 1475], [50, 1460], [87, 1455]]
  },

  "data_quality": {
    "thetao": {"coverage_pct": 100, "quality": "multi-model ensemble, buoy 28.4 km away"},
    "chl": {"coverage_pct": 100, "quality": "single-model, 0.25° native, nearest CTD 15.7 km"},
    "sediment": {"coverage_pct": 0, "quality": "MISSING — no sediment data for this site"}
  },

  "figures": {
    "wind_rose_png": "/api/jobs/{id}/figures/wind_rose.png",
    "wave_rose_png": "/api/jobs/{id}/figures/wave_rose.png",
    "ts_diagram_png": "/api/jobs/{id}/figures/ts_diagram.png",
    "profile_png": "/api/jobs/{id}/figures/profiles.png",
    "seasonal_cycle_png": "/api/jobs/{id}/figures/seasonal.png"
  }
}
```

---

## TOOL 2: WIND WAKE MODELING

**Purpose:** Compute the wind speed deficit field behind the windmill.

### Input Variables

| ID | Variable | Source | Usage |
|----|----------|--------|-------|
| 4.5 | `u100`, `v100` | ERA5 | Freestream wind at hub height → u∞ |
| 4.19 | `zust` (friction velocity) | ERA5 | Compute TI_amb = u*/U |
| 4.17 | `blh` (boundary layer height) | ERA5 | Stability correction via L |
| 4.8 | `t2m` | ERA5 | Air-sea temp difference ΔT for stability |
| 2.10 | SST | ERA5 | Air-sea temp difference |
| 4.10 | MSLP | ERA5 | Air density ρ = p/(R·T) |
| 10.1 | Bathymetry | GEBCO | Not directly used for wake but for context |

Plus user windmill parameters: W3 (hub height), W4 (rotor diameter), W9 (Ct curve)

### Processing Steps

**Step 1 — Compute atmospheric stability:**
From real ERA5 data at the site and timestep:
```
u* = zust (from ERA5 friction velocity)
θ_v = t2m + 0.61·q·t2m  (virtual potential temp)
L = -u*³·θ_v / (κ·g·w′θ_v′)  (Obukhov length from surface heat flux)
z0 = α_ch·u*²/g  (Charnock, α_ch=0.0144)
```
Classification: L < 0 → unstable, L > 0 → stable, |L| > 500 → neutral

**Step 2 — Compute turbulence intensity:**
```
TI_amb = u* / U  where U = √(u100² + v100²) from ERA5
```

**Step 3 — Compute wake expansion rate k*:**
```
k* = 0.35 · TI_amb · f(z/L)
f(z/L) = φ_m(z/L)^(-1)  (stability function from Dyer 1974)
```
k* is NOT a constant — varies with real atmospheric conditions at each timestep.

**Step 4 — Compute initial wake width ε:**
```
Ct = thrust_coefficient_curve[U]  (from manufacturer data at current U)
β = (1 + √(1-Ct)) / (2·√(1-Ct))
ε = 0.25 · √β
```

**Step 5 — Compute Gaussian wake field:**
For each downstream distance x (0 to 20·D, Δx = D/2) and radial distance r (0 to 4·σ):
```
σ(x) = D · (k*·x/D + ε)

Δu(x,r) / u∞ = [1 - √(1 - Ct/(8·(σ/D)²))] · exp(-r²/(2·σ²))

u_wake(x,r) = u∞ - Δu(x,r)
```

The wake centerline is oriented along the mean wind direction at each timestep.

**Step 6 — Compute time-averaged wake field:**
Average u_wake(x,r) over all timesteps in the period W17-W18. This gives the mean wake deficit.

**Step 7 — Compute wake statistics:**
- Wake recovery distance: x where Δu/u∞ < 0.05 (95% recovery)
- Annual wake-affected area: area where mean Δu/u∞ > 0.02
- Wake frequency: fraction of time wind comes from each direction sector

### Output

```
{
  "wake_field": {
    "type": "spatial_grid",
    "dimensions": {"downstream_km": 40, "crosswind_km": 20},
    "resolution_m": 200,
    "values": {
      "mean_deficit_pct": [[...]],    // 2D array: mean Δu/u∞ as percentage
      "std_deficit_pct": [[...]],     // 2D array: standard deviation
      "mean_wind_ms": [[...]]          // 2D array: mean u_wake in m/s
    }
  },

  "wake_statistics": {
    "mean_freestream_ms": 8.7,
    "mean_deficit_at_2D_pct": 18.3,
    "mean_deficit_at_5D_pct": 8.1,
    "mean_deficit_at_10D_pct": 3.4,
    "recovery_distance_km": 12.8,
    "wake_affected_area_km2": 45.3,
    "annual_energy_loss_pct": 0  // for single turbine, 0; for arrays this matters
  },

  "stability_breakdown": {
    "unstable_pct": 32,
    "neutral_pct": 45,
    "stable_pct": 23,
    "mean_k_star_unstable": 0.058,
    "mean_k_star_neutral": 0.045,
    "mean_k_star_stable": 0.031
  },

  "figures": {
    "wake_field_png": "/api/jobs/{id}/figures/wake_deficit_map.png",
    "wake_profile_png": "/api/jobs/{id}/figures/wake_centerline.png"
  }
}
```

---

## TOOL 3: LAGRANGIAN PARTICLE TRACKING

**Purpose:** Release virtual particles at the windmill site and track their trajectories under real currents, waves, tides, and diffusion.

### Input Variables

| ID | Variable | Source | Usage |
|----|----------|--------|-------|
| 1.12 | `uo` | GLORYS12 + NRT | Eastward advection at each depth |
| 1.13 | `vo` | GLORYS12 + NRT | Northward advection at each depth |
| 1.1 | `thetao` | GLORYS12 + NRT | Compute density/stratification → Kz |
| 1.8 | `so` | GLORYS12 + NRT | Compute density/stratification → Kz |
| 2.7 | `mlotst` | GLORYS12 + NRT | Kz scaling via KPP |
| 3.20 | `VSDX` | Copernicus WAV | Stokes drift eastward |
| 3.21 | `VSDY` | Copernicus WAV | Stokes drift northward |
| 2.1 | `zos` | GLORYS12 + NRT | Barotropic sea level |
| 4.1 | `u10`, `v10` | ERA5 | Windage (surface drift) |
| 10.1 | Bathymetry | GEBCO | Coastline boundary, depth |
| 6.1 | Tidal constituents | DFO WebTide | Tidal current prediction |

Plus user parameters: W1-W2 (site), W17-W18 (time), W19 (n_particles), W20 (release depth), W21-W24 (options)

### Processing Steps

**Step 1 — Initialize particles:**
Create N particles (W19) at position (W1, W2, W20). Assign particle IDs 1..N.

**Step 2 — Compute diffusivity field:**
For each timestep at the site and surrounding ROI:
```
N²(z) = -(g/ρ₀)·∂ρ_θ/∂z     [from thetao(z), so(z) profiles]
S²(z) = (∂u/∂z)² + (∂v/∂z)²   [from uo(z), vo(z) profiles]
Ri(z) = N²/S²
Kz(z) = 1e-5 + (5e-3 - 1e-5)/(1 + 5·Ri)²    [Pacanowski-Philander]

Kh = 0.1 · Δx · Δy · |S|    [Smagorinsky from velocity gradients]
```

**Step 3 — Predict tidal currents:**
From DFO WebTide constituents at the site, reconstruct u_tide(t), v_tide(t) for each timestep.

**Step 4 — Time integration loop (for each of T timesteps):**

For each particle p at (x_p, y_p, z_p):
a) Interpolate u_eulerian, v_eulerian from Copernicus 3D field at (x_p, y_p, z_p, t) using 4D bilinear interpolation
b) Interpolate u_stokes, v_stokes from Copernicus WAV at (x_p, y_p, t)
c) Add tidal current u_tide(t), v_tide(t)
d) Add windage: u_wind = C_d·u10, v_wind = C_d·v10 (if z_p near surface + W22=True)
e) Add random walk:
   - dx_rand = √(2·Kh·Δt)·N(0,1)
   - dy_rand = √(2·Kh·Δt)·N(0,1)
   - dz_rand = √(2·Kz·Δt)·N(0,1) + (∂Kz/∂z)·Δt
f) RK4 integration step with Δt = 900s
g) Boundary check: beached? exited ROI? reflected at surface/seabed?

**Step 5 — Compute statistics from final positions:**
- All particle trajectories stored
- Dispersion ellipse from covariance matrix
- Residence times
- Connectivity matrix

### Output

```
{
  "trajectories": {
    "type": "geojson",
    "url": "/api/jobs/{id}/result/trajectories.geojson",
    "features": 500,  // one LineString per particle
    "timesteps": 672  // e.g., 28 days hourly
  },

  "particle_density": {
    "type": "grid",
    "grid_shape": [13, 28],
    "values": [[...]],  // probability [0,1] per cell
    "description": "Probability of particle presence per 1/12° grid cell"
  },

  "scalars": {
    "mean_displacement_km": 34.2,
    "max_displacement_km": 89.7,
    "residence_time_10km_hours": 52.3,
    "particles_beached": 13,
    "particles_exited_roi": 67,
    "self_recruitment_pct": 0.73
  },

  "dispersion_ellipse": {
    "major_axis_km": 18.3,
    "minor_axis_km": 7.1,
    "orientation_deg": 225,
    "area_km2": 408,
    "elongation_ratio": 2.58
  },

  "connectivity_matrix": {
    "grid_shape": [13, 28],
    "values": [[...]],  // fraction of particles from source arriving at each destination
    "high_risk_cells": [[44.12, -63.25, 0.32], ...]  // cells with >10% arrival probability
  },

  "displacement_timeseries": {
    "hours": [0, 1, 2, ..., 672],
    "mean_km": [0, 0.3, 0.6, ..., 34.2],
    "std_km": [0, 0.5, 1.0, ..., 12.1],
    "median_km": [0, 0.2, 0.5, ..., 31.8]
  },

  "data_sources": {
    "currents": "Copernicus GLORYS12 + NRT ensemble, 6-hourly, 1/12°",
    "stokes_drift": "Copernicus WAV 3-hourly, 1/12°",
    "tides": "DFO WebTide 10 constituents calibrated to Scotian Shelf",
    "diffusivity": "Pacanowski-Philander from real T,S stratification (mean Kz=3.2×10⁻⁴ m²/s)",
    "bathymetry": "Copernicus static 1/12° (8-266m at site)"
  },

  "figures": {
    "trajectory_map": "/api/jobs/{id}/figures/trajectory_map.png",
    "displacement_plot": "/api/jobs/{id}/figures/displacement.png",
    "connectivity_heatmap": "/api/jobs/{id}/figures/connectivity.png"
  }
}
```

---

## TOOL 4: ACOUSTIC PROPAGATION

**Purpose:** Compute the underwater noise footprint from the windmill.

### Input Variables

| ID | Variable | Source | Usage |
|----|----------|--------|-------|
| 1.1 | `thetao` | GLORYS12 + NRT | Sound speed c(z) via UNESCO eq, absorption α via François-Garrison |
| 1.8 | `so` | GLORYS12 + NRT | Sound speed, absorption |
| 10.1 | Depth | GEBCO | Water depth at source, bottom interaction |
| 8.10 | `ph` | Copernicus BGC | François-Garrison boric acid term |
| 3.1 | `VHM0` | Copernicus WAV | Surface roughness → surface reflection loss |
| 10.4 | Sediment type | NRCan/GSC | Bottom reflection (if available) |
| 4.1 | Wind 10m | ERA5 | Wind-generated ambient noise (Wenz) |
| 11.1 | Vessel density | GFW | Shipping ambient noise |

Plus user parameters: W1-W2 (site), W25-W26 (noise type, frequencies)

### Processing Steps

**Step 1 — Compute sound speed profile c(z):**
At the windmill site, for each month (to capture seasonal variation):
```
For each depth z_k in Copernicus vertical levels:
  T = thetao[site, z_k]
  S = so[site, z_k]
  P = ρ₀·g·z_k / 10000  [dbar]
  c(z_k) = UNESCO_Chen_Millero(T, S, P)
```
Store: summer c(z), winter c(z), annual mean c(z).

**Step 2 — Determine source level:**
Operational (from published measurements, scaled to 15 MW):
```
SL(f) = 130 - 17·log₁₀(f)   [dB re 1μPa @ 1m, per 1 Hz, f in Hz]
SL_1Hz = 130 dB for f ≤ 500 Hz
```
Construction (pile driving, from published measurements):
```
SL_peak = 230 dB re 1μPa @ 1m (8-10m monopile)
SEL_ss = 200 dB re 1μPa²·s @ 1m
SEL_cum = SEL_ss + 10·log₁₀(1500) = 232 dB  [N=1500 strokes]
```

**Step 3 — Compute absorption α(f) at each frequency:**
For each frequency band in W26 (50, 200, 500, 1000 Hz):
```
α(f) = A₁·f²/(f²+f₁²) + A₂·f²/(f²+f₂²) + A₃·f²   [dB/km]
```
Where A₁, f₁ (boric acid), A₂, f₂ (MgSO₄), A₃ (pure water) — all computed from T_avg, S_avg, pH_avg, c_avg at the site's mid-water depth. NOT assumed constants.

**Step 4 — Compute transmission loss on a radial grid:**
For each direction θ (0° to 360°, Δθ=5°) and range r (0 to 50 km, Δr=100m):
```
if r ≤ D:
    TL_geo = 20·log₁₀(r)          [spherical spreading]
else:
    TL_geo = 20·log₁₀(D) + 10·log₁₀(r/D)  [cylindrical beyond depth]

TL_abs = α·r/1000

Surface loss: R_surf = -exp(-0.5·(4π·f·σ_h·sin(θ_g)/c)²)
σ_h = H_s_mean/4  [from real VHM0 data]
TL_surf = -20·log₁₀(|R_surf|)

Bottom loss (if sediment data available):
R_bot = (Z_b·sin(θ_g) - Z_w·sin(θ_t)) / (Z_b·sin(θ_g) + Z_w·sin(θ_t))
TL_bot = -20·log₁₀(|R_bot|)
[If sediment data missing: TL_bot = 3 dB (sandy assumption, flagged)]

TL_total(r,θ,f) = TL_geo + TL_abs + TL_surf + TL_bot
```

**Step 5 — Received level at each point:**
```
RL(r,θ,f) = SL(f) - TL_total(r,θ,f)
```

**Step 6 — Ambient noise:**
```
NL_wind(f) = 50 + 7.5·(U_10_knots)^0.5 - 17·log₁₀(f_kHz)   [Wenz]
NL_ship(f) = 60 + 10·log₁₀(D_ship) - 15·log₁₀(f/100)   [from GFW data]
NL_total(f) = 10·log₁₀(10^(NL_wind/10) + 10^(NL_ship/10))
```
Where U_10_knots from ERA5 wind at site, D_ship from GFW vessel density at site.

**Step 7 — Compute impact metrics:**
- Area ensonified above 160 dB (injury threshold for marine mammals)
- Area ensonified above 140 dB (behavioral response)
- Area ensonified above 120 dB (masking)
- Signal excess: SE(r,θ,f) = RL - NL - DT where DT is species-specific from published audiograms

### Output

```
{
  "sound_speed_profile": {
    "depths_m": [0, 5, 10, 20, 30, 50, 87],
    "summer_c_ms": [1508, 1506, 1495, 1478, 1468, 1462, 1456],
    "winter_c_ms": [1455, 1456, 1458, 1460, 1462, 1464, 1465],
    "annual_mean_c_ms": [1482, 1481, 1477, 1469, 1465, 1463, 1461]
  },

  "absorption": {
    "frequencies_hz": [50, 200, 500, 1000],
    "alpha_db_per_km": [0.18, 1.42, 4.87, 12.3],
    "notes": "Computed from T=8.2°C, S=32.5 PSU, pH=8.05, z=87m at site"
  },

  "noise_levels": {
    "frequencies_hz": [50, 200, 500, 1000],
    "source_level_operational_db": [130, 118, 110, 103],
    "source_level_construction_db": [195, 190, 185, 178],
    "ambient_noise_db": [92, 78, 68, 60]
  },

  "impact_areas": {
    "operational": {
      "radius_160db_km": null,   // Not reached (operational too quiet)
      "radius_140db_km": 0.02,
      "radius_120db_km": 1.8,
      "area_120db_km2": 10.2,
      "radius_above_ambient_km": 3.4
    },
    "construction": {
      "radius_180db_km": 0.5,
      "radius_160db_km": 8.7,
      "radius_140db_km": 25.3,
      "radius_120db_km": 48.2,
      "area_160db_km2": 238
    }
  },

  "species_impact": {
    "north_atlantic_right_whale": {
      "audibility_radius_km": 28.4,
      "behavioral_response_radius_km": 12.1,
      "temporary_threshold_shift_radius_km": 3.2,
      "permanent_threshold_shift_radius_km": 0.8
    },
    "harbour_porpoise": { ... },
    "atlantic_cod": { ... }
  },

  "noise_field": {
    "type": "spatial_grid",
    "url": "/api/jobs/{id}/result/noise_field.json",
    "dimensions": {"range_km": 50, "bearing_deg": 360},
    "frequencies": [50, 200, 500, 1000],
    "values_operational": [[...]],   // RL matrix: 360 bearings × 500 ranges
    "values_construction": [[...]]
  },

  "figures": {
    "noise_map": "/api/jobs/{id}/figures/noise_footprint.png",
    "sound_speed_profile": "/api/jobs/{id}/figures/sound_speed.png",
    "absorption_spectrum": "/api/jobs/{id}/figures/absorption.png"
  }
}
```

---

## TOOL 5: SPECIES EXPOSURE RISK

**Purpose:** Overlay physical footprints with real species occurrence data to quantify ecological risk.

### Input Variables

| ID | Variable | Source | Usage |
|----|----------|--------|-------|
| 9.1 | Species occurrence | OBIS (50k records) | Presence points for SDM |
| 9.2 | Scientific name | OBIS | Species grouping |
| 9.3 | Individual count | OBIS | Abundance weighting |
| 1.1 | `thetao` | GLORYS12 | Environmental covariate for SDM |
| 1.8 | `so` | GLORYS12 | Environmental covariate |
| 10.1 | Bathymetry | GEBCO | Environmental covariate |
| 8.1 | `chl` | Copernicus BGC | Environmental covariate |
| 8.8 | `o2` | Copernicus BGC | Environmental covariate |

Plus outputs from TOOL 2 (wake field), TOOL 4 (noise field), and governance layers (MPA boundaries)

### Processing Steps

**Step 1 — Fit species distribution model:**
Using 50,000 OBIS records + environmental rasters:
- MaxEnt model via `elapid`
- Features: SST mean, SST range, Salinity, Depth, Chlorophyll, Bathymetric slope, SST frontal intensity
- Output: Habitat suitability map (0-1) over 13×28 ROI grid

**Step 2 — For each species group (Cetaceans, Seabirds, Fish, Elasmobranchs, Benthic Invertebrates):**
a) Extract occurrence probability at each grid cell from SDM output
b) Compute exposure = overlap of physical footprint (wake/noise/scour) with species occurrence
c) Apply species-specific sensitivity thresholds from published literature

**Step 3 — Compute risk score:**
```
Risk(x,y) = P(occurrence) × P(exposure|occurrence) × Consequence
           = SDM(x,y) × Overlap(x,y,footprint) × Sensitivity_factor
```
Where:
- SDM(x,y) = habitat suitability from MaxEnt (0-1)
- Overlap = fraction of cell affected by wake/noise/scour/EMF
- Sensitivity_factor = species-specific vulnerability from literature

**Step 4 — Cumulative risk:**
```
Risk_total(x,y) = Σ_species_group w_g · Risk_g(x,y)
```
Weights w_g: equal by default, user-adjustable.

### Output

```
{
  "habitat_suitability": {
    "type": "spatial_grid",
    "url": "/api/jobs/{id}/result/habitat_suitability.json",
    "grid_shape": [13, 28],
    "values": [[0.1, 0.3, 0.05, ...], ...],  // 0-1 per cell
    "auc_score": 0.87,
    "top_predictors": [
      {"variable": "depth", "importance": 0.38},
      {"variable": "sst_mean", "importance": 0.24},
      {"variable": "chl", "importance": 0.18}
    ]
  },

  "species_risk": {
    "cetaceans": {
      "at_risk_cells": 12,
      "mean_risk_score": 0.12,
      "max_risk_score": 0.42,
      "species_present": ["Eubalaena glacialis", "Balaenoptera physalus"],
      "risk_map": [[...]]
    },
    "seabirds": { ... },
    "fish": { ... },
    "elasmobranchs": { ... },
    "benthic_invertebrates": { ... }
  },

  "cumulative_impact": {
    "mean_score": 0.18,
    "max_score": 0.56,
    "breaks_down_as": {
      "noise_contribution_pct": 42,
      "habitat_disturbance_pct": 28,
      "collision_risk_pct": 15,
      "scour_contribution_pct": 10,
      "emf_contribution_pct": 5
    }
  },

  "figures": {
    "habitat_suitability_map": "/api/jobs/{id}/figures/habitat_suitability.png",
    "species_risk_map": "/api/jobs/{id}/figures/species_risk.png",
    "cumulative_impact_map": "/api/jobs/{id}/figures/cumulative_impact.png",
    "response_curves": "/api/jobs/{id}/figures/response_curves.png"
  }
}
```

---

## TOOL 6: MULTI-OBJECTIVE SITING OPTIMIZATION

**Purpose:** Find Pareto-optimal windmill sites across the entire ROI.

### Input Variables

| ID | Variable | Source | Usage |
|----|----------|--------|-------|
| 4.5 | `u100`, `v100` | ERA5 | Wind power density = ½·ρ·u³ at each grid cell |
| 10.1 | Bathymetry | GEBCO | Depth constraint (<60m) |
| 12.1 | MPA boundaries | DFO | Exclusion constraint |
| 12.4 | Lease blocks | CNSOPB | Exclusion constraint |
| 11.1 | Vessel presence | GFW | Shipping conflict objective |
| 11.2 | Fishing effort | GFW | Fishing conflict objective |
| 9.1 | Species occurrence | OBIS → SDM output | Ecological impact objective |

Plus outputs from TOOL 2 (wake field at each candidate site), TOOL 4 (noise impact at each site), TOOL 5 (species risk at each site)

### Processing Steps

**Step 1 — Evaluate energy potential at every grid cell:**
For each of the 364 grid cells in the ROI:
```
E(x,y) = mean_t(½·ρ(t)·v³(t,x,y))
v = √(u100² + v100²) from ERA5 at each grid cell
ρ = p_msl/(R·t2m) from ERA5
```
This uses the actual hourly wind distribution, NOT a Weibull assumption.

**Step 2 — Evaluate ecological impact at every grid cell:**
```
I_eco(x,y) = Risk_total(x,y) from TOOL 5 output
```
If SDM hasn't been run yet, use proxy: I_eco = biodiversity_richness(x,y)×(1-MPA_protection)

**Step 3 — Evaluate human conflict at every grid cell:**
```
I_human(x,y) = w_shipping·Vessel_hours(x,y)/max(Vessel_hours)
             + w_fishing·Fishing_hours(x,y)/max(Fishing_hours)
             + w_shore·(1 - distance_to_shore_km(x,y)/max_distance)
```
All from real GFW + coastline data.

**Step 4 — Apply constraints (hard binary):**
- Depth(x,y) < 60m → feasible, else infeasible
- MPA_fraction(x,y) == 0 → feasible, else infeasible
- Lease_block(x,y) == 0 → feasible, else infeasible
- distance_to_shore > 5km → feasible, else infeasible

**Step 5 — NSGA-II optimization:**
```
Population: 100 individuals (grid cells)
Objectives: [maximize E, minimize I_eco, minimize I_human]
Constraints: feasibility mask
Generations: 200
Crossover: Simulated Binary Crossover (SBX), η_c=20
Mutation: Polynomial Mutation, η_m=20
Selection: Binary tournament with crowding distance
```

**Step 6 — Extract Pareto frontier:**
Non-dominated sorting of final population → Pareto-optimal sites. Rank by crowding distance.

**Step 7 — Compare with user's selected site:**
Where does the user's site (W1, W2) rank in the Pareto set?

### Output

```
{
  "feasible_sites": 247,
  "infeasible_sites": 117,
  "infeasible_reasons": {
    "depth_exceeds_60m": 48,
    "inside_mpa": 23,
    "inside_lease_block": 15,
    "too_close_to_shore": 31
  },

  "pareto_frontier": [
    {
      "rank": 1,
      "sites": [
        {"lon": -63.21, "lat": 44.35, "energy_wm2": 687, "eco_impact": 0.12, "human_conflict": 0.08},
        {"lon": -62.85, "lat": 44.08, "energy_wm2": 652, "eco_impact": 0.09, "human_conflict": 0.14},
        ...
      ]
    }
  ],

  "user_site_ranking": {
    "rank": 34,
    "percentile": 86,
    "energy_percentile": 72,
    "eco_impact_percentile": 45,
    "human_conflict_percentile": 68,
    "summary": "Your site is in the top 14% of feasible sites. It has good wind (72nd percentile) and moderate ecological impact (45th percentile). Consider shifting 3.2 km southeast for a Pareto-optimal alternative with 8% more energy at the same ecological cost."
  },

  "trade_offs": {
    "energy_vs_ecology": [
      {"energy_wm2": 687, "eco_impact": 0.12},
      {"energy_wm2": 612, "eco_impact": 0.08},
      ...
    ],
    "energy_vs_conflict": [...],
    "ecology_vs_conflict": [...]
  },

  "figures": {
    "pareto_map": "/api/jobs/{id}/figures/pareto_sites_map.png",
    "tradeoff_energy_eco": "/api/jobs/{id}/figures/tradeoff_energy_ecology.png",
    "constraint_map": "/api/jobs/{id}/figures/constraints.png"
  }
}
```

---

## TOOL 7: SCOUR ASSESSMENT

### Input Variables

| ID | Variable | Source | Usage |
|----|----------|--------|-------|
| 1.12 | `uo` (near-bed) | GLORYS12 | Bottom current speed |
| 1.13 | `vo` (near-bed) | GLORYS12 | Bottom current speed |
| 3.1 | `VHM0` | Copernicus WAV | Wave height → orbital velocity |
| 3.4 | `VTPK` | Copernicus WAV | Wave period → orbital velocity |
| 10.1 | Depth | GEBCO | Dispersion relation |
| 10.5 | d50 (grain size) | NRCan/GSC | If available: critical shear stress; if not: flag as "missing" |

Plus user parameters: W11-W12 (foundation type, diameter)

### Processing Steps

**Step 1 — Compute bottom orbital velocity from waves:**
```
ω = 2π/T_p
Solve ω² = gk·tanh(kh) for k (Newton-Raphson)
U_orb = π·H_s/(T_p·sinh(kh))
A = U_orb·T_p/(2π)  [orbital excursion]
```

**Step 2 — Compute current shear stress:**
```
τ_c = ρ·C_D·U_bottom²
C_D = [κ/ln(z₀/z_r + 1)]²
z₀ = d50/12  [if d50 known, else flag]
U_bottom = √(uo² + vo²) at deepest Copernicus level at site
```

**Step 3 — Compute wave shear stress:**
```
If d50 known:
  f_w = exp(-5.977 + 5.213·(A/k_s)^(-0.194))  [Swart 1974]
  k_s = 2.5·d50
  τ_w = ½·ρ·f_w·U_orb²
Else:
  f_w default range: 0.01-0.05 (coarse estimate, flagged)
```

**Step 4 — Combined wave-current stress (Soulsby 1997):**
```
τ_mean = τ_c·[1 + 1.2·(τ_w/(τ_c+τ_w))^3.2]
τ_max = √[(τ_mean + τ_w·cos(φ))² + (τ_w·sin(φ))²]
φ = |θ_current - θ_wave|
```

**Step 5 — Scour depth (if d50 available):**
```
KC = U_orb·T_p/D_foundation
Scour_current = 1.3·D_foundation
Scour_wave = 1.3·D_foundation·(1 - exp(-0.03·(KC-6)))  for KC ≥ 6
Scour_combined = Scour_current·(1 - exp(-0.08·(θ_cw/θ_cr - 1)))
```

**If d50 NOT available:** Report τ_c, τ_w, τ_cw, τ_max as time series. Do NOT compute scour depth. Flag as "sediment data missing — shear stress only."

### Output

```
{
  "bottom_stress": {
    "tau_c_mean_Npm2": 0.12,
    "tau_w_mean_Npm2": 0.87,
    "tau_cw_max_Npm2": 2.34,
    "tau_cw_exceeds_critical_pct": 18.3,  // % of time (if d50 known)
    "timeseries_url": "/api/jobs/{id}/result/bottom_stress_ts.json"
  },

  "scour": {
    "computed": false,  // true only if d50 available
    "reason": "Sediment grain size data unavailable for this site (NRCan/GSC maps not covering this cell). Scour depth cannot be estimated — only bottom shear stress is reported."
  },

  "warning": "Scour depth requires sediment grain size data. The Scotian Shelf surficial geology maps from NRCan GSC Open File reports should be obtained for this location to compute scour depth."
}
```

---

## TOOL 8: EMF ASSESSMENT

### Input Variables

| ID | Variable | Source | Usage |
|----|----------|--------|-------|
| 1.12 | `uo` (near-bed) | GLORYS12 | Induced electric field E = v×B |
| 1.13 | `vo` (near-bed) | GLORYS12 | Induced electric field |

Plus user parameters: W13-W15 (cable voltage, current, burial depth), W4 (foundation diameter for cable exit location)

### Processing Steps

**Step 1 — Magnetic field at cable (DC approximation):**
```
B(r) = μ₀·I/(2π·r)   [Biot-Savart, single conductor]
```
For 3-phase AC cable at burial depth d:
```
B_net(r,d) ≈ 3·μ₀·I·s/(4π·r³)   [far-field dipole, s = conductor spacing ~0.075m]
```
At 1m depth: B ≈ 3.15 μT.

**Step 2 — Induced electric field:**
```
E_ind = v·B   [v = bottom current speed from real data]
```
At v = 0.1 m/s, B = 3.15 μT → E_ind = 0.3 μV/m.

**Step 3 — Comparison with thresholds:**
- Earth's magnetic field: 50 μT → B_cable < 50 μT beyond ~0.5m from cable
- Elasmobranch detection threshold: ~0.5 μT (from published EMF sensitivity studies)
- Induced E threshold for behavioral response: ~1 μV/m

### Output

```
{
  "magnetic_field": {
    "cable_burial_depth_m": 2,
    "cable_current_a": 138,
    "B_at_1m_ut": 3.15,
    "B_at_5m_ut": 0.13,
    "B_at_10m_ut": 0.02,
    "distance_to_background_m": 0.48,
    "distance_to_detection_threshold_m": 2.8,
    "notes": "Background = 50 μT (Earth field). Detection threshold = 0.5 μT for elasmobranchs."
  },

  "induced_electric_field": {
    "E_ind_max_uVm": 0.31,
    "E_ind_mean_uVm": 0.08,
    "below_behavioral_threshold": true,
    "behavioral_threshold_uVm": 1.0
  },

  "elasmobranch_risk": {
    "species_present_in_roi": ["Squalus acanthias", "Amblyraja radiata", "Malacoraja senta"],
    "risk_assessment": "LOW — maximum EMF strength at cable is below behavioral response thresholds for all known elasmobranch species. Field drops below detection threshold within 3m of cable."
  }
}
```

---

## TOOL 9: MCMC UNCERTAINTY QUANTIFICATION

**Purpose:** Propagate uncertainty from all inputs through the simulation pipeline to produce credible intervals on all outputs.

### Input Variables

All variables used by TOOLS 1-8, plus:
- Multi-source spread (Copernicus vs HYCOM difference) for each physics variable
- Buoy/CTD validation data for model bias estimation
- OBIS detection uncertainty

### Processing Steps

**Step 1 — Define prior distributions from data:**
```
θ_T ~ Normal(μ_T_data, σ_T_data)   [from GLORYS12 climatology at site]
θ_Hs ~ Weibull(k_data, c_data)     [from WAVERYS 1980-2023 at site]
θ_U ~ Normal(μ_U_data, σ_U_model_spread)  [Copernicus-HYCOM spread]
θ_pH ~ Normal(8.05, 0.05)         [from BGC reanalysis ± uncertainty]
```

**Step 2 — Define likelihood from validation data:**
```
P(buoy_T_obs | θ_T) = Normal(θ_T, σ_obs²)
P(ctd_S_obs | θ_S) = Normal(θ_S, σ_obs²)
```

**Step 3 — MCMC sampling (NUTS via PyMC):**
```
Draw 2000 samples, 4 chains, 1000 tuning steps
Target acceptance rate: 0.95
Check convergence: R-hat < 1.1 for all parameters
```

**Step 4 — Propagate through simulation:**
For each of N=100 posterior samples:
- Run Lagrangian tracking with sampled parameters → N sets of trajectories
- Run acoustic propagation with sampled parameters → N noise fields
- Run species risk with sampled SDM parameters → N risk maps

**Step 5 — Compute credible intervals:**
```
Output_CI_95 = [percentile_2.5, percentile_97.5] across N ensemble members
```

### Output

```
{
  "convergence": {
    "r_hat_max": 1.02,
    "effective_samples_min": 1850,
    "divergences": 0,
    "sampling_time_seconds": 45.2
  },

  "parameter_posteriors": {
    "temperature_C": {"mean": 9.47, "ci95_lower": 9.12, "ci95_upper": 9.82},
    "wave_height_Hs_m": {"mean": 1.92, "ci95_lower": 1.78, "ci95_upper": 2.08},
    "current_speed_ms": {"mean": 0.15, "ci95_lower": 0.11, "ci95_upper": 0.19},
    "diffusivity_Kz_m2s": {"mean": 3.2e-4, "ci95_lower": 1.8e-4, "ci95_upper": 5.6e-4}
  },

  "output_uncertainty": {
    "mean_displacement_km": {"mean": 34.2, "ci95": [28.1, 41.3]},
    "acoustic_impact_area_km2": {"mean": 10.2, "ci95": [7.4, 14.8]},
    "species_risk_score": {"mean": 0.18, "ci95": [0.11, 0.26]},
    "cumulative_impact": {"mean": 0.42, "ci95": [0.29, 0.58]}
  },

  "sensitivity_analysis": {
    "method": "Sobol first-order indices",
    "top_factors": [
      {"parameter": "diffusivity_Kz", "Si": 0.34, "explains": "34% of displacement variance"},
      {"parameter": "current_speed", "Si": 0.28, "explains": "28% of displacement variance"},
      {"parameter": "source_level", "Si": 0.21, "explains": "21% of noise impact variance"}
    ]
  },

  "model_comparison": {
    "method": "Bayesian Model Averaging",
    "weights": {
      "copernicus": 0.58,
      "hycom": 0.42
    },
    "notes": "Weights computed from marginal likelihood vs SMA Halifax buoy observations. Copernicus slightly better fit to buoy currents (RMSE: 0.08 vs 0.11 m/s)."
  },

  "figures": {
    "trace_plot": "/api/jobs/{id}/figures/mcmc_traces.png",
    "posterior_density": "/api/jobs/{id}/figures/posteriors.png",
    "uncertainty_map": "/api/jobs/{id}/figures/uncertainty_spatial.png"
  }
}
```

---

## OUTPUT SUMMARY: WHAT THE CLIENT RECEIVES

After running TOOLS 1-9, the platform assembles:

1. **Baseline Report** — what the environment looks like at the site without the windmill
2. **Physical Footprint Maps** — wake deficit, noise levels, scour potential, EMF
3. **Environmental Response** — particle trajectories, species risk, cumulative impact
4. **Human Conflict Analysis** — shipping lanes, fishing grounds, MPA status
5. **Site Optimization** — your site ranked against all alternatives with trade-off curves
6. **Uncertainty Assessment** — what we're confident about, what needs more data
7. **Data Provenance** — every number traced to its source API, quality flag, and reference

Every number in every output is derived from real data. Every equation parameter is either a universal physical constant or computed from real environmental variables at the specific site and time.
