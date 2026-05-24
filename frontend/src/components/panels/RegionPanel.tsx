import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

export default function RegionPanel() {
  const [isOpen, setIsOpen] = useState(true)
  const regionBounds = useSimulationStore(state => state.regionBounds)
  const setRegionBounds = useSimulationStore(state => state.setRegionBounds)

  if (!regionBounds) return null

  const handleBoundChange = (corner: 'southwest' | 'northeast', axis: 'lat' | 'lon', value: string) => {
    // Allows typing '-' or empty before parsing
    if (value === '' || value === '-') {
       // We'll temporarily allow string in state if we were typing, but input type="number" returns empty string when invalid.
       // Let's just handle parsefloat. For a smooth typing experience with numbers, 
       // it's tricky, but standard HTML number inputs handle '-' internally.
    }
    
    const num = parseFloat(value)
    if (isNaN(num)) return

    setRegionBounds({
      ...regionBounds,
      [corner]: {
        ...regionBounds[corner],
        [axis]: num
      }
    })
  }

  if (!isOpen) {
    return (
      <div 
        className="absolute top-[480px] right-stack-md bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-sm z-20 hover:bg-surface-variant transition-colors"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-primary">map</span>
        <span className="font-label-md text-label-md text-on-surface">Simulation Region</span>
      </div>
    )
  }

  return (
    <div className="absolute top-[480px] right-stack-md w-[320px] bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-md flex flex-col gap-stack-md shadow-sm z-20">
      <div className="flex items-center justify-between border-b border-outline-variant pb-stack-sm">
        <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-secondary">map</span>
          Simulation Region
        </h3>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>
      
      <div className="flex flex-col gap-stack-sm pt-2">
        
        <div className="flex flex-col gap-1">
          <label className="font-label-sm text-label-sm text-on-surface font-semibold">Southwest Corner (Lat, Lon)</label>
          <div className="flex gap-2">
            <input 
              type="number"
              step="0.01"
              value={regionBounds.southwest.lat}
              onChange={(e) => handleBoundChange('southwest', 'lat', e.target.value)}
              placeholder="Lat"
              className="w-1/2 bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-1 px-2 rounded focus:outline-none focus:border-secondary transition-all"
            />
            <input 
              type="number"
              step="0.01"
              value={regionBounds.southwest.lon}
              onChange={(e) => handleBoundChange('southwest', 'lon', e.target.value)}
              placeholder="Lon"
              className="w-1/2 bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-1 px-2 rounded focus:outline-none focus:border-secondary transition-all"
            />
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <label className="font-label-sm text-label-sm text-on-surface font-semibold">Northeast Corner (Lat, Lon)</label>
          <div className="flex gap-2">
            <input 
              type="number"
              step="0.01"
              value={regionBounds.northeast.lat}
              onChange={(e) => handleBoundChange('northeast', 'lat', e.target.value)}
              placeholder="Lat"
              className="w-1/2 bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-1 px-2 rounded focus:outline-none focus:border-secondary transition-all"
            />
            <input 
              type="number"
              step="0.01"
              value={regionBounds.northeast.lon}
              onChange={(e) => handleBoundChange('northeast', 'lon', e.target.value)}
              placeholder="Lon"
              className="w-1/2 bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-1 px-2 rounded focus:outline-none focus:border-secondary transition-all"
            />
          </div>
        </div>

      </div>
    </div>
  )
}
