# Marine Digital Twin — Rigorous Scientific Rebuild Plan

**Date:** 2026-05-24
**Status:** Pipeline runs end-to-end (16 tools pass), but with superficial output.
**Goal:** Full scientific rigor — all 169 variables, real data, real physics,
statistical validation on every output, published benchmark comparisons, time-evolving
simulations, and visualizations. Answer: "Should we put the windmill here?" with
quantified uncertainty.

---

## Current State Audit

### What Works (16/16 tools execute):
- A1 Baseline, B1 Wake, B2/C2 Acoustic, B3 Scour, B4 EMF, C1 Lagrangian,
  C3 Species, C4 Cumulative, D1-D4 Human Conflict, E1 NSGA-II Optimization,
  F1 MCMC, A11 Morris Sensitivity, Synthesis

### What's Superficial (every tool has at least one of these):
1. **Data gap:** Only 6/169 variables load from cube; rest are climatological fallbacks
2. **Registry mismatch:** `cube_source` IDs in registry.py don't match cube_metadata.json keys
3. **Wake wrong:** 49% deficit at 2D vs published 26-42% (Jensen model too aggressive)
4. **Cumulative zeros:** All impact layers are tiny values that normalize to zero
5. **Morris empty:** Rankings print nothing — analyzer produces empty output
6. **Species fake:** MaxEnt trained on random data (AUC 0.57, below published 0.70-0.95)
7. **No time evolution:** All tools use scalar means, no time-stepping simulation
8. **No visualizations:** No maps, no time series plots, no Pareto front charts
9. **Lagrangian fake:** Uses synthetic velocity fields instead of real GLORYS12 4D currents
10. **Human conflict mock:** Random shipping/fishing instead of real GFW raster data

---

## Task 1: Fix Registry-to-Cube Data Mapping (DATA_PIPELINE)

**Goal:** All 169 variables loadable via `cube.extract(var_id, lat, lon)` without KeyError.
Real data flows into every tool. Climatological fallbacks ONLY used when data genuinely
doesn't exist.

