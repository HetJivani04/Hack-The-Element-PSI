# Data Source Organizations & Agencies

**Every data source used in the Scotian Shelf Marine Digital Twin — with links, what we downloaded, and license information.**

---

## 1. Copernicus Marine Service (CMEMS)

**Organization:** European Union / Mercator Ocean International
**Website:** https://marine.copernicus.eu/
**Data portal:** https://data.marine.copernicus.eu/
**Registration:** https://data.marine.copernicus.eu/register (FREE)

**What we downloaded:**
- GLORYS12V1 global ocean reanalysis (1993-2023) — 3D temperature, salinity, currents, SSH, MLD, sea ice
- Global Ocean Physics NRT (2024-2026) — 3D T, S, U, V at 6-hourly, surface fields daily, merged currents hourly
- Global Ocean Waves NRT (2024-2026) — 19 wave variables at 3-hourly, including Stokes drift
- WAVERYS wave reanalysis (2016-2023) — long-term wave climatology
- Global Ocean Biogeochemistry NRT (2024-2026) — chlorophyll, O2, nutrients, pH, DIC, alkalinity, NPP
- Static bathymetry (1/12°)

**License:** Free, open data. Registration required. Citation required.

---

## 2. Copernicus Climate Data Store (CDS)

**Organization:** European Centre for Medium-Range Weather Forecasts (ECMWF) / Copernicus
**Website:** https://cds.climate.copernicus.eu/
**API:** `cdsapi` Python package
**Registration:** https://cds.climate.copernicus.eu/ (FREE, must accept licence)

**What we downloaded:**
- ERA5 atmospheric reanalysis (2016-2025) — wind at 10m and 100m (u,v components), 2m temperature, MSLP, SST, precipitation, boundary layer height, friction velocity
- ERA5 wave reanalysis (2016-2025) — significant wave height, mean/peak wave period, mean wave direction, wind sea + swell partitions, Stokes drift components

**License:** Copernicus Licence (free for all uses, including commercial). Must accept terms on website.

**Citation:** Hersbach et al. (2020) "The ERA5 global reanalysis." Q.J.R. Meteorol. Soc. 146: 1999-2049. doi:10.1002/qj.3803

---

## 3. HYCOM Consortium

**Organization:** HYCOM Consortium — U.S. Navy / National Ocean Partnership Program (NOPP) / University of Miami / Florida State University
**Website:** https://www.hycom.org/
**Data server:** https://www.hycom.org/dataserver (THREDDS/OPeNDAP)

**What we downloaded:**
- HYCOM + NCODA Global 1/12° Reanalysis (GLBv0.08/expt_53.X) — 1994-2015, 3-hourly 3D fields
- HYCOM + NCODA Global 1/12° Analysis (GLBy0.08/expt_93.0) — GOFS 3.1, 2018-2024 surface samples

**License:** Public domain. No registration. OPeNDAP access.

---

## 4. Fisheries and Oceans Canada (DFO) / Bedford Institute of Oceanography (BIO)

**Organization:** Government of Canada — Department of Fisheries and Oceans / Bedford Institute of Oceanography (Dartmouth, Nova Scotia)
**Website:** https://www.dfo-mpo.gc.ca/
**BIO:** https://www.bio.gc.ca/

**CIOOS Atlantic ERDDAP:** https://cioosatlantic.ca/erddap/

**What we downloaded:**
- AZMP Moored CTD time series (2000-2023) — temperature, salinity, density, potential temperature at fixed moorings
- BBMP Bedford Basin Niskin bottle samples (2016-2024) — nutrients (ammonia, nitrite, nitrate, phosphate, silicate), oxygen, chlorophyll, HPLC pigments, POC/PON, pH
- AZMP Ecosystem Survey CTD vertical profiles — T, S, O2, chl, CDOM, PAR, transmittance
- Historical coastal/offshore moored CTD (1967-2023)

**Scotian Shelf MPA Conservation Network — EGISP ArcGIS REST:**
- https://egisp.dfo-mpo.gc.ca/arcgis/rest/services/open_data_donnees_ouvertes/offshore_ecological_human_use_mpa_scotian_shelf_en/MapServer
- 119 spatial layers: fisheries (37 layers), ecological habitats (10), depleted species (21), species richness (9), functional groups (38), biophysical (4)

**License:** Open Government Licence — Canada. Free for all uses with attribution.

