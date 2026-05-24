import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

export default function RegionPanel() {
  const [isOpen, setIsOpen] = useState(false)
  const regionBounds = useSimulationStore(state => state.regionBounds)

  if (!isOpen) {
    return (
      <div 
        className="relative bg-white border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-md hover:bg-[#f5f5f5] transition-colors w-full"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-tertiary">map</span>
        <span className="font-label-md text-label-md text-on-surface font-semibold flex-1">Simulation Region</span>
        {regionBounds && (
          <span className="material-symbols-outlined text-green-600 text-[18px]">check_circle</span>
        )}
      </div>
    )
  }

  return (
    <div className="relative w-full flex flex-col bg-white border border-outline-variant rounded-xl shadow-xl overflow-hidden transition-all duration-200">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-white">
        <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-tertiary">map</span>
          Simulation Region
        </h3>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <div className="p-stack-md flex flex-col gap-stack-md">
        <div className="flex items-center gap-2 mb-2">
          <span className="material-symbols-outlined text-primary">info</span>
          <p className="text-body-sm text-on-surface-variant">
            Use the "Bounds" tool to click exactly 4 points on the map to define an arbitrary polygon environment.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-stack-md">
          {[1, 2, 3, 4].map(idx => {
            const pt = regionBounds && regionBounds[idx - 1]
            return (
              <div key={idx} className="flex flex-col gap-1">
                <label className="font-label-sm text-label-sm text-on-surface-variant">Point {idx}</label>
                <input 
                  className="bg-surface-variant border-none rounded-DEFAULT px-3 py-2 text-on-surface font-body-md"
                  type="text" 
                  readOnly 
                  value={pt ? `${pt.lat.toFixed(3)}°, ${pt.lon.toFixed(3)}°` : '---'} 
                />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
