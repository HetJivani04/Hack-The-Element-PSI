# Frontend-Backend Contract: Lagrangian Particle Tracking

**Tool:** Lagrangian Particle Tracking from windmill site
**Purpose:** Place a windmill, release virtual particles, track where they go under real ocean currents, waves, tides, and wind. See the environmental connectivity footprint.

---

## Workflow: End-to-End (7 Steps)

```
FRONTEND                              BACKEND
────────                              ───────
                                      1. Cube is pre-built (done once, offline)
                                      

2. Frontend loads the page
   → GET /api/region
   ← Region bounds, available dates, 
     variable catalog summary
     
3. User places windmill site on map
   → GET /api/site/validate?lon=-63.45&lat=44.12
   ← Is this location in the data cube?
     What's the water depth here?
     Any MPA conflicts at this coordinate?

4. User opens Lagrangian tool config
   → GET /api/tools/lagrangian_tracking
   ← Tool metadata: required variables,
     optional variables, parameters,
     what output to expect

5. User configures and submits
   → POST /api/jobs
   ← Job queued, job_id returned
   
6. Frontend polls for completion
   → GET /api/jobs/{job_id}
   ← Status updates, then final result
   
7. Frontend renders the result
   (trajectory map, metrics, figures)
```

---

## Step-by-Step API Contract

### Step 2: Frontend Loads Page

**Request:**
```
GET /api/region
```

**Response:**
```json
{
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
```

Frontend uses this to: show the ROI map, set the date picker bounds, populate the variable browser sidebar.

---

### Step 3: User Clicks a Site on the Map

Every time the user moves the pin, the frontend fires:

**Request:**
```
GET /api/site/validate?lon=-63.45&lat=44.12
```

**Response:**
```json
{
  "valid": true,
  "site": {
    "lon": -63.45,
    "lat": 44.12,
    "water_depth_m": 87.3,
    "grid_cell": {"lat_index": 5, "lon_index": 14}
  },
  "data_availability": {
    "in_cube": true,
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
    "inside_mpa": false,
    "nearest_mpa_km": 12.3,
    "nearest_mpa_name": "The Gully Marine Protected Area",
    "inside_lease_block": false
  },
  "data_quality_summary": {
    "physics_3d": "multi-model (Copernicus + HYCOM), buoy 28.4 km away",
    "waves": "3-model ensemble (Copernicus WAV + ERA5 + DWD ICON), buoy 28.4 km away",
    "biogeochemistry": "single-model (Copernicus BGC), nearest CTD 15.7 km away",
    "species": "OBIS records present in this grid cell",
    "sediment": "NOT AVAILABLE for this location"
  }
}
```

Frontend uses this to: show "Site is valid" or warn about data gaps. The sediment missing warning is shown as a yellow alert. The MPA proximity is shown.

---

### Step 4: User Opens Lagrangian Tool

**Request:**
```
GET /api/tools/lagrangian_tracking
```

**Response:**
```json
{
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
      "included_by_default": true
    },
    {
      "variable_id": "3.21",
      "variable_name": "Stokes drift — northward (VSDY)",
      "description": "Wave-driven surface transport.",
      "source": "Copernicus WAV",
      "included_by_default": true
    },
    {
      "variable_id": "4.1",
      "variable_name": "Wind speed at 10m — eastward",
      "description": "Windage effect — wind pushes surface particles ~1-3% of wind speed",
      "source": "ERA5",
      "included_by_default": false
    },
    {
      "variable_id": "6.2",
      "variable_name": "Tidal currents (u/v constituents)",
      "description": "Adds tidal oscillation to particle paths. Important in coastal waters.",
      "source": "DFO WebTide",
      "included_by_default": true
    },
    {
      "variable_id": "2.1",
      "variable_name": "Sea surface height (zos)",
      "description": "Barotropic component — sea level variations drive shelf currents",
      "source": "Copernicus PHY",
      "included_by_default": true
    },
    {
      "variable_id": "2.7",
      "variable_name": "Mixed layer depth (mlotst)",
      "description": "Constrains vertical movement — particles stay within mixed layer",
      "source": "Copernicus PHY",
      "included_by_default": true
    },
    {
      "variable_id": "10.1",
      "variable_name": "Bathymetry",
      "description": "Land boundary — particles reflect off or beach on coastline",
      "source": "GEBCO 2026",
      "included_by_default": true
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
```

Frontend uses this to: build the tool configuration panel. Required variables show as locked checkboxes. Optional variables show as toggles. Parameters show as input fields with validation. The runtime estimate helps set user expectations.

---

### Step 5: User Submits