**Citation:** DFO BIO (2026). AZMP/BBMP data accessed via CIOOS Atlantic ERDDAP.

---

## 5. Environment and Climate Change Canada (ECCC) / Meteorological Service of Canada (MSC)

**Organization:** Government of Canada — Environment and Climate Change Canada
**Website:** https://www.canada.ca/en/environment-climate-change.html
**MSC Open Data:** https://eccc-msc.github.io/open-data/

**What we downloaded:**
- Moored buoy observations via CanWIN ERDDAP (DFO MEDS Buoys)
- MSC marine weather forecasts via GeoMet OGC API

**License:** Open Government Licence — Canada.

---

## 6. SmartAtlantic / COVE (Centre for Ocean Ventures & Entrepreneurship)

**Organization:** SmartAtlantic Alliance / COVE / Marine Institute of Memorial University
**Website:** https://www.smartatlantic.ca/

**CIOOS ERDDAP datasets:**
- SMA_halifax — Halifax Herring Cove Buoy (2013-present): wind, waves, SST, air pressure, current profiles at multiple depth levels
- SMA_halifax_fairview — Fairview Cove wind station (2015-present): wind speed, direction, gusts, air temp, humidity, pressure
- SMA_halifax_pier9c — Pier 9C tide station (2014-present): wind, air temp, pressure, tide height

**License:** Open data.

---

## 7. Ocean Biodiversity Information System (OBIS)

**Organization:** UNESCO / Intergovernmental Oceanographic Commission (IOC)
**Website:** https://obis.org/
**API:** https://api.obis.org/

**What we downloaded:**
- 50,000+ species occurrence records for Scotian Shelf ROI (501,900 total available)
- 1,111 unique species including: American lobster (Homarus americanus), Atlantic cod (Gadus morhua), silver hake (Merluccius bilinearis), Atlantic herring (Clupea harengus), pollock, haddock, blue shark, various redfish species

**DFO datasets within OBIS:**
- Maritimes Spring RV Surveys — 650,166 records, bottom trawl
- Atlantic Reference Centre Museum — 139,730 records, 1,978 species

**License:** CC-BY 4.0. Citation of individual datasets required.

---

## 8. General Bathymetric Chart of the Oceans (GEBCO)

**Organization:** International Hydrographic Organization (IHO) / UNESCO IOC
**Website:** https://www.gebco.net/
**Data:** https://www.gebco.net/data_and_products/gridded_bathymetry_data/

**What we downloaded:**
- GEBCO 2026 global bathymetry grid at 15 arc-second resolution (~450m)
- (We used Copernicus 1/12° static bathymetry as the primary source for our common grid)

**License:** Public domain. Free for all uses.

---

## 9. Global Fishing Watch (GFW)

**Organization:** Global Fishing Watch (non-profit founded by Oceana, SkyTruth, Google)
**Website:** https://globalfishingwatch.org/
**API:** https://globalfishingwatch.org/apis

**What we downloaded:**
- Gridded vessel presence hours (4Wings API) for Scotian Shelf ROI
- Fishing effort by gear type
- Vessel presence by class (cargo, tanker, fishing, passenger)

**License:** CC-BY-SA 4.0. Free API token (registration required).

---

## 10. Open-Meteo

**Organization:** Open-Meteo (open-source weather API, Switzerland)
**Website:** https://open-meteo.com/
**API:** https://open-meteo.com/en/docs

**What we downloaded:**
- Marine API (DWD ICON wave model): 14 wave/SST/current variables at center point, hourly 2016-2026
- Forecast API: 92 days of recent wind at 10m+100m, temperature, pressure

**Note:** The Open-Meteo Archive API (for historical atmospheric data back to 1940) was not accessible from this network (DNS resolution + routing issue to `archive-api.open-meteo.com` IP 5.9.98.184). We used CDS ERA5 as the primary source for historical atmosphere instead.

**License:** CC-BY 4.0. Attribution to DWD (German Weather Service) required for marine data.

**Citation:** Zippenfenig, P. (2023). Open-Meteo.com Weather API. Zenodo. doi:10.5281/ZENODO.7970649

---

## 11. Deutscher Wetterdienst (DWD)

**Organization:** German Weather Service
**Website:** https://www.dwd.de/
**Model:** ICON wave forecast — powers the Open-Meteo Marine API

**License:** Open data via Open-Meteo. Attribution required.

---

## 12. NOAA — National Oceanic and Atmospheric Administration

