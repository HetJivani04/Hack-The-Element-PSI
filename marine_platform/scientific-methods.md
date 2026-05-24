# Scientific Methods — Marine Digital Twin Windmill Simulation

**All parameters derived from real data. No hardcoded constants aside from universal physical constants.**

---

## 1. WIND WAKE MODELING

### 1.1 Gaussian Wake (Bastankhah & Porté-Agel 2014) — RECOMMENDED

The platform uses the BP-A Gaussian wake model. More physically accurate than Jensen (top-hat assumption), simpler to implement than FLORIS.

**Velocity deficit equation:**

```
Δu / u∞ = [1 - √(1 - Ct / (8(σ/D)²))] · exp(-0.5 · (r/σ)²)
```

Where every parameter comes from real data:

| Parameter | Source | Origin |
|-----------|--------|--------|
| `u∞` | ERA5 `u100`, `v100` at site | Real wind data at hub height |
| `Ct` | Manufacturer power curve lookup Ct(u∞) or Ct = 4a(1-a) | Real turbine specs |
| `σ/D = k*·x/D + ε` | Wake width, k* computed from real TI | Real turbulence |
| `k* ≈ 0.35·TI` | Wake expansion rate | From real friction velocity u* |

**Wake decay constant α (when using Jensen model as fallback):**

```
α = 0.5 / ln(z_hub / z₀)
```

where `z₀` is the atmospheric surface roughness from **real ERA5 data** (`fsr` or computed via Charnock: z₀ = α_ch·u*²/g with α_ch = 0.0144). NOT an assumed constant like 0.04 or 0.075.

**Atmospheric stability correction:**

Using Monin-Obukhov similarity theory with Obukhov length L from real ERA5 fluxes:

```
L = -u*³·θv / (κ·g·w′θv′)

α(z/L) = α_neutral · f(z/L)
f(z/L) > 1 for unstable (faster recovery)
f(z/L) < 1 for stable (longer wake)

Where φ_m(z/L) from Dyer (1974):
  Unstable: φ_m = (1 - 16·z/L)^(-1/4)
  Stable:   φ_m = 1 + 5·z/L
  α ∝ 1/φ_m
```

### 1.2 Wake-Added Turbulence (Frandsen 2007)

```
TI_wake(x) = √(TI_amb² + TI_add²)
TI_add² = 1 / (1.5 + 0.8·x/D / √(Ct))
```

Where `TI_amb = u*/U` from real ERA5 friction velocity and wind speed.

---

## 2. UNDERWATER NOISE MODELING

### 2.1 Source Level — Operational

From published measurements at operational wind farms (Tougaard et al. 2009, 2020; Madsen et al. 2006):

| Turbine Size | Measured SL (dB re 1μPa @ 1m) |
|---|---|
| 2-3 MW | 109-127 |
| 3.6 MW | 113-120 |
| 6 MW | 118-131 |
| 8 MW | 120-134 |
| 15 MW (scaled) | 125-140 |

Frequency content: tonal at blade-passing frequency f_BPF = 3·Ω (20-27 Hz for 15 MW), broadband at higher frequencies.

### 2.2 Source Level — Construction (Pile Driving)

From published measurements:

| Hammer/Pile | Measured SL_peak | SEL_single-stroke |
|---|---|---|
| Hydraulic 2-3m pile | 200-215 dB | 175-190 dB |
| Hydraulic 4-6m pile | 210-230 dB | 185-200 dB |
| 15 MW monopile (8-10m) | 220-240 dB | 190-210 dB |

Cumulative SEL: SEL_cum = SEL_ss + 10·log₁₀(N), with N ≈ 500-2000 strokes.

### 2.3 Transmission Loss — François-Garrison (1982) EXACT

**Absorption coefficient α (dB/km):**

```
α = A₁·P₁·f²/(f² + f₁²) + A₂·P₂·f²/(f² + f₂²) + A₃·P₃
```

**Boric acid (low frequency):**
```
A₁ = 0.106 · exp((pH - 8) / 0.56)
f₁ = 0.78 · √(S/35) · exp(T/26)
```