**Request:**
```
POST /api/jobs
Content-Type: application/json

{
  "tool_id": "lagrangian_tracking",
  "site": {
    "lon": -63.45,
    "lat": 44.12,
    "water_depth_m": 87.3
  },
  "variables": {
    "1.12": true,    // uo — required
    "1.13": true,    // vo — required
    "3.20": true,    // Stokes U — optional, user kept on
    "3.21": true,    // Stokes V
    "6.2": true,     // Tidal currents — optional, user kept on
    "2.1": true,     // SSH — optional, user kept on
    "2.7": true,     // MLD — optional, user kept on
    "10.1": true,    // Bathymetry — optional, user kept on
    "4.1": false,    // Wind 10m — user turned off (release at 50m depth, windage minimal)
    "4.2": false     // Wind 10m — user turned off
  },
  "params": {
    "n_particles": 500,
    "release_depth_m": 10,
    "duration_hours": 168,
    "start_date": "2025-06-15",
    "diffusivity_mode": "auto"
  }
}
```

**Response (immediate):**
```json
{
  "job_id": "lag_7f3a2b91",
  "tool_id": "lagrangian_tracking",
  "tool_name": "Lagrangian Particle Tracking",
  "status": "queued",
  "queued_at": "2026-05-23T20:15:00Z",
  "estimated_runtime_seconds": 30,
  "poll_interval_ms": 2000
}
```

Frontend shows: "Job submitted. Running Lagrangian simulation... 500 particles, 7 days from June 15, 2025. Estimated 30 seconds."

---

### Step 6: Frontend Polls

**Request (every 2 seconds):**
```
GET /api/jobs/lag_7f3a2b91
```

**Response — while running:**
```json
{
  "job_id": "lag_7f3a2b91",
  "status": "running",
  "progress": {
    "timesteps_completed": 84,
    "timesteps_total": 168,
    "percent": 50,
    "particles_active": 487,
    "particles_beached": 13
  }
}
```

Frontend shows a progress bar: "Simulating hour 84 of 168 (50%). 13 particles have beached."

**Response — completed:**
```json
{
  "job_id": "lag_7f3a2b91",
  "status": "completed",
  "runtime_seconds": 28.3,
  "completed_at": "2026-05-23T20:15:28Z",

  "result": {
    "particle_trajectories": {
      "type": "geojson",
      "url": "/api/jobs/lag_7f3a2b91/result/trajectories.geojson",
      "size_kb": 4200,
      "feature_count": 500,
      "timestep_count": 168,
      "description": "LineString features — one per particle. Properties: particle_id, depth_m, timestep. Coordinates: [lon, lat] per timestep."
    },

    "particle_density": {
      "type": "grid",
      "url": "/api/jobs/lag_7f3a2b91/result/density.json",
      "grid_shape": [13, 28],
      "lat_range": [43.68, 44.83],
      "lon_range": [-64.33, -61.94],
      "values": "probability_0_to_1",
      "description": "2D grid of particle presence probability. Value 0.4 means 40% chance a particle passed through this cell."
    },

    "connectivity_matrix": {
      "type": "grid",
      "url": "/api/jobs/lag_7f3a2b91/result/connectivity.json",
      "grid_shape": [13, 28],
      "values": "fraction_0_to_1",
      "description": "What fraction of particles released at the windmill site ended up in each grid cell. Used for: if a spill happened here, which areas are at risk?"
    },

    "scalars": {
      "mean_displacement_km": {
        "value": 34.2,
        "unit": "km",
        "interpretation": "Average distance particles traveled from release site after 7 days"
      },
      "max_displacement_km": {
        "value": 89.7,
        "unit": "km",
        "interpretation": "Furthest particle from release site"
      },
      "residence_time_hours": {
        "value": 52.3,
        "unit": "hours",
        "interpretation": "Median time before particles leave the 10km radius around the site"
      },
      "particles_beached": {
        "value": 13,
        "unit": "count out of 500",
        "interpretation": "13 particles hit the coastline during the 7-day simulation"
      },
      "particles_left_roi": {
        "value": 67,
        "unit": "count out of 500",
        "interpretation": "67 particles exited the ROI boundary"
      }
    },

    "dispersion_ellipse": {
      "type": "time_series",
      "url": "/api/jobs/lag_7f3a2b91/result/dispersion.json",
      "fields": ["hour", "major_axis_km", "minor_axis_km", "angle_degrees"],
      "final_values": {
        "major_axis_km": 18.3,
        "minor_axis_km": 7.1,
        "orientation_deg": 225,
        "interpretation": "After 7 days, the particle cloud is elongated SW-NE (following the shelf current). Major axis = 18.3 km, minor axis = 7.1 km."
      }
    },

    "displacement_timeseries": {
      "type": "time_series",
      "url": "/api/jobs/lag_7f3a2b91/result/displacement_ts.json",
      "fields": ["hour", "mean_km", "std_km", "median_km", "p5_km", "p95_km"]
    },

    "data_sources_used": {
      "currents": "Copernicus PHY 6-hourly + HYCOM 3-hourly ensemble mean. Spread between models: ±4.2 cm/s RMS.",
      "stokes_drift": "Copernicus WAV 3-hourly",
      "tides": "DFO WebTide — 10 harmonic constituents fitted to Scotian Shelf tide gauges",
      "diffusivity": "Auto-computed from stratification (N²) at site. Mean Kz = 3.2×10⁻⁴ m²/s in mixed layer, 8.7×10⁻⁵ m²/s below.",
      "bathymetry": "GEBCO 2026",
      "quality_notes": [
        "Windage excluded (user turned off) — surface drift may be underestimated for buoyant particles",
        "Tidal currents from WebTide harmonic prediction — actual tide may differ from prediction",
        "Diffusivity from K-profile parameterization — not direct turbulence measurements"
      ]
    },

    "figures": {
      "trajectory_map": {
        "url": "/api/jobs/lag_7f3a2b91/figures/trajectory_map.png",
        "width": 1200,
        "height": 800,
        "description": "500 particle trajectories (white lines) overlaid on GEBCO bathymetry (blue gradient). Windmill site marked as red circle. Beached particles shown as orange dots. Coastline in black."
      },
      "displacement_plot": {
        "url": "/api/jobs/lag_7f3a2b91/figures/displacement_plot.png",
        "width": 800,
        "height": 500,
        "description": "Mean displacement (km) vs time (hours). Blue line = mean, shaded = ±1σ, dashed = median. Shows particles dispersing over time."
      },
      "connectivity_heatmap": {
        "url": "/api/jobs/lag_7f3a2b91/figures/connectivity.png",
        "width": 1200,
        "height": 800,
        "description": "Heatmap of connectivity — red cells = high probability of particles arriving from the windmill site. Shows downstream connectivity pathways."
      }
    }
  }
}
```