**Root cause:** Variable registry uses source IDs like `"glorys_physics"` but
cube_metadata.json keys are `"glorys_physics"` (some match, some don't). The
`_safe_extract()` wrapper silently returns None for KeyError, triggering fallbacks.

**Steps:**
1. Read `cube_metadata.json` — list all 29 source keys
2. Read `registry.py` — list all `cube_source` values
3. Cross-reference: find every mismatch
4. Update registry.py `cube_source` values to EXACTLY match metadata keys
5. Add a `validate_registry()` function that checks all 181 variables have valid sources
6. Remove `_safe_extract()` — replace with direct `cube.extract()` calls
7. Run pipeline — verify real data loads (should see temperature from GLORYS12, waves from WAVERYS, wind from ERA5, etc.)
8. Add `--mock-data=false` flag defaulting to real data only

**Files:** `marine_platform/variables/registry.py`, `marine_platform/cube/reader.py`, `execute_pipeline.py`
**Verification:** Pipeline prints "Loaded X/169 variables from cube" with X > 100

---

## Task 2: Fix Wind Wake Model Physics (WAKE_FIX)

**Goal:** Wake deficits match published BP&A (2014) LES benchmarks within tolerance.
Current: 49% at 2D. Target: 26-42% at 2D.

**Root cause:** Jensen (1983) model uses `alpha=0.075` wake decay constant for
onshore. Offshore value should be ~0.04. Also, the thrust coefficient Ct should
be computed from the turbine's power curve at the actual wind speed, not assumed.

**Steps:**
1. Read `WindWakeModel` class in `windmill_effects.py` — check Jensen alpha, Ct computation
2. Implement BP&A (2014) Gaussian wake model as the PRIMARY model
   - Eq: ΔU/U∞ = (1 - sqrt(1 - Ct/(8*(σ/D)²))) * exp(-r²/(2σ²))
   - σ/D = k* * x/D + ε, where k* = f(TI), ε = 0.2√β
3. Compute turbulence intensity TI from real wind data (std/mean of wind speed)
4. Keep Jensen as comparison/secondary model, label which is which
5. Compute deficits at standard distances: 2D, 5D, 10D, 20D, 40D, 60D
6. Each deficit gets: value, 95% CI (bootstrap across wind speeds), comparison to published range
7. Add Park (2014) model as ensemble member for uncertainty quantification
8. Wake recovery distance: use 5% threshold with ensemble spread

**Files:** `marine_platform/science/windmill_effects.py` (WindWakeModel class)
**Verification:** 2D deficit in 26-42% range, all published comparisons show ✓

---

## Task 3: Real Lagrangian Tracking with GLORYS12 Currents (LAGRANGIAN_REAL)

**Goal:** LagrangianParticleTracker uses real 4D (time, depth, lat, lon) velocity
fields from GLORYS12, not synthetic fields.

**Steps:**
1. Load full 4D uo, vo from cube for the ROI time window
2. Load depth levels from GLORYS12
3. Compute Smagorinsky horizontal diffusivity from real velocity gradients
4. Compute Pacanowski-Philander vertical diffusivity from real N² stratification
5. Run 500 particles with RK4 time stepping over real velocity fields
6. Output: mean/max displacement with bootstrap CI, dispersion ellipse (major/minor axis, orientation), beaching statistics, connectivity matrix between sub-regions
7. Ensemble: run 3x with perturbed initial positions, report ensemble spread
8. Compare against published drifter trajectories in Scotian Shelf (DFO AZMP drifter program)

**Files:** `marine_platform/science/windmill_effects.py` (LagrangianParticleTracker), `execute_pipeline.py`
**Verification:** Displacement values reflect real Scotian Shelf circulation (~50-150km over 7 days)

---

## Task 4: Real Species Distribution Modeling (SPECIES_REAL)

**Goal:** MaxEnt/LogisticRegression fitted to real OBIS occurrence data for Scotian Shelf
species, with AUC > 0.70 (matching published Elith et al. 2006 benchmarks).

**Steps:**
1. Load real OBIS dataset from cube (`cube.load_source('obis')`)
2. Filter to Scotian Shelf ROI (43.68-44.83N, 64.33-61.94W)
3. Build presence-only dataset: species × (lat, lon)
4. Extract real environmental layers at each occurrence point:
   - SST (from Copernicus SST)
   - Depth (from GEBCO)
   - Chlorophyll-a (from Copernicus BGC)
   - SST gradient (from spatial derivative)
   - Distance to shore (from GEBCO coastline)
5. Generate 10,000 background points (random across ROI) for MaxEnt
6. Fit L1-regularized logistic regression (equivalent to MaxEnt)
7. 5-fold cross-validation: report mean AUC ± SD
8. Variable importance via permutation test (not just coefficient magnitude)
9. Predict habitat suitability across full ROI (13×28 grid)
10. Compute connectivity metrics: habitat area, n_patches, mean patch size, fragmentation index
11. Species-specific models for NARW (North Atlantic right whale) using known habitat preferences
12. Compare AUC against published: Elith et al. (2006) MaxEnt AUC 0.70-0.95

**Files:** `marine_platform/science/windmill_effects.py` (SpeciesDistributionModel), `execute_pipeline.py`
**Verification:** AUC > 0.70, variable importance has ecological meaning (depth should be top predictor)

---

## Task 5: Fix Cumulative Impact with Real Spatial Data (CUMULATIVE_FIX)

**Goal:** CumulativeImpactAssessor produces meaningful scores (not all zeros) using
real spatial impact layers derived from upstream tools.

**Steps:**
1. Build real impact layers from tool outputs:
   - Wake layer: wake deficit field (2D spatial) from WindWakeModel.run_2d_field()
   - Noise layer: received level field from AcousticPropagationModel
   - Scour layer: shear stress exceedance from FoundationScourModel
   - Species layer: habitat suitability change (pre vs post windmill) from SDM
   - EMF layer: B-field exceedance from ElectromagneticFieldModel
2. Normalize each layer to [0,1] with proper min-max across ROI
3. Weight layers by ecological significance (from published impact weights)
4. Compute cumulative score per cell with uncertainty propagation:
   - Draw N=1000 Monte Carlo samples from each layer's uncertainty distribution
   - Compute cumulative score per sample → distribution of cumulative scores per cell
5. Report: global mean score with 95% CI, spatial hot spots (top 5% cells), per-variable Sobol' sensitivity indices
6. Compare against Halpern et al. (2008) global cumulative impact framework methodology

**Files:** `marine_platform/science/windmill_effects.py` (CumulativeImpactAssessor), `execute_pipeline.py`
**Verification:** Cumulative score in 0.01-0.20 range (not 0.000), uncertainty CIs don't span zero

---

## Task 6: Fix Morris Sensitivity with Real Parameters (MORRIS_FIX)

**Goal:** MorrisAnalyzer produces ranked parameter sensitivities with μ* values
for all parameters in the turbine + environment system.

**Root cause:** `MorrisAnalyzer.analyze()` returns empty rankings — either the
dummy model produces constant output, or the analyzer has a bug.

**Steps:**
1. Debug MorrisAnalyzer.analyze() — trace through with test inputs
2. Fix ParameterSpace integration — ensure sampled parameters flow to model
3. Build real forward model: wake_deficit(wind_speed, TI, z0, Ct) → deficit at 2D
4. Run Morris with 20 trajectories, 4 levels per parameter
5. Parameters to analyze (at least 8):
   - Wind speed at 100m (5-15 m/s)
   - Turbulence intensity (0.04-0.15)
   - Surface roughness z0 (0.0001-0.001 m)
   - Thrust coefficient Ct (0.6-0.9)
   - Water depth (50-200 m)
   - Significant wave height (1-6 m)
   - Current speed (0.05-0.5 m/s)
   - Ambient noise level (60-90 dB)
6. Report: μ* (mean absolute elementary effect), σ (standard deviation), ranking
7. Classify each parameter: linear (σ/μ* < 0.1), monotonic (0.1 < σ/μ* < 1), interactive (σ/μ* > 1)
8. Compare against published: Morris (1991) Technometrics, Campolongo et al. (2007)

**Files:** `marine_platform/science/sensitivity.py` (MorrisAnalyzer), `execute_pipeline.py`
**Verification:** 8+ parameters ranked with non-zero μ*, classification by linear/nonlinear

---

## Task 7: Time-Evolving Weather-Driven Simulation (TIME_SIM)

**Goal:** Run a 7-day time-stepping simulation showing how the environment responds
hour-by-hour when the windmill operates under real weather forcing.

**Steps:**
1. Load 7 days of hourly ERA5 wind (u10, v10, u100, v100), waves (Hs, Tp, Dm),
   currents (uo, vo), and temperature from cube
2. For each hour:
   a. Compute wind speed at hub height (log-law extrapolation from 100m)
   b. Compute turbine power output (from power curve)
   c. Compute wake deficit field (BP-A Gaussian, depends on wind speed + TI)
   d. Compute underwater noise source level (operational, depends on power)
   e. Compute acoustic propagation (depends on stratification that hour)
   f. Compute Lagrangian particle advection (currents + Stokes drift)
   g. Compute scour shear stress (combined wave-current)
3. Accumulate statistics over the 7-day period:
   - Total energy produced (MWh)
   - Mean/max wake deficit
   - Mean/max noise footprint area
   - Particle displacement trajectories
   - Cumulative scour exceedance hours
4. Output: hourly time series CSV + summary statistics
5. Plot: time series of power, wind speed, wake deficit, noise footprint area
6. Compare 7-day simulation against climatological (annual mean) approach —
   show how much error is introduced by using means instead of time series

**Files:** `execute_pipeline.py` (new `run_time_simulation()` function)
**Verification:** Power output follows wind speed temporal pattern, wake varies with wind

---

## Task 8: Statistical Validation on EVERY Tool Output (STATS_DEPTH)

**Goal:** Every number in every tool output has a statistical test, effect size,
or confidence interval attached. No bare means. No unsupported claims.

**Current state:** ~60% of outputs have stats. Missing: scour, Lagrangian, species,
human conflict, optimization, cumulative, Morris.

**Steps (per tool):**
1. **Baseline (A1):** Add GEV return levels (10yr, 50yr, 100yr) for Hs and wind.
   Add seasonal decomposition (STL). Add Hurst exponent for long-range dependence.
2. **Wake (B1):** Bootstrap CI on every deficit distance. Cohen's d vs published mean.
   Ensemble spread across Jensen/BP-A/Park models.
3. **Acoustic (B2/C2):** Monte Carlo propagation loss (1000 samples, vary c(z) within
   UNESCO uncertainty ±2 m/s). Report 95% CI on all threshold distances.
4. **Scour (B3):** If d50 available, bootstrap CI on scour depth (1000 resamples of
   wave/current time series). If not, report why with data source citation.
5. **EMF (B4):** Sensitivity to cable burial depth (±0.5m), water conductivity (±10%).
   Report range of E_ind at 1m.
6. **Lagrangian (C1):** t-test on displacement (site vs regional mean). Bootstrap CI
   on dispersion ellipse parameters. Ensemble spread across 3 runs.
7. **Species (C3):** Cross-validated AUC ± SD. Permutation p-values for variable importance.
   Binomial test on NARW presence.
8. **Cumulative (C4):** 95% CI from Monte Carlo uncertainty propagation.
   Sobol' first-order and total-effect indices per impact layer.
9. **Human (D1-D4):** Bootstrap CI on shipping conflict index.
   Sensitivity to buffer radius (±2 km). Cohen's d vs regional median conflict.
10. **Optimization (E1):** Hypervolume indicator with bootstrap CI.
    Generational distance metric. Inverted generational distance.
11. **MCMC (F1):** Already has R-hat, ESS. Add: posterior predictive p-value interpretation,
    WAIC (Watanabe-Akaike IC) for model comparison, trace plots.
12. **Morris (A11):** Bootstrap CI on μ* (1000 resamples of trajectories).
    Convergence check: μ* vs n_trajectories.

**Files:** `execute_pipeline.py`, `marine_platform/engine.py`
**Verification:** Every print statement shows value + CI/effect/p-value triplet

---

## Task 9: Visualizations and Maps (VISUALIZATION)

**Goal:** Every tool that produces spatial output generates a publication-quality
figure. Time series tools generate time series plots.

**Steps:**
1. Add `plot/` directory with `plot_tools.py` module
2. Spatial map plots (cartopy + matplotlib):
   - Bathymetry map with site marker + feasible/infeasible cells
   - Wake deficit spatial footprint (colormap)
   - Acoustic propagation footprint (isopleths at threshold distances)
   - Habitat suitability map (colormap + occurrence overlay)
   - Cumulative impact map (per-cell scores)
   - NSGA-II Pareto-optimal sites (ranked markers on map)
3. Time series plots:
   - Temperature, salinity, wind speed, wave height time series with trend lines
   - Wind rose (directional histogram from real ERA5)
   - Wave rose
   - Lagrangian particle trajectories (spaghetti plot on map)
   - Power output vs time (7-day simulation)
   - MCMC trace plots (chain convergence)
4. Statistical plots:
   - Pareto front (energy vs ecology trade-off, 2D scatter)
   - Tornado plot (Morris sensitivity μ* with error bars)
   - Posterior density plots (MCMC parameter distributions)
   - Bootstrap CI forest plot (all tools on one figure)
5. Save all figures to `output/figures/` as PNG (300 dpi)
6. Generate HTML report stitching all figures + stats into one page
7. **Animated visualizations** (matplotlib.animation + ffmpeg, save as MP4/GIF):
   - Lagrangian particle drift animation: 500 particles over 168 hours, color-coded by depth, with bathymetry basemap
   - Wake deficit time-lapse: 7-day hourly wake field evolving with wind speed/direction changes
   - Acoustic footprint pulse animation: noise propagation isopleths expanding/contracting with varying stratification
   - Cumulative impact accumulation: layers stacking over time as each physical process activates
   - Pareto front evolution: NSGA-II generations animating population convergence toward optimal front
   - MCMC chain mixing: trace plot building iteration-by-iteration across 4 chains
   - Scour development: shear stress time series with storm events highlighting exceedance periods
8. All animations embedded in HTML report with playback controls

**Files:** `marine_platform/plot/plot_tools.py` (new), `execute_pipeline.py`
**Verification:** `output/figures/` contains 12+ PNGs + `output/animations/` contains 6+ MP4s

---

## Task 10: Integration Test — Full Pipeline Validation (INTEGRATION)

**Goal:** End-to-end test proving the platform answers both questions with full rigor.

**Steps:**
1. Run all 16 tools at 3 sites across the ROI (near-shore, mid-shelf, off-shelf)
2. Verify each tool produces output with: value, statistical test, published comparison
3. Verify no climatological fallbacks for variables that exist in cube
4. Verify all published comparisons show ✓ (values within published ranges)
5. Generate HTML report for each site
6. Compare the 3 sites — which is best? Does the answer change with different weighting?
7. Write `VALIDATION.md` documenting:
   - Number of real variables loaded per site
   - Number of statistical tests passed
   - Published benchmark hit rate (% of outputs within published ranges)
   - Known data gaps and their impact on confidence

**Files:** `execute_pipeline.py`, `VALIDATION.md` (new)
**Verification:** 3-site comparison produces ranked recommendation with uncertainty

---

## Execution Order

```
Task 1 (DATA_PIPELINE) ── first, everything depends on real data
    │
    ├── Task 2 (WAKE_FIX) ── independent physics fix
    ├── Task 3 (LAGRANGIAN_REAL) ── needs Task 1 data
    ├── Task 4 (SPECIES_REAL) ── needs Task 1 data
    ├── Task 5 (CUMULATIVE_FIX) ── needs Tasks 2,3,4 outputs
    ├── Task 6 (MORRIS_FIX) ── independent
    ├── Task 7 (TIME_SIM) ── needs Task 1 data + Task 2 wake model
    ├── Task 8 (STATS_DEPTH) ── can run parallel, touches all tools
    ├── Task 9 (VISUALIZATION) ── needs all tool outputs
    └── Task 10 (INTEGRATION) ── last, validates everything
```

Tasks 1, 6, 8 can start immediately (independent).
Tasks 2, 3, 4, 7 need Task 1.
Tasks 5, 9 need upstream tool outputs.
Task 10 needs everything.

---

## Success Criteria (the "Done" bar)

1. Pipeline extracts >100/169 variables from real cube data (not fallbacks)
2. Wake deficit at 2D: 26-42% (published range)
3. MaxEnt AUC > 0.70 (published benchmark)
4. Lagrangian displacement uses real GLORYS12 4D currents (not synthetic)
5. Cumulative impact score ≠ 0.000, with non-zero uncertainty decomposition
6. Morris sensitivity: 8+ parameters ranked with non-zero μ*
7. Time simulation: 7-day hourly output with energy production
8. Every tool output line formatted as: `name: value [CI] d=effect p=value sig | published: range`
9. 12+ publication-quality figures saved to `output/figures/`
10. 3-site comparison with ranked recommendation