**Organization:** United States Department of Commerce — NOAA
**Website:** https://www.noaa.gov/
**CO-OPS API:** https://tidesandcurrents.noaa.gov/api/

**What we downloaded:**
- (Accessed for methodology reference; primary data from Copernicus and DFO)

**License:** Public domain (U.S. government).

---

## 13. Ocean Networks Canada (ONC)

**Organization:** University of Victoria / Ocean Networks Canada
**Website:** https://www.oceannetworks.ca/
**Data portal:** https://data.oceannetworks.ca/

**Note:** ONC operates cabled observatories on the Pacific and Arctic coasts — not directly relevant to Scotian Shelf. We referenced their Oceans 3.0 API methodology for data integration patterns.

**License:** CC-BY 4.0. Free API token.

---

## 14. Dalhousie University / Ocean Tracking Network (OTN)

**Organization:** Dalhousie University (Halifax, Nova Scotia)
**Website:** https://oceantrackingnetwork.org/
**ERDDAP:** https://members.oceantrack.org/erddap/

**What we downloaded:**
- OTN acoustic animal detection data for broader NW Atlantic
- Receiver station metadata

**License:** CC-BY 4.0.

---

## 15. Canada-Nova Scotia Offshore Petroleum Board (CNSOPB)

**Organization:** CNSOPB — joint federal-provincial regulatory agency
**Website:** https://www.cnsopb.ns.ca/

**Note:** Lease block and offshore energy spatial data. Referenced for governance constraint layers in the MPA optimization.

---

## 16. Natural Resources Canada (NRCan) / Geological Survey of Canada (GSC)

**Organization:** Government of Canada — Natural Resources Canada
**Website:** https://www.nrcan.gc.ca/

**Relevance:** Scotian Shelf surficial geology / sediment maps — referenced for sediment grain size data. Open File reports available but not API-accessible. Flagged as a data gap in the platform.

---

## Summary Table

| # | Organization | Country | Data Accessed | Auth | License |
|---|-------------|---------|---------------|------|---------|
| 1 | Copernicus Marine / Mercator Ocean | EU | 3D physics, waves, BGC | Free registration | Copernicus |
| 2 | Copernicus CDS / ECMWF | EU | ERA5 atmosphere, waves | Free registration | Copernicus |
| 3 | HYCOM Consortium / US Navy | USA | Ocean reanalysis | None | Public domain |
| 4 | DFO / BIO | Canada | CTD, nutrients, MPA layers | None | Open Gov't Canada |
| 5 | ECCC / MSC | Canada | Buoy observations, forecasts | None | Open Gov't Canada |
| 6 | SmartAtlantic / COVE | Canada | Halifax buoy network | None | Open data |
| 7 | OBIS / UNESCO IOC | International | Biodiversity records | None | CC-BY 4.0 |
| 8 | GEBCO / IHO | International | Bathymetry | None | Public domain |
| 9 | Global Fishing Watch | International | Vessel presence, fishing | Free token | CC-BY-SA 4.0 |
| 10 | Open-Meteo | Switzerland | Marine waves, atmosphere | None | CC-BY 4.0 |
| 11 | DWD | Germany | ICON wave model | None | Attribution |
| 12 | NOAA | USA | Tides, water levels | None | Public domain |
| 13 | ONC / UVic | Canada | Cabled observatory (method ref) | Free token | CC-BY 4.0 |
| 14 | OTN / Dalhousie | Canada | Acoustic telemetry | None | CC-BY 4.0 |
| 15 | CNSOPB | Canada | Offshore lease blocks | None | Open data |
| 16 | NRCan / GSC | Canada | Seabed geology (referenced) | None | Open Gov't Canada |

---

## Key Contacts for Data Attribution

**For the hackathon pitch/demo — acknowledge these organizations:**

> "Data sources include Copernicus Marine Service (EU), ECMWF ERA5, HYCOM Consortium (US Navy/NOPP), Fisheries and Oceans Canada (DFO/BIO), Environment and Climate Change Canada (ECCC), SmartAtlantic/COVE, OBIS/UNESCO, GEBCO/IHO, Global Fishing Watch, Open-Meteo/DWD, and the Ocean Tracking Network (Dalhousie University)."

**Primary regional data provider:**
Bedford Institute of Oceanography (BIO), Dartmouth, Nova Scotia — the central repository for Scotian Shelf oceanographic data and the Atlantic node of CIOOS.