**Magnesium sulfate (mid frequency):**
```
A₂ = 21.44 · (S/35) · (1 + 0.025·T)
f₂ = 42.0 · exp(T/17)
P₂ = 1 - 1.37×10⁻⁴·z + 6.2×10⁻⁹·z²
```

**Pure water viscosity (high frequency):**
```
For T ≤ 20°C: A₃ = 4.937×10⁻⁴ - 2.59×10⁻⁵·T + 9.11×10⁻⁷·T² - 1.50×10⁻⁸·T³
P₃ = 1 - 3.83×10⁻⁵·z + 4.9×10⁻¹⁰·z²
```

Every input from real data:
- T → Copernicus `thetao` at site depth
- S → Copernicus `so` at site depth
- z → GEBCO depth
- pH → Copernicus BGC `ph`

**Total transmission loss:**
```
TL(r,f) = 20·log₁₀(r) + α(f)·r/1000   [deep water]
TL(r,f) = 15·log₁₀(r) + α(f)·r/1000   [shelf — Scotian Shelf]
TL(r,f) = 10·log₁₀(r) + α(f)·r/1000   [very shallow]
```

**Surface reflection loss (Rayleigh roughness):**
```
R_s = -exp(-0.5 · (2k·H_s·sin θ)²)
```
where H_s is real significant wave height from Copernicus WAV `VHM0`.

### 2.4 Ambient Noise — Wenz Curves

```
NL(f) = 10·log₁₀(10^(NL_wind/10) + 10^(NL_ship/10))

NL_wind(f, U_s) = 50 + 7.5·U_s^0.5 - 17·log₁₀(f)   [dB, f in kHz]
NL_ship(f, D_ship) = 60 + 10·log₁₀(D_ship) - 15·log₁₀(f/100)
```

Where:
- U_s = wind speed from real ERA5 10m wind
- D_ship = vessel density from real GFW AIS data

---

## 3. SCOUR / SEDIMENT TRANSPORT

### 3.1 Bottom Shear Stress — Soulsby (1997)

**Current-only stress:**
```
τ_c = ρ · C_D · U²
C_D = [κ / (ln(z₀/z_r) + 1)]²
z₀ = d50 / 12
```

**Wave-only stress (Swart 1974):**
```
τ_w = ½ · ρ · f_w · U_orb²

U_orb = π·H_s / (T_p·sinh(kh))     [linear wave theory]
f_w = exp(-5.977 + 5.213·(A/k_s)^(-0.194))   for A/k_s > 1.57
A = U_orb·T_p / (2π)
k_s = 2.5·d50
```

Dispersion relation solved iteratively: ω² = gk·tanh(kh) from real T_p and depth.

**Combined wave-current (Soulsby Eq. 69):**
```
τ_mean = τ_c · [1 + 1.2 · (τ_w/(τ_c + τ_w))^3.2]
τ_max = √[(τ_mean + τ_w·cos φ)² + (τ_w·sin φ)²]
```

**Critical shear stress (Soulsby & Whitehouse 1997):**
```
τ_cr = θ_cr · g · (ρ_s - ρ) · d50
θ_cr = 0.30/(1 + 1.2·D*) + 0.055·[1 - exp(-0.020·D*)]
D* = d50 · [g·(s-1)/ν²]^(1/3)
```

### 3.2 Scour Depth — Sumer & Fredsoe (2002)

```
Steady current: S_c/D = 1.3   (clear-water scour, θ < 2·θ_cr)
Waves only:     S_w/D = 1.3·{1 - exp[-0.03·(KC - 6)]}   for KC ≥ 6
                KC = U_orb·T_p / D

Combined wave-current:
S_cw/S_c = 1 - exp[-A·(θ_cw/θ_cr - 1)],   A ≈ 0.08-0.10

Time development:
S(t)/S_eq = 1 - exp(-t/T_s)
T_s·√(g·(s-1)·d50³)/D² = 1/(2000·θ^2.2)
```

**If sediment grain size d50 is unavailable from NRCan maps:** τ_c, τ_w, τ_cw are still computed (from real currents + waves). But τ_cr and scour depth S are NOT computed — reported as "sediment data missing; only shear stress available."

