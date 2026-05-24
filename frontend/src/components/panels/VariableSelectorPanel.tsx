import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

export default function VariableSelectorPanel() {
  const [isOpen, setIsOpen] = useState(false)
  
  const selectedVariables = useSimulationStore(state => state.selectedVariables)
  const toggleVariable = useSimulationStore(state => state.toggleVariable)

  const mockGroups = [
    { 
      id: 'physics_3d', 
      name: '1. Physics: 3D Water Column', 
      vars: [
        { id: '1.1', name: 'Potential temperature' },
        { id: '1.2', name: 'Water temperature' },
        { id: '1.3', name: 'In-situ temperature' },
        { id: '1.4', name: 'Sea surface temperature' },
        { id: '1.5', name: 'Practical salinity' },
        { id: '1.6', name: 'Salinity' },
        { id: '1.7', name: 'In-situ salinity' },
        { id: '1.8', name: 'Eastward velocity' },
        { id: '1.9', name: 'Northward velocity' },
        { id: '1.10', name: 'Current speed at 20 depth levels' },
        { id: '1.11', name: 'Current direction at 20 depth levels' },
        { id: '1.12', name: 'Upward velocity' },
        { id: '1.13', name: 'Surface current (Euler+tide+Stokes)' },
        { id: '1.14', name: 'Surface current velocity' },
        { id: '1.15', name: 'Surface current direction' },
        { id: '1.16', name: 'Barotropic velocity' },
        { id: '1.17', name: 'Potential density (sigma-theta)' },
        { id: '1.18', name: 'Vertical eddy diffusivity' },
        { id: '1.19', name: 'Vertical eddy viscosity' }
      ] 
    },
    { 
      id: 'physics_surface', 
      name: '2. Physics: Surface & Sea Level', 
      vars: [
        { id: '2.1', name: 'Sea surface height above geoid' },
        { id: '2.2', name: 'Sea surface height' },
        { id: '2.3', name: 'Steric SSH' },
        { id: '2.4', name: 'Sea level height (tide+IB+steric+mass)' },
        { id: '2.5', name: 'Inverse barometer height' },
        { id: '2.6', name: 'Tide height' },
        { id: '2.7', name: 'Mixed layer depth (sigma-theta)' },
        { id: '2.8', name: 'Mixed layer thickness' },
        { id: '2.9', name: 'Surface boundary layer thickness' },
        { id: '2.10', name: 'Bottom temperature' },
        { id: '2.11', name: 'Bottom salinity' },
        { id: '2.12', name: 'Sea ice concentration' },
        { id: '2.13', name: 'Sea ice thickness' },
        { id: '2.14', name: 'Sea ice velocity' }
      ] 
    },
    { 
      id: 'waves_stokes', 
      name: '3. Waves & Stokes Drift', 
      vars: [
        { id: '3.1', name: 'Significant wave height' },
        { id: '3.2', name: 'Peak wave period' },
        { id: '3.3', name: 'Mean wave period' },
        { id: '3.4', name: 'Mean wave direction' },
        { id: '3.5', name: 'Peak wave direction' },
        { id: '3.6', name: 'Wind sea significant height' },
        { id: '3.7', name: 'Wind sea direction' },
        { id: '3.8', name: 'Wind sea period' },
        { id: '3.9', name: 'Primary swell height' },
        { id: '3.10', name: 'Primary swell direction' },
        { id: '3.11', name: 'Primary swell period' },
        { id: '3.12', name: 'Secondary swell height' },
        { id: '3.13', name: 'Tertiary swell height/period/dir' },
        { id: '3.14', name: 'Swell partitions 1–3' },
        { id: '3.15', name: 'Stokes drift (eastward)' },
        { id: '3.16', name: 'Stokes drift (northward)' },
        { id: '3.17', name: 'Stokes drift (u/v)' },
        { id: '3.18', name: 'Maximum wave height' },
        { id: '3.19', name: 'Max crest height' },
        { id: '3.20', name: 'Wave directional spread' },
        { id: '3.21', name: 'Wave energy flux into ocean' },
        { id: '3.22', name: 'Normalized stress into ocean' },
        { id: '3.23', name: 'Drag coefficient with waves' }
      ] 
    },
    { 
      id: 'atmospheric_forcing', 
      name: '4. Atmospheric Forcing', 
      vars: [
        { id: '4.1', name: '10m eastward wind' },
        { id: '4.2', name: '10m northward wind' },
        { id: '4.3', name: '10m wind speed' },
        { id: '4.4', name: '10m wind direction' },
        { id: '4.5', name: '100m wind speed' },
        { id: '4.6', name: '100m wind direction' },
        { id: '4.7', name: '10m wind gust' },
        { id: '4.8', name: '2m air temperature' },
        { id: '4.9', name: '2m dewpoint' },
        { id: '4.10', name: 'Mean sea level pressure' },
        { id: '4.11', name: 'Surface pressure' },
        { id: '4.12', name: 'Relative humidity' },
        { id: '4.13', name: 'Total cloud cover' },
        { id: '4.14', name: 'Low/mid/high cloud cover' },
        { id: '4.15', name: 'Precipitation' },
        { id: '4.16', name: 'Snowfall' },
        { id: '4.17', name: 'Boundary layer height' },
        { id: '4.18', name: 'Surface roughness' },
        { id: '4.19', name: 'Friction velocity' },
        { id: '4.20', name: 'Solar radiation (shortwave)' },
        { id: '4.21', name: 'Direct/diffuse radiation' },
        { id: '4.22', name: 'Evapotranspiration' },
        { id: '4.23', name: 'Vapour pressure deficit' }
      ] 
    },
    {
      id: 'surface_fluxes',
      name: '5. Surface Fluxes',
      vars: [
        { id: '5.1', name: 'Eastward turbulent surface stress' },
        { id: '5.2', name: 'Northward turbulent surface stress' },
        { id: '5.3', name: 'Surface latent heat flux' },
        { id: '5.4', name: 'Surface sensible heat flux' },
        { id: '5.5', name: 'Net shortwave radiation flux' },
        { id: '5.6', name: 'Net longwave radiation flux' },
        { id: '5.7', name: 'Downward shortwave flux' },
        { id: '5.8', name: 'Downward longwave flux' },
        { id: '5.9', name: 'Total precipitation' },
        { id: '5.10', name: 'Evaporation' },
        { id: '5.11', name: 'Mean precipitation rate' },
        { id: '5.12', name: 'Mean evaporation rate' },
        { id: '5.13', name: 'Net surface heat flux' },
        { id: '5.14', name: 'Evaporation minus precipitation' },
        { id: '5.15', name: 'Surface wind stress' }
      ]
    },
    {
      id: 'tides',
      name: '6. Tides',
      vars: [
        { id: '6.1', name: 'Tidal elevation (constituents)' },
        { id: '6.2', name: 'Tidal current (u/v, constituents)' },
        { id: '6.3', name: 'Tidal elevation (global)' },
        { id: '6.4', name: 'Tidal current (u/v component)' },
        { id: '6.5', name: 'Tide height (Halifax)' }
      ]
    },
    {
      id: 'mixing_turbulence',
      name: '7. Mixing & Turbulence',
      vars: [
        { id: '7.1', name: 'Vertical eddy diffusivity' },
        { id: '7.2', name: 'Vertical eddy viscosity' },
        { id: '7.3', name: 'Turbulent kinetic energy' },
        { id: '7.4', name: 'Mixed layer depth' },
        { id: '7.5', name: 'Brunt-Väisälä frequency' },
        { id: '7.6', name: 'Richardson number' }
      ]
    },
    {
      id: 'biogeochemistry',
      name: '8. Biogeochemistry',
      vars: [
        { id: '8.1', name: 'Chlorophyll-a concentration' },
        { id: '8.2', name: 'Chlorophyll-a' },
        { id: '8.3', name: 'Chlorophyll-a (satellite)' },
        { id: '8.4', name: 'Nitrate' },
        { id: '8.5', name: 'Phosphate' },
        { id: '8.6', name: 'Silicate' },
        { id: '8.7', name: 'Dissolved iron' },
        { id: '8.8', name: 'Dissolved oxygen' },
        { id: '8.9', name: 'pH (total scale)' },
        { id: '8.10', name: 'Surface pCO2' },
        { id: '8.11', name: 'Dissolved inorganic carbon' },
        { id: '8.12', name: 'Total alkalinity' },
        { id: '8.13', name: 'Net primary production' },
        { id: '8.14', name: 'Phytoplankton carbon' },
        { id: '8.15', name: 'Zooplankton carbon' },
        { id: '8.16', name: 'Light attenuation coefficient' },
        { id: '8.17', name: 'Ammonia' },
        { id: '8.18', name: 'POC / PON' },
        { id: '8.19', name: 'HPLC phytoplankton pigments (18 types)' },
        { id: '8.20', name: 'CDOM' },
        { id: '8.21', name: 'Turbidity' },
        { id: '8.22', name: 'Optical: PAR, transmittance, attenuation' }
      ]
    },
    {
      id: 'biology_species',
      name: '9. Biology & Species',
      vars: [
        { id: '9.1', name: 'Species occurrence records' },
        { id: '9.2', name: 'Scientific name' },
        { id: '9.3', name: 'Individual count / abundance' },
        { id: '9.4', name: 'Observation depth' },
        { id: '9.5', name: 'Fish length/weight (MoF)' },
        { id: '9.6', name: 'Maturity stage / sex (MoF)' },
        { id: '9.7', name: 'Acoustic animal detections' },
        { id: '9.8', name: 'Receiver station metadata' },
        { id: '9.9', name: 'North Atlantic Right Whale sightings' }
      ]
    },
    {
      id: 'seafloor',
      name: '10. Seafloor',
      vars: [
        { id: '10.1', name: 'Bathymetry / elevation' },
        { id: '10.2', name: 'Model bathymetry' },
        { id: '10.3', name: 'Seafloor sediment type' },
        { id: '10.4', name: 'Grain size distribution' }
      ]
    },
    {
      id: 'human_activity',
      name: '11. Human Activity',
      vars: [
        { id: '11.1', name: 'Vessel presence hours (gridded)' },
        { id: '11.2', name: 'Fishing effort by gear type' },
        { id: '11.3', name: 'Vessel position (real-time)' },
        { id: '11.4', name: 'Vessel type (cargo/tanker/fishing)' },
        { id: '11.5', name: 'Shipping lanes (density)' },
        { id: '11.6', name: 'Fishing zones / closures' }
      ]
    },
    {
      id: 'governance',
      name: '12. Governance & Spatial Planning',
      vars: [
        { id: '12.1', name: 'Marine Protected Areas (Oceans Act)' },
        { id: '12.2', name: 'Marine refuges / other effective area-based conservation measures (OECMs)' },
        { id: '12.3', name: 'Critical habitat (Species at Risk Act)' },
        { id: '12.4', name: 'Lease blocks (oil & gas, offshore wind)' },
        { id: '12.5', name: 'Renewable energy areas' },
        { id: '12.6', name: 'Aquaculture sites' },
        { id: '12.7', name: 'Submarine cables' },
        { id: '12.8', name: 'Dumping / disposal sites' },
        { id: '12.9', name: 'Navigational aids / traffic separation' }
      ]
    },
    {
      id: 'derived',
      name: '13. Derived & Computed Variables',
      vars: [
        { id: '13.1', name: 'Sound speed' },
        { id: '13.2', name: 'Brunt-Väisälä frequency' },
        { id: '13.3', name: 'Richardson number' },
        { id: '13.4', name: 'Potential density' },
        { id: '13.5', name: 'Lagrangian trajectory' },
        { id: '13.6', name: 'Habitat suitability index' },
        { id: '13.7', name: 'Species probability of occurrence' },
        { id: '13.8', name: 'Acoustic transmission loss' },
        { id: '13.9', name: 'Wind power density' },
        { id: '13.10', name: 'Multi-objective Pareto frontier' },
        { id: '13.11', name: 'Ship strike risk' },
        { id: '13.12', name: 'Uncertainty ensemble spread' }
      ]
    }
  ]

  if (!isOpen) {
    return (
      <div 
        className="relative bg-white border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-md hover:bg-[#f5f5f5] transition-colors w-full"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-tertiary">public</span>
        <span className="font-label-md text-label-md text-on-surface font-semibold flex-1">Environmental Variables</span>
        {selectedVariables.length > 0 && (
          <span className="ml-2 w-5 h-5 bg-primary text-on-primary rounded-full flex items-center justify-center text-[10px] font-bold">
            {selectedVariables.length}
          </span>
        )}
      </div>
    )
  }

  return (
    <div className="relative w-full flex flex-col bg-white border border-outline-variant rounded-xl shadow-xl overflow-hidden transition-all duration-200">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-white flex-shrink-0">
        <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-tertiary">public</span>
          Environmental Variables
        </h3>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <div className="max-h-[400px] overflow-y-auto custom-scrollbar p-4 flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          {mockGroups.map((group) => (
            <details key={group.id} className="group/section" open={group.id === 'physics_3d'}>
              <summary className="flex items-center justify-between font-label-sm text-primary uppercase tracking-wider cursor-pointer py-1 border-b border-outline-variant/30 list-none">
                <span>{group.name}</span>
                <span className="material-symbols-outlined text-sm group-open/section:rotate-180 transition-transform">expand_more</span>
              </summary>
              <div className="flex flex-col gap-2 mt-2 pl-2">
                {group.vars.map(v => (
                  <label key={v.id} className="flex items-center gap-2 font-body-md text-on-surface cursor-pointer text-sm">
                    <input 
                      type="checkbox" 
                      checked={selectedVariables.includes(v.id)}
                      onChange={() => toggleVariable(v.id)}
                      className="rounded border-outline-variant text-primary focus:ring-primary h-3 w-3"
                    /> 
                    {v.name}
                  </label>
                ))}
              </div>
            </details>
          ))}
        </div>
      </div>
    </div>
  )
}
