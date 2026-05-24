// import { useSimulationStore } from '../../store/simulationStore'

// export default function TurbineSpecPanel() {
//   const specs = useSimulationStore(state => state.turbineSpecs)
//   const setSpecs = useSimulationStore(state => state.setTurbineSpecs)
//   const windmillType = useSimulationStore(state => state.windmillType)

//   return (
//     <div className="absolute top-[480px] left-stack-md w-[320px] bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-md flex flex-col gap-stack-md shadow-sm z-20">
//       <div className="flex items-center justify-between border-b border-outline-variant pb-stack-sm">
//         <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
//           <span className="material-symbols-outlined text-secondary">wind_power</span>
//           Turbine Specs
//         </h3>
//         <span className="px-2 py-1 bg-surface-container-high rounded text-label-sm font-label-sm text-on-surface-variant uppercase">
//           {windmillType}
//         </span>
//       </div>
      
//       <div className="flex flex-col gap-stack-sm pt-2">
//         <div className="flex flex-col gap-1">
//           <div className="flex justify-between items-end">
//             <label className="font-label-sm text-label-sm text-on-surface">Hub Height (m)</label>
//             <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">{specs.hubHeight}</span>
//           </div>
//           <input 
//             className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-secondary" 
//             type="range" min="80" max="250" 
//             value={specs.hubHeight} 
//             onChange={e => setSpecs({ hubHeight: Number(e.target.value) })}
//           />
//         </div>

//         <div className="flex flex-col gap-1">
//           <div className="flex justify-between items-end">
//             <label className="font-label-sm text-label-sm text-on-surface">Rotor Diameter (m)</label>
//             <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">{specs.rotorDiameter}</span>
//           </div>
//           <input 
//             className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-secondary" 
//             type="range" min="100" max="300" 
//             value={specs.rotorDiameter} 
//             onChange={e => setSpecs({ rotorDiameter: Number(e.target.value) })}
//           />
//         </div>

//         {windmillType === 'floating' && (
//           <>
//             <div className="flex flex-col gap-1">
//               <div className="flex justify-between items-end">
//                 <label className="font-label-sm text-label-sm text-on-surface">Floater Radius (m)</label>
//                 <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">{specs.floaterRadius}</span>
//               </div>
//               <input 
//                 className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-secondary" 
//                 type="range" min="20" max="80" 
//                 value={specs.floaterRadius} 
//                 onChange={e => setSpecs({ floaterRadius: Number(e.target.value) })}
//               />
//             </div>
//           </>
//         )}

//         <div className="flex flex-col gap-1 mt-2">
//           <label className="font-label-sm text-label-sm text-on-surface">Material Grade</label>
//           <select 
//             value={specs.materialGrade}
//             onChange={e => setSpecs({ materialGrade: e.target.value })}
//             className="w-full bg-surface-container-low border border-outline-variant text-on-surface font-body-sm text-body-sm py-2 px-2 rounded focus:outline-none focus:border-secondary transition-all cursor-pointer"
//           >
//             <option value="s355">S355 Structural Steel</option>
//             <option value="s420">S420 High Strength</option>
//             <option value="s460">S460 Ultra High Strength</option>
//           </select>
//         </div>
//       </div>
//     </div>
//   )
// }


import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

const COORD_PRESETS = [
  { label: 'Scotian Shelf',  lat: 44.100, lon: -63.200 },
  { label: 'Cabot Strait',   lat: 47.300, lon: -59.800 },
  { label: 'Bay of Fundy',   lat: 44.800, lon: -66.100 },
  { label: 'Sable Island',   lat: 43.934, lon: -60.010 },
]

function SliderRow({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  unit?: string
  onChange: (v: number) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-end">
        <label className="font-label-sm text-[11px] text-on-surface">{label}</label>
        <span className="font-label-sm text-[11px] font-mono text-on-surface-variant font-semibold">
          {value}{unit ?? ''}
        </span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-secondary"
      />
    </div>
  )
}

