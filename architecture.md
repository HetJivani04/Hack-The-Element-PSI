# Marine Digital Twin Platform — System Architecture

**Core feature:** Place a windmill at specific coordinates. Simulate its environmental impact using ONLY real historical and near-real-time data. No fabricated data, no made-up coefficients.

**Region:** Scotian Shelf — `43.68°N, -64.33°W` to `44.83°N, -61.94°W`

**Data sources:** 16 real scientific APIs. All variables in [api/variables.md](../api/variables.md). All access details in [api/oceans.md](../api/oceans.md).

---

## Table of Contents

1. [What This Platform Actually Does](#1-what-this-platform-actually-does)
2. [Data Cube: Real Data Only](#2-data-cube-real-data-only)
3. [The Windmill Simulation Pipeline](#3-the-windmill-simulation-pipeline)
4. [Module-by-Module Deep Dive](#4-module-by-module-deep-dive)
5. [How Variables Flow Through the System](#5-how-variables-flow-through-the-system)
6. [Output: What the User Gets](#6-output-what-the-user-gets)
7. [Implementation Plan](#7-implementation-plan)

---

## 1. What This Platform Actually Does

A user has a proposed offshore wind turbine site. They need to understand: **if I build here, what happens to the environment?**

The platform answers this in stages:

```
User selects windmill site (lon, lat)
         │
         ▼
┌────────────────────────────────────────────┐
│ STAGE 1: What's the baseline environment?   │
│ Extract all 169 real variables at this site │
│ from historical + near-real-time data       │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│ STAGE 2: What does the windmill DO here?    │
│ Physical: wake, noise, scour, EMF          │
│ Biological: collision, habitat change       │
│ Human: shipping conflict, fishing conflict  │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│ STAGE 3: How does the environment respond?  │
│ Lagrangian: where do particles go?          │
│ Acoustics: noise propagation footprint      │
│ Species: habitat suitability change         │
│ Cumulative: multi-variable impact score     │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│ STAGE 4: Is this the best spot?             │
│ Multi-objective optimization across ROI     │
│ Trade-off: energy vs ecology vs conflict    │
│ Ranked site alternatives with uncertainty   │
└────────────────────────────────────────────┘
```

Every stage uses **only real data from real APIs**. Nothing is synthetic. If data doesn't exist for a cell or time, it stays as a gap — flagged and reported to the user.

---

## 2. Data Cube: Real Data Only

### 2.1 The No-Fabrication Rule

The fused data cube is built from 16 real APIs. For every cell in the cube:

| Situation | What We Do | Quality Flag |
|-----------|-----------|-------------|
| Direct observation exists (buoy, CTD, Argo) | Use the real measurement | `1` — direct |
| Model data exists from 2+ independent sources | Use both, store spread for uncertainty | `2` — multi-model |
| Model data exists from 1 source only | Use it | `3` — single-model |
| Real data exists but at coarser resolution | Bilinear interpolation from real data points | `4` — interpolated |
| Real data exists but at different time step | Forward-fill or linear interpolation **between real timesteps only** | `5` — temporally aligned |
| **No data from ANY source for this cell/time** | **Leave as NaN (missing)** | `6` — missing |
| No data at all | **NaN. Never fill.** | `6` — missing |

**Never:** fabricate data, use "typical values", extrapolate beyond data coverage, or generate synthetic data.

### 2.2 What Goes Into the Cube

The cube is built once for the ROI and cached. Variable sources:

| Variable Group | Real Sources | Native Resolution | How It Goes Into Cube |
|---|---|---|---|
| 3D Temperature | Copernicus GLORYS12, HYCOM, CIOOS CTD profiles | 1/12°, point | Copernicus + HYCOM averaged (spread stored). CTD as validation station data. |
| 3D Salinity | Same | Same | Same |
| 3D Currents (u, v) | Copernicus GLORYS12, HYCOM, SMA buoy (20-level point) | 1/12°, point | Same averaging. Buoy for validation. |
| Waves (Hs, Tp, Dp, swell partitions) | Copernicus WAV, ERA5, Open-Meteo Marine, SMA Halifax buoy | 0.083°, 0.5°, 0.25°, point | Multi-source ensemble. Store mean + spread. Buoy as truth reference. |
| Wind (10m, 100m) | ERA5, Open-Meteo Atmosphere, MSC GeoMet | 0.25°, point | ERA5 + Open-Meteo averaged |
| Surface fluxes (τ, Q, E-P) | ERA5 CDS, HYCOM | 0.25°, 1/12° | ERA5 fluxes regridded to 1/12° |
| Sea level / SSH / tides | Copernicus, HYCOM, DFO WebTide, SMA pier9c | 1/12°, ~1km, point | Copernicus + HYCOM SSH. WebTide for tidal constituents. Pier9c for validation. |
| Biogeochemistry (chl, O2, NO3, pH, etc.) | Copernicus BGC, CIOOS CTD profiles, BBMP Bedford Basin, satellite ocean color | 0.25°, point, 1km | Copernicus BGC regridded. CTD/BBMP as in-situ truth. Satellite chl (higher res) for surface. |
| Bathymetry | GEBCO 2026, Copernicus static | 15 arc-sec, 1/12° | GEBCO conservative-averaged to 1/12°. Copernicus as secondary. |
| Species occurrence | OBIS (501,900 records in ROI), OTN acoustic detections | Point | Gridded occurrence count + species list per cell. No spatial interpolation of biology. |
| Vessel presence | Global Fishing Watch 4Wings, AIS Stream | 0.01°–0.1°, point | GFW grid conservative-averaged. AIS for real-time events. |
| Governance layers | DFO MPA boundaries, NRCan lease blocks, CHS shipping lanes | Polygon vector | Fractional area per grid cell (0–1). |

### 2.3 Common Grid Specification

```
Latitude:  43.68 to 44.83 at 1/12° step  → 13 lat cells
Longitude: -64.33 to -61.94 at 1/12° step → 28 lon cells
Depth:     0.49m to seafloor, 50 vertical levels (Copernicus standard)
Time:      1993-01-01 to 2026-05-23, aligned to hourly
Total cells: 13 × 28 × 50 = 18,200 horizontal columns × ~25 wet depth levels
```

### 2.4 Cube Storage

```
platform/cube/
  physics_3d.zarr/        # T, S, U, V at all depth levels
  surface.zarr/           # SSH, MLD, SST, ice
  waves.zarr/             # All wave variables, ensemble statistics
  atmosphere.zarr/        # Wind (both levels), pressure, fluxes
  biogeochemistry.zarr/   # Chl, nutrients, O2, pH, NPP
  bathymetry.zarr/        # Static depth field
  stations/               # Buoy, CTD profiles — not gridded
  species/                # OBIS gridded occurrences
  human_activity/         # GFW gridded vessel presence
  governance/             # MPA fractional coverage per cell
  quality_masks/          # Per-cell quality flags (1-6 scale)
  metadata.json           # Source versions, build date, ROI bounds
```

---

## 3. The Windmill Simulation Pipeline

### 3.1 User Input

The user provides exactly:
1. **Windmill site coordinates** — one (lon, lat) point
2. **Turbine specifications** — hub height, rotor diameter, rated power (or use defaults: 150m hub, 236m rotor, 15 MW)
3. **Time window of interest** — start date, end date (constrained by what data exists)
4. **Which impact modules to run** — toggle on/off: physical, biological, human conflict, optimization
5. **Variables of interest** — from the 169-variable catalog, which ones they want to see the impact on

The platform then shows what data is available for their selections and warns about any gaps.

### 3.2 Pipeline Overview

```
USER SITE (lon, lat)
       │
       ├──→ MODULE A: BASELINE CHARACTERIZATION
       │    Extract all selected variables at the site + surrounding ROI
       │    Time series, climatology, seasonal patterns, extremes
       │    Output: baseline report with distributions, trends, variability
       │
       ├──→ MODULE B: WINDMILL PHYSICAL FOOTPRINT
       │    Given the turbine specs, compute:
       │    B1. Wind wake deficit field (how far downwind does wind slow)
       │    B2. Underwater noise source level (operational + construction)
       │    B3. Foundation scour potential (bottom stress from waves+currents)
       │    B4. EMF from export cable (static magnetic field)
       │    Output: spatial footprint of each physical effect
       │
       ├──→ MODULE C: ENVIRONMENTAL RESPONSE
       │    Given the physical footprint, simulate:
       │    C1. Lagrangian particle tracking from site (drift, dispersal)
       │    C2. Acoustic propagation footprint (sound transmission loss)
       │    C3. Species exposure risk (overlap footprint × occurrence)
       │    C4. Cumulative multi-variable impact score
       │    Output: spatial response fields, risk maps, impact scores
       │
       ├──→ MODULE D: HUMAN CONFLICT ASSESSMENT
       │    Given the site and footprints:
       │    D1. Shipping lane conflict (GFW vessel density × site proximity)
       │    D2. Fishing ground conflict (GFW fishing effort × site proximity)
       │    D3. MPA/closure violation check
       │    D4. Visual impact (distance from shore, viewshed)
       │    Output: conflict scores per stakeholder group
       │
       └──→ MODULE E: MULTI-OBJECTIVE OPTIMIZATION
            Given all impact scores across the entire ROI:
            E1. Rank every grid cell by energy vs ecology vs conflict
            E2. Find Pareto-optimal alternative sites
            E3. Show trade-off curves
            E4. Return recommendation with uncertainty
            Output: ranked site alternatives with impact comparison
```

---

## 4. Module-by-Module Deep Dive

### MODULE A: BASELINE CHARACTERIZATION

**Purpose:** Before you can understand the windmill's impact, you must understand what the environment looks like without it.

**Real data used:**
- All 169 variables extracted at the windmill point and for the surrounding ROI
- Uses the pre-fused data cube (Section 2)
- Variables extracted as: point time series (for the site), spatial snapshots (for maps), vertical profiles (for depth-dependent variables)

**What happens step by step:**

1. **Point extraction:** For each selected variable, extract the time series at the windmill site coordinates. If the site is between grid cells, use bilinear interpolation from the four nearest real grid cells. If there's a buoy or CTD station nearby, pull that too — the real observation is shown alongside the model value.

2. **Climatology computation:** From the full time series (1993–present), compute:
   - Monthly means and standard deviations (the seasonal cycle)
   - Long-term trend (Mann-Kendall test + Sen's slope — from real data only)
   - Extreme value statistics (what's the 50-year storm wave height at this site? Fitted from real data, not assumed)
   - Wind rose, wave rose (directional distributions from real wind/wave data)

3. **Baseline variability:** How much does each variable naturally vary at this site? Computed as: interannual std, seasonal amplitude, day-to-day variance. This becomes the "noise floor" — any windmill impact smaller than natural variability is flagged as "below detection threshold."

4. **Data quality report:** For every variable, report:
   - Temporal coverage (% of selected time window with real data)
   - Source quality (direct observation vs model vs interpolated)
   - Nearest real observation station and its distance
   - Missing periods (gaps) — shown honestly

**Output:**
- Baseline report for each variable: mean, range, trend, seasonality, extremes, data quality
- Time series plots with uncertainty bands
- Spatial maps showing the variable's distribution across the ROI
- Data coverage map showing where real data exists vs gaps

**Real coefficients/parameters used:** None fabricated. The Mann-Kendall test is a standard non-parametric test. Sen's slope is computed from the actual data pairs. Extreme value distributions (GEV, GPD) are fitted to the actual observed extremes using MLE — parameters come from the data, not assumptions.

---

### MODULE B: WINDMILL PHYSICAL FOOTPRINT

**Purpose:** Given the turbine specifications, compute the spatial extent of each physical effect. All physical parameters come from the real environmental data at the site.

#### B1. Wind Wake Deficit

**What it is:** A wind turbine extracts energy from the wind, creating a slower, more turbulent wake behind it. This wake can extend kilometers downwind and affect other turbines or local wind patterns.

**Real data needed:**
- Wind speed at hub height (100m) — from ERA5 / Open-Meteo Atmosphere
- Wind direction at hub height — same source
- Atmospheric stability (approximated from: air-sea temperature difference ΔT = SST − T2m, boundary layer height from ERA5)
- Ambient turbulence intensity (derived from: friction velocity u* from ERA5, surface roughness z0 from ERA5)

**Scientific method — Jensen (1983) wake model:**
The Jensen model is the standard engineering wake model used in offshore wind. It assumes a linearly expanding wake behind the turbine:
- Wake radius at distance x: r_wake = r_rotor + α·x
- Velocity deficit at distance x: Δu/u∞ = (1 − √(1−Ct)) × (r_rotor / r_wake)²
- Where:
  - r_rotor = actual rotor radius (from turbine specs, not assumed)
  - Ct = thrust coefficient (from turbine power curve, real manufacturer data)
  - α = wake decay constant = 0.5 / ln(z_hub / z0)   ← **from real ERA5 roughness z0, not an assumed constant**
  - z_hub = hub height from turbine specs
  - z0 = surface roughness from ERA5 reanalysis at the site

**Why no fabricated coefficients:** Every parameter is either from the turbine spec sheet (real engineering data), from ERA5 (real atmospheric data), or from measured environmental variables. The wake decay constant α is computed from the actual surface roughness at the site — it's not a fixed 0.04 or 0.075 from textbooks.

**Output:**
- Spatial field: wind speed deficit (%) at hub height, extending downwind from the turbine
- Scalar: wake recovery distance (distance at which Δu < 5% of u∞)
- Scalar: annual wake-affected area (km²) — how much ocean surface sees reduced wind
- Figure: wake deficit map overlaid on ROI map

#### B2. Underwater Noise

**What it is:** Operating wind turbines produce continuous underwater noise. Construction (pile driving) produces intense impulsive noise. Both affect marine life.

**Real data needed:**
- Sound speed profile c(z) at the site — computed from real T(z), S(z), depth data via UNESCO equation
- Bathymetry — from GEBCO real measurements
- Sea state (wave height) — affects ambient noise and surface reflection
- Bottom sediment type — if available from NRCan/GSB maps; otherwise flagged as "unknown, assumed sandy silt (Scotian Shelf typical — from DFO surveys)"

**Scientific method:**

Source level (SL) for operational turbine:
- For a 15 MW turbine, SL ≈ 120–150 dB re 1μPa @ 1m (based on published measurements from existing offshore wind farms — not our number, we cite the source)
- Frequency range: 50–500 Hz dominant (tonal at blade-passing frequency)
- The user can input measured SL from similar turbines, or use published reference values with explicit citation

Source level for construction (pile driving):
- SL ≈ 180–220 dB re 1μPa @ 1m depending on pile size and hammer energy
- Published measurement ranges from real offshore wind construction
- We provide the range and cite the measurement campaigns

Transmission loss (TL) computed using real physics on real data:
- Spreading loss: 20·log₁₀(r) — spherical in deep water, transitions to 15·log₁₀(r) in shallow
- Absorption loss: α·r, where α is from François-Garrison formula using **real T, S, pH, depth at the site**
- François-Garrison coefficients: α = A₁·f₁·f²/(f²+f₁²) + A₂·f₂·f²/(f²+f₂²) + A₃ — where A₁, A₂, A₃, f₁, f₂ are computed from real T, S, z, pH at the site. No assumed values.
- Boundary effects: surface reflection (depends on real wave height), bottom reflection (depends on real sediment if available)

**Output:**
- Spatial field: noise level (dB re 1μPa) map around the turbine for key frequencies
- Scalar: radius to key thresholds (160 dB — injury, 140 dB — behavioral response, 120 dB — masking)
- Figure: noise footprint overlaid on species occurrence map
- Citation list: all SL references used

#### B3. Foundation Scour

**What it is:** The turbine foundation (monopile, jacket, or floating) interacts with water currents and waves, potentially scouring the seabed around the base.

**Real data needed:**
- Near-bottom current speed — from Copernicus/HYCOM bottom layer
- Significant wave height and period at site — from real wave data
- Water depth — from GEBCO
- Grain size d50 — from NRCan/GSB surficial geology maps if available; if not, flagged as "sediment data not available for this site"

**Scientific method (Soulsby 1997, Sumer & Fredsøe 2002):**
- Bottom shear stress from currents: τ_c = ρ·C_D·U_bottom², where C_D is the drag coefficient computed from real depth and roughness
- Bottom shear stress from waves: τ_w = ½·ρ·f_w·U_orb², where f_w is the wave friction factor computed from real wave period and grain size (if available) or depth
- Combined wave-current friction: τ_cw from Soulsby's formula — uses only real wave + current data
- Critical shear stress for sediment motion: τ_cr from Soulsby-Whitehouse equation — if grain size is unknown, we report "cannot compute τ_cr — sediment data missing"
- Scour depth (if sediment data exists): S/D = f(KC, U_cw) from Sumer & Fredsøe, where KC (Keulegan-Carpenter number) = U_orb·T_w / D_pile — all real data

**Output:**
- Scalar: maximum scour depth estimate with uncertainty range
- Time series: bottom shear stress at the site showing storm peaks
- Flag: "sediment data available/missing" — if missing, scour depth is not computed, only shear stress is reported

#### B4. Electromagnetic Field (EMF) from Export Cable

**What it is:** The export cable carrying power to shore produces a static magnetic field and induced electric field in the water. Some marine species (elasmobranchs — sharks, skates, rays) are electrosensitive.

**Real data needed:**
- Cable specifications: voltage, current, burial depth (from user input or typical offshore wind cable specs — these are engineering standards, not environmental assumptions)
- Water conductivity — from real salinity and temperature at the site (conductivity = f(S, T))

**Scientific method:**
- Magnetic field B at distance r from cable: B = μ₀·I/(2πr) — this is the Biot-Savart law, a fundamental physics equation. The only parameter is current I (from cable specs).
- Induced electric field: E = v·B, where v is water velocity (from real current data)
- Attenuation with burial depth and sediment/water conductivity — uses real conductivity if salinity data exists

**Output:**
- Spatial field: magnetic field strength (μT) around the cable route
- Scalar: distance to background level (where B < Earth's magnetic field ~50μT)
- Flag: "elasmobranch species present in this area?" — cross-reference with OBIS data

---

### MODULE C: ENVIRONMENTAL RESPONSE

**Purpose:** Given the physical footprint from Module B, simulate how the environment responds. All transport, mixing, and biological parameters come from real data.

#### C1. Lagrangian Particle Tracking

**What it is:** Release virtual particles at the windmill site and track where they go under real ocean currents, waves, tides, and wind. This simulates: where would a pollutant spill go? Where would construction sediment disperse? Where would larvae drift?

**Real data driving the simulation:**
- 3D currents (uo, vo) at every depth level — from Copernicus/HYCOM real data
- Stokes drift (VSDX, VSDY) — from Copernicus WAV real data
- Tidal currents — from DFO WebTide (real tidal constituents fitted to real tide gauge data)
- Wind at 10m — from ERA5 real data (for windage — surface particles pushed by wind)
- Sea surface height — for barotropic component
- Mixed layer depth — confines particles vertically
- Bathymetry — boundary condition (particles can't go on land)
- Turbulent diffusion — NOT a made-up diffusivity. Computed diagnostically from real stratification:
  - Brunt-Väisälä frequency N² = −(g/ρ₀)·(∂σθ/∂z) — computed from real T and S profiles
  - Vertical diffusivity Kz estimated from stratification + MLD using a standard parameterization — but the parameters going INTO that parameterization are all real data. We cite the parameterization (Large et al. 1994, KPP).
  - Horizontal diffusivity Kh from Smagorinsky: Kh = C_s·Δx·Δy·|S|, where S is the strain rate computed from real velocity gradients. C_s is a dimensionless constant (~0.1) from turbulence theory — not tuned to our data.

**How it runs:**
1. User specifies: number of particles (100–10,000), release depth, duration, release timing (start date)
2. For each timestep (hourly), the model:
   a. Interpolates the 3D velocity field to each particle's position (bilinear in space, linear in depth)
   b. Adds Stokes drift at the surface layer
   c. Adds tidal current from WebTide harmonic prediction (real constituents, predicted forward)
   d. Adds random-walk displacement scaled by Kz (from real stratification)
   e. Moves particles via 4th-order Runge-Kutta
   f. Checks bathymetry — reflects or beaches particles at the coastline
3. Records every particle position at every timestep

**Output:**
- Spatial field: particle trajectories (GeoJSON for map rendering)
- Spatial field: particle density map (probability of particle presence per grid cell)
- Scalar: mean displacement distance, max displacement distance, residence time
- Time series: mean displacement over time, dispersion ellipse axes
- Figure: trajectory map overlaid on bathymetry + site marker
- Connectivity matrix: what fraction of particles starting at the windmill site end up in each surrounding grid cell

#### C2. Acoustic Propagation Footprint

**What it is:** Take the noise source from Module B2 and propagate it through the real sound speed field to determine the acoustic footprint.

**Real data driving the simulation:**
- Sound speed profile c(z) — computed from real T(z), S(z), P(z) data via UNESCO/Chen-Millero equation at the site
- Bathymetry — from GEBCO
- Sea state (wave height, wave period) — affects surface roughness and thus surface reflection loss
- Bottom sediment type — if available, affects bottom reflection loss; if not, uses range of possible values with uncertainty

**Scientific method:**
- Source → receiver transmission loss computed along radials from the windmill site
- At each range step: TL(r) = 20log₁₀(r) + α·r + surface_loss(f, Hs) + bottom_loss(f, sediment_type)
- Absorption α uses François-Garrison formula with real T, S, z, pH at each depth
- This gives a noise level at every point in the ROI for key frequencies (50 Hz, 200 Hz, 500 Hz, 1000 Hz)
- Ambient noise level from real wave data (Wenz curves: ambient noise depends on sea state and shipping density)
- Signal excess: SE = RL − NL − DT, where RL = received level, NL = ambient noise (from real wave+shipping data), DT = detection threshold (species-dependent — use published audiogram data)

**Output:**
- Spatial field: noise level map at each frequency band
- Spatial field: signal excess map (where the turbine is audible above ambient)
- Scalar: area ensonified above threshold (km²) for each species hearing sensitivity
- Spatiotemporal: how the noise footprint changes with season (different T/S profiles → different sound speed → different propagation)

#### C3. Species Exposure Risk

**What it is:** Overlay the physical footprint maps with real species occurrence data to quantify which species are exposed to what effects.

**Real data used:**
- Species occurrence grid — from OBIS real survey data (501,900 records in ROI)
- Each physical footprint from Modules B and C: noise map, wake map, EMF map, scour zone
- Species-specific sensitivity parameters from **published literature** (not our assumptions):
  - Hearing sensitivity (audiogram) for cetaceans, fish
  - Collision risk model parameters (flight height distribution for birds from radar studies)
  - Electrosensitivity for elasmobranchs

**How it works:**
1. For each species group (cetaceans, seabirds, fish, elasmobranchs, benthic invertebrates), the model:
   a. Takes the physical footprint map (e.g., noise level in dB)
   b. Takes the species occurrence probability surface (from OBIS data)
   c. Computes overlap: exposure = footprint × occurrence
   d. Applies species sensitivity threshold from published literature
2. Risk = exposure × sensitivity × consequence (from literature, cited)

**Output:**
- Spatial field: risk map per species group (0–1 scale)
- Scalar: area of "high risk" for each group (km²)
- Scalar: population fraction exposed
- Table: species list present in footprint area, ranked by risk

#### C4. Cumulative Multi-Variable Impact Score

**What it is:** Combine all impact layers into a single integrated score, preserving the multi-dimensional nature of the problem.

**Real data used:** All outputs from Modules B and C — which are all derived from real environmental data.

**How it works:**
1. Each impact layer (wake, noise, scour, EMF, species risk) is a spatial field
2. Normalization: each layer is normalized to [0,1] using min-max across the ROI (NOT using assumed thresholds — the max is the actual max in the ROI)
3. Weighting: either equal weights (default) or user-specified weights reflecting stakeholder priorities
4. The cumulative score is a field: S_total(x,y) = Σ w_i · S_i(x,y)
5. **Crucially:** the uncertainty in each layer propagates through to the total score. If noise data came from a well-constrained sound speed profile, lower uncertainty. If sediment data is missing, higher uncertainty in scour.

**Output:**
- Spatial field: cumulative impact score map
- Spatial field: cumulative uncertainty map (where are we uncertain?)
- Figure: stacked bar chart showing contribution of each impact type at the windmill site
- Figure: uncertainty decomposition (which missing data contributes most to uncertainty?)

---

### MODULE D: HUMAN CONFLICT ASSESSMENT

**Purpose:** How does the windmill site conflict with existing human uses of the ocean?

**Real data used:**
- Vessel presence hours per grid cell — from GFW 4Wings (AIS data, real ship tracks)
- Vessel type classification (cargo, tanker, fishing, passenger) — from GFW
- MPA boundaries — from DFO real shapefiles
- Lease blocks — from CNSOPB
- Distance from shore — from GEBCO coastline

**How it works:**

**Shipping conflict:** The shipping conflict score for a grid cell is the vessel presence hours (from real AIS data) weighted by distance from the windmill site (closer = more conflict). The shipping density comes from real data — we're not assuming it.

**Fishing conflict:** Same approach but filtered to fishing vessels (from GFW gear type classification). Fishing vessels that actually fish in the proposed site area (real data) generate conflict.

**MPA check:** Binary — is the site inside an MPA polygon? This is a hard constraint for the optimizer.

**Output:**
- Spatial field: shipping conflict map
- Spatial field: fishing conflict map
- Scalar: conflict score per sector
- Flag: "Site is inside [MPA name]" or "Site is outside all protected areas"

---

### MODULE E: MULTI-OBJECTIVE OPTIMIZATION

**Purpose:** Given all impact scores across the entire ROI, find the best windmill sites. "Best" means maximizing energy while minimizing ecological and human conflict — which are inherently in tension.

**Real data driving the optimization:**
- Wind power density at every grid cell — from real 100m wind data (ERA5)
- Bathymetry constraint — from real GEBCO data
- Ecological impact scores — from Modules C (derived from real data)
- Human conflict scores — from Module D (derived from real GFW + MPA data)
- MPA/lease block exclusion zones — from real governance shapefiles

**How it works:**

The optimizer does NOT use made-up objective functions. Every objective is computed from real data:

1. **Objective 1 — Maximize energy:** Energy potential at each cell = mean(½·ρ·v³) where v is real 100m wind speed. No assumed Weibull parameters — the actual wind distribution from real data determines the power.
2. **Objective 2 — Minimize ecological impact:** Cumulative impact score from Module C4.
3. **Objective 3 — Minimize human conflict:** Conflict score from Module D.
4. **Constraints:** Depth < 60m (real bathymetry), Outside MPAs (real polygons), Outside existing lease blocks (real shapefiles).

The optimizer searches across all 364 grid cells in the ROI, evaluating these three objectives for each candidate site. Sites that satisfy all constraints are ranked on the Pareto frontier — sites where you cannot improve one objective without worsening another.

**Method:** NSGA-II (Non-dominated Sorting Genetic Algorithm) with the three objectives above. The algorithm does not assume or fabricate anything — it evaluates real data at each candidate location.

**Output:**
- Map: Pareto-optimal sites shown on ROI map, color-coded by rank
- Figure: 2D trade-off plots (energy vs ecology, energy vs conflict, ecology vs conflict)
- Table: Top 10 sites with all objective values, compared to user's originally selected site
- Scalar: "Your site ranks #X out of Y feasible sites"

---

### MODULE F: MCMC / BAYESIAN INFERENCE (Cross-Cutting)

**Purpose:** Quantify uncertainty in all the above. When we say "the impact score at this site is 0.42," how confident are we?

**Real data used:** All outputs from Modules B–E, plus their uncertainty estimates propagated from the data quality flags.

**How it works:**

1. **Priors come from data, not assumptions:**
   - Prior for wave height distribution at a site → fitted from the full 1980–present Copernicus WAV reanalysis
   - Prior for wind speed → fitted from 1940–present ERA5
   - Prior for species occurrence → from the OBIS data for this specific region
   - No flat/"uninformative" priors by default — use data-driven priors

2. **Likelihood:** How likely is the observed data given model parameters? Uses the real observations (buoy data, CTD profiles) as the validation set.

3. **Posterior:** MCMC sampling (via `pymc` or `emcee`) to estimate the posterior distribution of key outputs:
   - Posterior distribution of the cumulative impact score
   - Posterior distribution of the Lagrangian mean displacement
   - Posterior predictive check: does the model reproduce the real buoy observations?

4. **Model comparison:** When two models disagree (e.g., Copernicus vs HYCOM currents), MCMC can estimate which model is more consistent with the real buoy observations — a **data-driven** model weight, not an assumed one.

**Output:**
- Distribution: Posterior probability density for each key output scalar
- Scalar: 95% credible interval for impact scores
- Figure: Trace plots showing MCMC convergence
- Diagnostic: Gelman-Rubin R-hat (convergence check)

---

## 5. How Variables Flow Through the System

The 169 variables from the catalog flow into specific modules:

```
REAL DATA CUBE
│
├─→ MODULE A (Baseline): ALL 169 variables extracted at site + ROI
│
├─→ MODULE B1 (Wake):
│     Wind speed 100m (4.5), Wind direction 100m (4.6), SST (2.10),
│     T2m (4.8), Boundary layer height (4.17), Friction velocity (4.19),
│     Surface roughness (4.18)
│
├─→ MODULE B2 (Noise):
│     Temperature profile (1.1), Salinity profile (1.8), Depth/pressure,
│     pH (8.10), Wave height (3.1), Bottom sediment (10.4) if available
│
├─→ MODULE B3 (Scour):
│     Bottom current u/v (1.12,1.13 at bottom level), Wave height (3.1),
│     Wave period (3.4), Depth (10.1), Grain size (10.5) if available
│
├─→ MODULE B4 (EMF):
│     Salinity (1.8), Temperature (1.1), Bottom current (1.12,1.13)
│
├─→ MODULE C1 (Lagrangian):
│     3D u (1.12), 3D v (1.13), Stokes drift u/v (3.20,3.21),
│     SSH (2.1), Wind 10m (4.1,4.2), MLD (2.7), Bathymetry (10.1),
│     T/S profiles (1.1,1.8) for stratification → Kz diagnostic
│
├─→ MODULE C2 (Acoustic):
│     T profile (1.1), S profile (1.8), Depth (10.1), pH (8.10),
│     Wave height (3.1), Sediment type (10.4) if available
│
├─→ MODULE C3/C4 (Species/Cumulative):
│     Chl (8.1), O2 (8.8), Temperature (1.1), Salinity (1.8),
│     Bathymetry (10.1), OBIS occurrence (9.1–9.4),
│     ALL Module B outputs as impact layers
│
├─→ MODULE D (Human Conflict):
│     GFW vessel presence (11.1,11.2), MPA boundaries (12.1),
│     Lease blocks (12.4), Shipping lanes
│
├─→ MODULE E (Optimization):
│     Wind 100m (4.5), Bathymetry (10.1), Species probability (9.x),
│     GFW vessel presence (11.1,11.2), MPA boundaries (12.1),
│     ALL Module C/D outputs as objective layers
│
└─→ MODULE F (MCMC):
      ANY variable with uncertainty, buoy observations for validation,
      Multi-source spread for ensemble uncertainty
```

---

## 6. Output: What the User Gets

### 6.1 Per-Module Output Types

| Module | Output Type | What It Is |
|--------|------------|------------|
| A — Baseline | Time series, scalars, climatology tables | Monthly means, trends, extremes, data quality report |
| B1 — Wake | Spatial field | Wind deficit (%) map at hub height |
| B2 — Noise source | Scalars | Source level in dB at key frequencies |
| B3 — Scour | Scalars + time series | Shear stress, scour depth estimate |
| B4 — EMF | Spatial field | Magnetic field µT around cable |
| C1 — Lagrangian | GeoJSON trajectories + spatial density + scalars | Particle paths, displacement stats, connectivity |
| C2 — Acoustic propagation | Spatial field | Noise level maps at key frequencies |
| C3 — Species risk | Spatial fields + scalars + tables | Risk maps per group, species lists |
| C4 — Cumulative | Spatial field + scalar | Integrated impact score, stacked contributions |
| D — Human conflict | Spatial fields + scalars | Shipping/fishing conflict per sector |
| E — Optimization | Spatial fields + scatter plots + table | Pareto sites, trade-off curves, site ranking |
| F — MCMC | Distributions + scalars | Credible intervals, posterior densities |

### 6.2 Assembling the Final Report

All module outputs are merged into one systematic report:

1. **Executive Summary:** One-page summary of findings with key numbers
2. **Site Baseline:** What the environment looks like at the proposed site
3. **Physical Footprint:** Maps of wake, noise, scour, EMF
4. **Environmental Response:** Lagrangian trajectories, acoustic footprint, species risk
5. **Human Conflict:** Shipping and fishing conflict analysis
6. **Optimization:** How your site compares to alternatives — rank and trade-offs
7. **Uncertainty Assessment:** What we're confident about, what needs more data
8. **Data Provenance:** Every data source, every coefficient, every equation cited with DOI/reference

---

## 7. Implementation Plan

### Phase 1: Fused Data Cube (Foundation)

Build the real-data-only cube for the Scotian Shelf ROI.

**Data sources to ingest (in order):**
1. Copernicus Global PHY (3D T, S, U, V) — requires auth, done
2. GEBCO 2026 — bathymetry, one-time download
3. Open-Meteo Marine + Atmosphere — no auth, hourly, quick
4. HYCOM — no auth, OPeNDAP
5. ERA5 via CDS — requires CDS account
6. CIOOS Atlantic ERDDAP — buoy + CTD data
7. OBIS — species occurrences
8. GFW — vessel presence (token from friend's script)
9. DFO governance layers — shapefile download

**Cube construction:** Define common grid → fetch each source → regrid → merge with quality flags → write Zarr.

### Phase 2: Core Simulation Modules

**Priority order (by scientific importance for the windmill story):**
1. **Module A — Baseline** (required by everything else)
2. **Module B1 — Wake** (the most direct windmill impact)
3. **Module C1 — Lagrangian** (shows connectivity, drift, dispersion)
4. **Module E — Optimization** (the decision output — the payoff)
5. **Module C3 — Species risk** (ecological layer)
6. **Module D — Human conflict** (GFW + MPA)
7. **Module C2 — Acoustic** (noise propagation)
8. **Module B2/B3 — Noise source/Scour** (physical footprint details)
9. **Module F — MCMC** (uncertainty quantification, cross-cutting)

### Phase 3: API Layer

Serve the cube and module outputs via FastAPI endpoints. Frontend team only needs these endpoints — they never touch the data directly.

### Phase 4: Integration & Demo

End-to-end flow: user picks site → baseline shown → wake computed → Lagrangian run → species risk mapped → optimizer ranks sites → report generated.

---

## Appendix: Key References (Real Coefficients Come From These)

| Parameter | Source | Citation |
|-----------|--------|----------|
| Sound speed equation | UNESCO 1983 / Chen-Millero 1977 | Fofonoff & Millard (1983) UNESCO Technical Papers in Marine Science 44 |
| Seawater density (EOS-80 / TEOS-10) | IOC/SCOR/IAPSO 2010 | TEOS-10 Manual, IOC/UNESCO |
| François-Garrison absorption | François & Garrison (1982) JASA 72(6) | α computed from T, S, z, pH, f |
| Jensen wake model | Jensen (1983) Risø-M-2411 | Wake decay α = 0.5/ln(z/z0) |
| Bastankhah Gaussian wake | Bastankhah & Porté-Agel (2014) Renewable Energy 70 | Gaussian wake profile |
| Soulsby bottom stress | Soulsby (1997) "Dynamics of Marine Sands" | τ_c, τ_w, τ_cw formulas |
| Sumer & Fredsøe scour | Sumer & Fredsøe (2002) "The Mechanics of Scour..." | Scour depth formula |
| KPP mixing | Large, McWilliams, Doney (1994) Rev. Geophysics 32(4) | K-profile parameterization |
| Smagorinsky diffusivity | Smagorinsky (1963) Monthly Weather Review 91(3) | C_s ≈ 0.1 |
| Wenz ambient noise curves | Wenz (1962) JASA 34(12) | NL vs sea state |
| Operational turbine noise | Tougaard et al. (2020) JASA 147(4) | Measured SL from real wind farms |
| Pile driving noise | Bailey et al. (2010) Marine Pollution Bull. 60(6) | Measured SL from real construction |
| NSGA-II | Deb et al. (2002) IEEE Trans. Evol. Comp. 6(2) | Multi-objective optimization |