---

## 4. ELECTROMAGNETIC FIELD

**Biot-Savart law:**
```
B(r) = μ₀·I / (2π·r)   [single conductor, DC]
```

**Three-phase AC cable (far-field dipole):**
```
B_net(r) ≈ 3·μ₀·I·s / (4π·r³)
```

Where s is conductor spacing (~0.05-0.1m for 3-core cable).

**Induced electric field:**
```
E_ind = v · B
```
where v = real water current velocity from Copernicus.

**Typical 15 MW turbine export cable:** 66 kV AC, I ≈ 138 A per turbine, burial depth 1-3m.

At 1m depth: B ≈ 3.15 μT (well below Earth's 50 μT background). EMF effects drop to background within meters.

---

## 5. PHYSICAL ENVIRONMENT MODELING

### 5.1 Sound Speed Profile — UNESCO/Chen-Millero EXACT

```
c(T,S,z) = C_w(T,z) + A(T,z)·S + B(T,z)·S^(3/2) + D·S²
```

With 27 exact coefficients (Fofonoff & Millard 1983). Valid T = -2 to 35°C, S = 0-45 ppt, z = 0-4000m.

### 5.2 Seawater Density — UNESCO EOS-80 / TEOS-10

```
ρ(T,S,P) = ρ_w + (b₀ + b₁·T + b₂·T² + b₃·T³ + b₄·T⁴)·S
           + (c₀ + c₁·T + c₂·T²)·S^(3/2) + d₀·S²
```

15 exact coefficients. All inputs from real Copernicus T,S,P data.

### 5.3 Stratification (Brunt-Väisälä Frequency)

```
N²(z) = -(g/ρ₀)·(∂ρ/∂z)
     ≈ (g/ρ₀)·[α(T,S)·∂T/∂z - β(T,S)·∂S/∂z]
```

From real T,S profiles. Used for K-profile diffusivity parameterization.

---

## 6. KEY REFERENCES

- Bastankhah & Porté-Agel (2014) *Renewable Energy* 70, 116-123
- Frandsen (2007) *Risø-R-1188* — Turbulence in wind turbine clusters
- François & Garrison (1982) *JASA* 72(3,6), 896-907, 1879-1890
- Wenz (1962) *JASA* 34(12), 1936-1956
- Soulsby (1997) *Dynamics of Marine Sands*, Thomas Telford
- Sumer & Fredsøe (2002) *The Mechanics of Scour in the Marine Environment*, World Scientific
- UNESCO (1983) *Tech. Papers in Mar. Sci.* No. 44 — Algorithms for seawater properties
- Chen & Millero (1977) *JASA* 62(5), 1129-1135
- Tougaard et al. (2009, 2020) — Measured offshore wind turbine noise
- Dyer (1974) — Monin-Obukhov stability functions
- Niayifar & Porté-Agel (2016) *Energies* 9(9), 741 — TI-dependent k*

---

## 7. LAGRANGIAN PARTICLE TRACKING

### 7.1 Governing Equation

```
dx_p(t) = v[x_p(t), t]·dt + dw(t)
```
where deterministic velocity: `v = u_eulerian + u_stokes + u_tide + u_windage`

### 7.2 4D Interpolation (x, y, z, t)

**Temporal → Horizontal → Vertical** (order doesn't matter — all linear operations):

Bilinear horizontal + linear vertical + linear temporal. Standard 4D interpolation from Copernicus grid to particle position. At each timestep, identify bracketing grid cells and interpolate.

### 7.3 RK4 Integration

```
k1 = v[x^n, t^n]
k2 = v[x^n + (Δt/2)·k1, t^n + Δt/2]
k3 = v[x^n + (Δt/2)·k2, t^n + Δt/2]
k4 = v[x^n + Δt·k3, t^n + Δt]

x^{n+1} = x^n + (Δt/6)(k1 + 2k2 + 2k3 + k4)
```

For Scotian Shelf (1/12°, u ~0.1-1.0 m/s): Δt = 300-900s standard.

| Scheme | Local error | Global error |
|--------|------------|--------------|
| Euler | O(Δt²) | O(Δt) |
| RK2 | O(Δt³) | O(Δt²) |
| RK4 | O(Δt⁵) | O(Δt⁴) |

### 7.4 Stochastic Diffusion

```
dx_random = √(2·K_h·Δt)·N(0,1) + (∂K_z/∂z)·Δt   [pseudovelocity correction]
dy_random = √(2·K_h·Δt)·N(0,1)
dz_random = √(2·K_z·Δt)·N(0,1)
```

The `∂K_z/∂z` pseudovelocity term is essential — without it, particles artificially accumulate in low-diffusivity regions (Visser 1997).

**Horizontal diffusivity — Smagorinsky (1963):**
```
K_h = C_s·Δx·Δy·|S|
|S| = √(2·(∂u/∂x)² + 2·(∂v/∂y)² + (∂u/∂y + ∂v/∂x)²)
```
C_s = 0.1 (Smagorinsky constant, universal). |S| computed from real Copernicus velocity gradients.

**Vertical diffusivity — Pacanowski-Philander (1981):**
```
K_z = K_b + (K_max - K_b)/(1 + α·Ri)^n
Ri = N²/S²
N² = -(g/ρ₀)(∂ρ_θ/∂z)     [from real T,S profiles]
S² = (∂u/∂z)² + (∂v/∂z)²   [from real velocity profiles]
```
α = 5, n = 2 (empirical form — but N² and S² are from real data, so K_z is data-driven).

### 7.5 Stokes Drift

Preferred: use Copernicus WAV `VSDX`, `VSDY` directly (includes full 2D wave spectrum).

Monochromatic approximation (when spectral data unavailable):
```
U_s(z) = (ω·k·a²)/(2·sinh²(kh))·e^(2kz)
a = H_s/4,  ω = 2π/T_p
```
Wavenumber k solved from dispersion relation ω² = gk·tanh(kh) using real T_p and depth.

### 7.6 Tidal Currents — 10 Harmonic Constituents

```
u_tide(t) = Σ f_i(t)·A_i(x,y)·cos(ω_i·t - g_i(x,y) + V_i(t₀) + u_i(t))
```

| Constituent | Type | Period (h) |
|-------------|------|-----------|
| M2 | Principal lunar semidiurnal | 12.42 |
| S2 | Principal solar semidiurnal | 12.00 |
| N2 | Larger lunar elliptic | 12.66 |
| K2 | Lunisolar semidiurnal | 11.97 |
| K1 | Lunisolar diurnal | 23.93 |
| O1 | Principal lunar diurnal | 25.82 |
| P1 | Principal solar diurnal | 24.07 |
| Q1 | Larger lunar elliptic diurnal | 26.87 |
| M4 | Shallow water quarter-diurnal | 6.21 |
| MSf | Lunisolar synodic fortnightly | 354.37 |

A_i, g_i from DFO WebTide (calibrated to Scotian Shelf). f_i, u_i from astronomical arguments.

### 7.7 Windage

```
u_windage = C_d·u_wind_10m
C_d = 0.01 for U_10 ≤ 5 m/s
C_d = 0.01 + 0.003·(U_10 - 5) for 5 < U_10 < 25 m/s
C_d = 0.07 for U_10 ≥ 25 m/s
```

Wind drag coefficient derived from field drifter studies (Edwards et al. 2006). u_wind_10m from real ERA5.

### 7.8 Boundaries

| Boundary | Condition |
|----------|-----------|
| Coastline | Check GEBCO mask → mark "beached" |
| Surface (z=0) | Reflect: z ← -z, w ← -w |
| Seabed (z=-h) | Reflect: normal component negated |
| ROI | Mark "exited" with coordinates + timestamp |

---

## 8. ACOUSTIC PROPAGATION MODELING

### 8.1 Sound Speed Profile — UNESCO/Chen-Millero (1977)

Full equation with 27 exact coefficients (Fofonoff & Millard 1983):

```
c(S,T,P) = C_w(T,P) + A(T,P)·S + B(T,P)·S^(3/2) + D·S²
```

C_w begins at 1402.388 m/s with polynomial terms in T (up to T⁵), P (up to P³), and T×P cross-terms. Valid: T=-2 to 35°C, S=0-45 ppt, z=0-4000m.

**Scotian Shelf seasonal c(z):**
- Winter (Jan-Mar): Nearly isovelocity, c ~1440-1460 m/s, weak gradient
- Summer (Jul-Sep): Strong thermocline at 20-40m, c ~1490-1510 m/s at surface, ~1460 m/s below

Must be computed from Copernicus T,S profiles, not assumed.

### 8.2 François-Garrison Absorption (1982)

```
α = A₁·P₁·f²/(f²+f₁²) + A₂·P₂·f²/(f²+f₂²) + A₃·P₃·f²   [dB/km]
```

**Boric acid:**
```
A₁ = (8.86/c)·10^(0.78·pH - 5)
f₁ = 2.8·√(S/35)·10^(4 - 1245/(T+273))
```

**Magnesium sulfate:**
```
A₂ = 21.44·(S/c)·(1 + 0.025·T)
f₂ = (8.17×10^(8 - 1990/(T+273)))/(1 + 0.0018·(S-35))
```

**Pure water viscosity (Ainslie & McColm 1998):**
- T ≤ 20°C: A₃ = 4.937×10⁻⁴ - 2.59×10⁻⁵·T + 9.11×10⁻⁷·T² - 1.50×10⁻⁸·T³
- T > 20°C: A₃ = 3.964×10⁻⁴ - 1.146×10⁻⁵·T + 1.45×10⁻⁷·T² - 6.5×10⁻¹⁰·T³

**Pressure corrections:** P₁=1, P₂=1-1.043×10⁻⁴·P, P₃=1-3.83×10⁻⁵·P+4.9×10⁻¹⁰·P²

All inputs from real Copernicus data: T from `thetao`, S from `so`, pH from `ph`, c from Chen-Millero.

### 8.3 Transmission Loss

```
TL_total = TL_geo + TL_abs + TL_surf + TL_bot

TL_geo(r) = 20·log₁₀(r)               for r ≤ D   (spherical)
TL_geo(r) = 20·log₁₀(D) + 10·log₁₀(r/D)  for r > D   (cylindrical)

TL_abs(r) = α·r/1000    [α in dB/km, r in m]
```

**Surface reflection (Kirchhoff):**
```
R_surf = exp[-2·(k·σ_h·sin θ)²]
σ_h = H_s/4    [RMS surface roughness from Copernicus VHM0]
```

**Bottom reflection (Rayleigh):**
```
R_bot = (Z_b·sin θ - Z_w·sin θ_t)/(Z_b·sin θ + Z_w·sin θ_t)
Z_w = ρ_w·c_w,  Z_b = ρ_b·c_b
```
Sediment type from NRCan/GSC Scotian Shelf seabed maps. If unavailable: report as "sediment data missing — TL_bot has high uncertainty."

### 8.4 Received Level

```
RL = SL - TL_total
SE = RL - NL - DT      [Signal Excess]
NL_total = 10·log₁₀(10^(NL_wind/10) + 10^(NL_ship/10))
```

Where:
- SL from published measurements (Section 2)
- NL from Wenz curves using real wind + real AIS shipping density
- DT species-specific from published audiograms

---

## 9. SPECIES DISTRIBUTION MODELING

### 9.1 Maximum Entropy (MaxEnt) — Phillips et al. 2006/2017

```
P(y=1|x) = q_λ(x)·P(y=1) / (q_λ(x)·P(y=1) + (1-P(y=1)))
q_λ(x) = exp(Σ λ_k·f_k(x)) / Z_λ
```

Feature types: linear, quadratic, product, threshold, hinge. λ_k learned via penalized maximum likelihood with L1 regularization.

**Copernicus variables needed (from 169-variable catalog):**

| Feature | Copernicus Variable |
|---------|-------------------|
| Mean SST | `thetao` (monthly climatology) |
| SST range | annual `thetao` max-min |
| Mean SSS | `so` |
| Depth | GEBCO `elevation` |
| Chlorophyll mean | `chl` from BGC |
| Chlorophyll max | annual `chl` max |
| Sea ice | `siconc` |
| SST fronts | vertical∇θₒ computed from field |
| Bathymetric slope | vertical∇depth vertical from GEBCO |

Implementation: `elapid` Python package. Inputs: 50,000 OBIS occurrence records from our ROI.

**Variable importance — jackknife:** Train on all vars → get AUC_full. Remove one var → get AUC_{-k}. Importance = AUC_full - AUC_{-k}.

### 9.2 Bayesian Hierarchical Occupancy Model

```
z_i ~ Bernoulli(ψ_i)              [true occupancy]
logit(ψ_i) = β₀ + β₁·SST_i + β₂·depth_i + β₃·chl_i + ...

y_ij | z_i ~ Bernoulli(z_i·p_ij)  [observed detection]
logit(p_ij) = α₀ + α₁·effort_j
```

Priors: β ~ Normal(0, 2.5), σ² ~ HalfCauchy(0, 2.5) (Gelman 2006).

Implementation: PyMC with NUTS sampler. **Critical advantage:** properly accounts for imperfect detection — species may be present but not observed. MaxEnt assumes perfect detection.

### 9.3 Random Forest SDM

Alternative to MaxEnt. Pseudo-absence generation: 10,000 random background points within ROI. Prediction: mean of n_trees classifications. Feature importance via permutation: Imp(k) = AUC_original - AUC_permuted_k.

---

## 10. CONNECTIVITY METRICS

### 10.1 Connectivity Matrix

```
C_ij = (1/N_i)·Σ_{p ∈ S_i} I(x_p(T) ∈ D_j)
```

Fraction of particles from source i arriving at destination j. Row-stochastic.

### 10.2 Residence Time

```
τ_p(d) = max{t: |x_p(t) - x_p(0)| ≤ d}
Residence_time(d) = median{τ_p(d)}
```

e-folding time T_e from: P_retained(t) = exp(-t/T_e)

### 10.3 Dispersion Ellipse

From covariance matrix Σ = cov(X_final, Y_final):

```
Eigendecomposition: Σ = V·Λ·Vᵀ
Major axis: a = 2.448·√λ₁    (95% confidence)
Minor axis: b = 2.448·√λ₂
Orientation: θ = ½·atan2(2σ_xy, σ²_xx - σ²_yy)
Area: A = 2π·5.991·√(λ₁·λ₂)
```

### 10.4 Self-Recruitment

```
Self_recruitment_i = C_ii
```

Diagonal of connectivity matrix. High self-recruitment (>0.3) indicates local retention — important for MPA design and larval ecology (Cowen et al. 2006).

---

## REFERENCES — Lagrangian, Acoustics, SDM, Connectivity

- Van Sebille et al. (2018) "Lagrangian ocean analysis: Fundamentals and practices" — Ocean Modelling
- Large, McWilliams & Doney (1994) "Oceanic vertical mixing..." — Rev. Geophysics 32(4)
- Visser (1997) "Using random walk models to simulate the vertical distribution of particles in a turbulent water column" — Mar. Ecol. Prog. Ser.
- Pacanowski & Philander (1981) "Parameterization of vertical mixing in numerical models" — J. Phys. Oceanogr.
- Chen & Millero (1977) "Speed of sound in seawater at high pressures" — JASA 62(5)
- François & Garrison (1982) "Sound absorption based on ocean measurements" — JASA 72(3,6)
- Ainslie & McColm (1998) "A simplified formula for viscous and chemical absorption in sea water" — JASA 103(3)
- Beckmann & Spizzichino (1963) "The Scattering of Electromagnetic Waves from Rough Surfaces"
- Phillips, Anderson, Dudik, Schapire & Blair (2017) "Opening the black box: an open-source release of Maxent" — Ecography
- MacKenzie et al. (2002, 2017) "Occupancy Estimation and Modeling" — Academic Press
- Mitarai, Siegel & Watson (2009) "Quantifying connectivity in the coastal ocean..." — JGR Oceans
- Cowen et al. (2006) "Scaling of connectivity in marine populations" — Science 311
