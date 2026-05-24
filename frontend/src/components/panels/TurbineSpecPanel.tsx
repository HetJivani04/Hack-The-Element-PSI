import { useSimulationStore } from '../../store/simulationStore'

export default function TurbineSpecPanel() {
  const specs = useSimulationStore(state => state.turbineSpecs)
  const setSpecs = useSimulationStore(state => state.setTurbineSpecs)
  const windmillType = useSimulationStore(state => state.windmillType)
  const windmillPos = useSimulationStore(state => state.windmillPosition)
  const setWindmillPos = useSimulationStore(state => state.setWindmillPosition)

  const handleLatChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const lat = parseFloat(e.target.value)
    if (!isNaN(lat)) {
      setWindmillPos({ lat, lon: windmillPos?.lon ?? -63.0 })
    }
  }

  const handleLonChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const lon = parseFloat(e.target.value)
    if (!isNaN(lon)) {
      setWindmillPos({ lat: windmillPos?.lat ?? 44.0, lon })
    }
  }

  return (
    <div className="absolute top-[480px] left-stack-md w-[320px] bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-md flex flex-col gap-stack-md shadow-sm z-20">
      <div className="flex items-center justify-between border-b border-outline-variant pb-stack-sm">
        <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-secondary">wind_power</span>
          Turbine Specs
        </h3>
        <span className="px-2 py-1 bg-surface-container-high rounded text-label-sm font-label-sm text-on-surface-variant uppercase">
          {windmillType}
        </span>
      </div>
      
      <div className="flex flex-col gap-stack-sm pt-2">
        {/* Location Input Section */}
        <div className="flex flex-col gap-1 pb-2 border-b border-outline-variant">
          <label className="font-label-sm text-label-sm text-on-surface">Location (Lat, Lon)</label>
          <div className="flex gap-2">
            <input 
              type="number"
              step="0.01"
              value={windmillPos?.lat ?? ''}
              onChange={handleLatChange}
              placeholder="Latitude"
              className="w-1/2 bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-1 px-2 rounded focus:outline-none focus:border-secondary transition-all"
            />
            <input 
              type="number"
              step="0.01"
              value={windmillPos?.lon ?? ''}
              onChange={handleLonChange}
              placeholder="Longitude"
              className="w-1/2 bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-1 px-2 rounded focus:outline-none focus:border-secondary transition-all"
            />
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex justify-between items-end">
            <label className="font-label-sm text-label-sm text-on-surface">Hub Height (m)</label>
            <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">{specs.hubHeight}</span>
          </div>
          <input 
            className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-secondary" 
            type="range" min="80" max="250" 
            value={specs.hubHeight} 
            onChange={e => setSpecs({ hubHeight: Number(e.target.value) })}
          />
        </div>

        <div className="flex flex-col gap-1">
          <div className="flex justify-between items-end">
            <label className="font-label-sm text-label-sm text-on-surface">Rotor Diameter (m)</label>
            <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">{specs.rotorDiameter}</span>
          </div>
          <input 
            className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-secondary" 
            type="range" min="100" max="300" 
            value={specs.rotorDiameter} 
            onChange={e => setSpecs({ rotorDiameter: Number(e.target.value) })}
          />
        </div>

        {windmillType === 'floating' && (
          <>
            <div className="flex flex-col gap-1">
              <div className="flex justify-between items-end">
                <label className="font-label-sm text-label-sm text-on-surface">Floater Radius (m)</label>
                <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">{specs.floaterRadius}</span>
              </div>
              <input 
                className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-secondary" 
                type="range" min="20" max="80" 
                value={specs.floaterRadius} 
                onChange={e => setSpecs({ floaterRadius: Number(e.target.value) })}
              />
            </div>
          </>
        )}

        <div className="flex flex-col gap-1 mt-2">
          <label className="font-label-sm text-label-sm text-on-surface">Material Grade</label>
          <select 
            value={specs.materialGrade}
            onChange={e => setSpecs({ materialGrade: e.target.value })}
            className="w-full bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-2 px-2 rounded focus:outline-none focus:border-secondary transition-all cursor-pointer"
          >
            <option value="s355">S355 Structural Steel</option>
            <option value="s420">S420 High Strength</option>
            <option value="s460">S460 Ultra High Strength</option>
          </select>
        </div>
      </div>
    </div>
  )
}