---

### What the Backend Actually Did (Step by Step)

Between receiving the job and returning the result:

1. **Validate:** Checked that lon=-63.45, lat=44.12 is inside the cube and all 7 selected variables exist at that location.

2. **Extract from cube:** Pulled 168 hourly timesteps of 3D velocity fields (uo, vo), wave fields (Stokes drift), SSH, and MLD — all from the pre-fused Zarr cube. Extracted bathymetry.

3. **Compute stratification:** Used the real T and S profiles at the site to compute N²(z) at each timestep, then Kz from K-profile parameterization. All from real data, nothing assumed.

4. **Predict tides:** DFO WebTide harmonic constituents predicted tidal currents at the site for June 15–22, 2025. Pure physics from real harmonic constants.

5. **Initialize particles:** 500 particles placed at (lon=-63.45, lat=44.12, depth=10m) at timestep 0.

6. **Integrate (168 hourly steps):**
   - At each hour, for each particle: interpolate u, v from the 3D velocity field at the particle's exact position → add Stokes drift at surface layer → add tidal current → add random walk from Kz → RK4 step → check bathymetry (beach if on land)
   - 500 particles × 168 steps = 84,000 position updates. Parallelized over 4 threads.

7. **Compute statistics:** Mean displacement, max displacement, residence time, dispersion ellipse, connectivity matrix, particle density field.

8. **Generate figures:** Matplotlib renders trajectory map, displacement plot, connectivity heatmap → saved as PNGs.

9. **Write GeoJSON:** All 500 particle trajectories written as LineString features with metadata.

10. **Return result:** All URLs, scalars, and metadata packaged into the response above.

---

### Step 7: Frontend Renders

Frontend receives the above JSON. What they show:

**Map view (main):**
- Leaflet/Mapbox map centered on the ROI
- GEBCO bathymetry as a blue gradient tile layer
- Particle trajectories rendered from the GeoJSON URL as animated polylines
- Windmill site as a red marker
- Particle density as a semi-transparent heatmap overlay
- Controls: play/pause animation, time slider (hour 0–168), speed toggle

**Side panel — Key Numbers:**
- Mean displacement: 34.2 km
- Max displacement: 89.7 km
- Residence time: 52.3 hours
- Particles beached: 13
- Particles left ROI: 67

**Side panel — Data Provenance (collapsible):**
- "Currents from Copernicus + HYCOM ensemble (spread: ±4.2 cm/s)"
- "Tides from DFO WebTide harmonic prediction"
- "Diffusivity auto-computed from real stratification"
- "Windage excluded (user choice) — surface drift may be underestimated"

**Side panel — Figures (clickable thumbnails):**
- Trajectory map (PNG)
- Displacement vs time plot (PNG)
- Connectivity heatmap (PNG)

---

### Summary: What the Frontend Team Needs to Build

**Against this API, the frontend needs 4 pages/views:**

| View | API Call(s) | What It Shows |
|------|------------|---------------|
| **Region setup** | `GET /api/region` | ROI map with bounds, available date range, variable browser |
| **Site pin** | `GET /api/site/validate` | Validates location on click, shows depth/MPA/data quality |
| **Tool config** | `GET /api/tools/{tool_id}` | Required/optional variable toggles, parameter inputs, runtime estimate |
| **Results** | `GET /api/jobs/{job_id}` (poll) | Map with GeoJSON overlay, scalar cards, figure thumbnails, data provenance |

**Everything they render comes from the API response. They never touch the data cube, run computation, or know about Copernicus/HYCOM.**
