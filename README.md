# Hack-The-Element-PSI

Marine Digital Twin Platform — Scotian Shelf Region (`43.68°N–44.83°N, -64.33°W to -61.94°W`)

## Data Documentation

| File | Purpose | Contents |
|------|---------|----------|
| [api/variables.md](api/variables.md) | **Master Variable Inventory** | 169 variables across 14 scientific domains, organized by module (Lagrangian, MCMC, SDM, acoustics, wind energy, MSP optimization). Maps every variable to its data source with temporal/spatial resolution. Flags 10 gaps with mitigations. |
| [api/oceans.md](api/oceans.md) | **Data Source Catalog** | 16 APIs cataloged with endpoints, auth requirements, Python code snippets, variable listings, temporal spans, and Scotian Shelf relevance. How to access each data source. Includes Open-Meteo Marine & Atmosphere. |

## Quick Reference

### Auth Status
- **No auth required:** HYCOM, Open-Meteo (all), CIOOS/CanWIN ERDDAP, OBIS, GEBCO, NOAA CO-OPS, MSC GeoMet
- **Free registration:** Copernicus Marine, Global Fishing Watch, ONC Oceans 3.0, AIS Stream
- **Paid:** None needed for MVP

### Variable Coverage
- **169 variables** cataloged across 14 scientific domains
- **152 covered** by real scientific APIs
- **10 gaps** — all mitigable (diagnostic computation or alternative databases)
- **Temporal span:** 1940–present (ERA5), 1993–present (Copernicus reanalysis), real-time (NRT + buoys)
- **Spatial resolution:** 1/12° (~8 km) models, 15 arc-sec (~450 m) bathymetry, point in-situ

### Demo Link 
https://drive.google.com/file/d/1tS_uzlaD9QxP25eyt1MyKsT37QL4g_cD/view?usp=share_link