export default function TurbineSpecPanel() {
  const [isOpen, setIsOpen] = useState(true)
  const [placedFeedback, setPlacedFeedback] = useState(false)

  const specs       = useSimulationStore((s) => s.turbineSpecs)
  const setSpecs    = useSimulationStore((s) => s.setTurbineSpecs)
  const windmillType = useSimulationStore((s) => s.windmillType)
  const setType     = useSimulationStore((s) => s.setWindmillType)

  const manualLat   = useSimulationStore((s) => s.manualLat)
  const manualLon   = useSimulationStore((s) => s.manualLon)
  const setManualLat = useSimulationStore((s) => s.setManualLat)
  const setManualLon = useSimulationStore((s) => s.setManualLon)
  const applyCoords = useSimulationStore((s) => s.applyManualCoords)
  const windmillPos  = useSimulationStore((s) => s.windmillPosition)

  const handleApply = () => {
    applyCoords()
    setPlacedFeedback(true)
    setTimeout(() => setPlacedFeedback(false), 2000)
  }

  if (!isOpen) {
    return (
      <div
        className="absolute top-[480px] left-stack-md bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-sm z-20 hover:bg-surface-variant transition-colors"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-secondary">wind_power</span>
        <span className="font-label-md text-label-md text-on-surface">Turbine & Location</span>
      </div>
    )
  }

  return (
    <div className="absolute top-[480px] left-stack-md w-[320px] max-h-[calc(100vh-520px)] flex flex-col bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl shadow-sm z-20 overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-surface flex-shrink-0">
        <h3 className="font-headline-sm font-semibold text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-secondary">wind_power</span>
          Turbine & Location
        </h3>
        <button
          onClick={() => setIsOpen(false)}
          className="text-on-surface-variant hover:text-on-surface"
        >
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-stack-md flex flex-col gap-stack-sm">

        {/* Foundation type toggle */}
        <div>
          <p className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant mb-1.5">
            Foundation type
          </p>
          <div className="flex gap-1 bg-surface-container-high rounded-lg p-1">
            {(['grounded', 'floating'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setType(t)}
                className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md text-[12px] font-semibold transition-all ${
                  windmillType === t
                    ? 'bg-surface text-secondary shadow-sm border border-outline-variant'
                    : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[15px]">
                  {t === 'grounded' ? 'anchor' : 'water'}
                </span>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
          <div className="mt-1.5 flex justify-end">
            <span className="text-[10px] px-1.5 py-0.5 bg-surface-container rounded font-label-sm text-on-surface-variant uppercase tracking-wide">
              {windmillType}
            </span>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-outline-variant" />

        {/* Specs */}
        <SliderRow
          label="Hub height (m)"
          value={specs.hubHeight}
          min={80} max={250} step={1}
          onChange={(v) => setSpecs({ hubHeight: v })}
        />
        <SliderRow
          label="Rotor diameter (m)"
          value={specs.rotorDiameter}
          min={100} max={300} step={1}
          onChange={(v) => setSpecs({ rotorDiameter: v })}
        />
        <SliderRow
          label="Rated power (MW)"
          value={specs.ratedPower}
          min={3} max={20} step={0.5}
          unit=" MW"
          onChange={(v) => setSpecs({ ratedPower: v })}
        />

        {/* Floating-only fields */}
        {windmillType === 'floating' && (
          <>
            <div className="border-t border-outline-variant" />
            <p className="font-label-sm text-[10px] uppercase tracking-wider text-tertiary">
              Floating platform
            </p>
            <SliderRow
              label="Floater radius (m)"
              value={specs.floaterRadius}
              min={20} max={80} step={1}
              onChange={(v) => setSpecs({ floaterRadius: v })}
            />
            <SliderRow
              label="Column diameter (m)"
              value={specs.columnDiameter}
              min={6} max={25} step={0.5}
              onChange={(v) => setSpecs({ columnDiameter: v })}
            />
          </>
        )}

        {/* Material grade */}
        <div className="flex flex-col gap-1">
          <label className="font-label-sm text-[11px] text-on-surface">Material grade</label>
          <select
            value={specs.materialGrade}
            onChange={(e) => setSpecs({ materialGrade: e.target.value })}
            className="w-full bg-surface-container-low border border-outline-variant text-on-surface text-[12px] py-2 px-2 rounded-lg focus:outline-none focus:border-secondary transition-all cursor-pointer"
          >
            <option value="s355">S355 Structural Steel</option>
            <option value="s420">S420 High Strength</option>
            <option value="s460">S460 Ultra High Strength</option>
          </select>
        </div>

        {/* Divider */}
        <div className="border-t border-outline-variant" />

        {/* Manual coordinates */}
        <div>
          <p className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant mb-2">
            Manual coordinates
          </p>

          {/* Preset buttons */}
          <div className="flex flex-wrap gap-1.5 mb-3">
            {COORD_PRESETS.map((p) => (
              <button
                key={p.label}
                onClick={() => {
                  setManualLat(p.lat.toFixed(3))
                  setManualLon(p.lon.toFixed(3))
                }}
                className="text-[10px] px-2 py-1 rounded-md border border-outline-variant bg-surface-container-low text-on-surface-variant hover:border-secondary hover:text-secondary hover:bg-surface-container transition-all font-semibold"
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Lat / Lon inputs */}
          <div className="flex gap-2 mb-2">
            <div className="flex-1 flex flex-col gap-1">
              <label className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant">
                Latitude °N
              </label>
              <input
                type="number"
                step="0.001"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                placeholder="44.100"
                className="w-full px-2.5 py-1.5 rounded-lg border border-outline-variant bg-surface-container-low text-on-surface text-[12px] focus:border-secondary focus:outline-none transition-colors"
              />
            </div>
            <div className="flex-1 flex flex-col gap-1">
              <label className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant">
                Longitude °W
              </label>
              <input
                type="number"
                step="0.001"
                value={manualLon}
                onChange={(e) => setManualLon(e.target.value)}
                placeholder="-63.200"
                className="w-full px-2.5 py-1.5 rounded-lg border border-outline-variant bg-surface-container-low text-on-surface text-[12px] focus:border-secondary focus:outline-none transition-colors"
              />
            </div>
          </div>

          {/* Current position badge */}
          {windmillPos && (
            <div className="flex items-center gap-1.5 mb-2 px-2 py-1.5 rounded-lg bg-surface-container border border-outline-variant">
              <span className="material-symbols-outlined text-[13px] text-primary">location_on</span>
              <span className="text-[11px] text-on-surface-variant font-mono">
                {windmillPos.lat.toFixed(3)}°N, {Math.abs(windmillPos.lon).toFixed(3)}°W
              </span>
              <span className="ml-auto text-[9px] bg-primary-container text-on-primary-container px-1.5 py-0.5 rounded font-semibold">
                Active
              </span>
            </div>
          )}

          {/* Info note */}
          <div className="flex items-start gap-1.5 mb-2">
            <span className="material-symbols-outlined text-[12px] text-on-surface-variant mt-0.5">info</span>
            <p className="text-[10px] text-on-surface-variant leading-relaxed">
              You can also click the globe to place the pin. Coordinates update automatically.
            </p>
          </div>

          {/* Place turbine button */}
          <button
            onClick={handleApply}
            className={`w-full py-2 rounded-lg text-[12px] font-bold flex items-center justify-center gap-1.5 transition-all ${
              placedFeedback
                ? 'bg-on-primary-fixed-variant text-on-primary'
                : 'bg-secondary text-on-secondary hover:opacity-90'
            }`}
          >
            <span className="material-symbols-outlined text-[15px]">
              {placedFeedback ? 'check' : 'push_pin'}
            </span>
            {placedFeedback ? 'Turbine placed!' : 'Place Turbine'}
          </button>
        </div>
      </div>
    </div>
  )
}
