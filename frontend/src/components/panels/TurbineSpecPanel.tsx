import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

export default function TurbineSpecPanel() {
  const [isOpen, setIsOpen] = useState(false)
  
  const manualLat = useSimulationStore(state => state.manualLat)
  const manualLon = useSimulationStore(state => state.manualLon)
  const setManualLat = useSimulationStore(state => state.setManualLat)
  const setManualLon = useSimulationStore(state => state.setManualLon)
  const applyManualCoords = useSimulationStore(state => state.applyManualCoords)

  const windmillPos = useSimulationStore(state => state.windmillPosition)
  const windmillType = useSimulationStore(state => state.windmillType)
  const setWindmillType = useSimulationStore(state => state.setWindmillType)
  const turbineSpecs = useSimulationStore(state => state.turbineSpecs)
  const setTurbineSpecs = useSimulationStore(state => state.setTurbineSpecs)

  if (!isOpen) {
    return (
      <div 
        className="relative bg-white border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-md hover:bg-[#f5f5f5] transition-colors w-full"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-tertiary">wind_power</span>
        <span className="font-label-md text-label-md text-on-surface font-semibold flex-1">Turbine & Location</span>
        {windmillPos && (
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
          <span className="material-symbols-outlined text-tertiary">wind_power</span>
          Turbine & Location
        </h3>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <div className="p-stack-md flex flex-col gap-stack-md">
        
        {/* Placement Section */}
        <div className="flex flex-col gap-2">
          <h4 className="font-label-sm text-primary uppercase tracking-wider border-b border-outline-variant/50 pb-1">Placement</h4>
          <p className="text-body-sm text-on-surface-variant">Use the "Pin" tool above or enter coordinates manually.</p>
          <div className="flex gap-2">
            <div className="flex flex-col flex-1 gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Latitude °N</label>
              <input 
                type="text" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-2 text-on-surface font-body-md w-full focus:outline-none focus:border-primary"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                onBlur={applyManualCoords}
                onKeyDown={(e) => e.key === 'Enter' && applyManualCoords()}
                placeholder="e.g. 44.1"
              />
            </div>
            <div className="flex flex-col flex-1 gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Longitude °W</label>
              <input 
                type="text" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-2 text-on-surface font-body-md w-full focus:outline-none focus:border-primary"
                value={manualLon}
                onChange={(e) => setManualLon(e.target.value)}
                onBlur={applyManualCoords}
                onKeyDown={(e) => e.key === 'Enter' && applyManualCoords()}
                placeholder="e.g. -63.2"
              />
            </div>
          </div>
        </div>

        {/* Technical Specs Section */}
        <div className="flex flex-col gap-3 mt-2">
          <h4 className="font-label-sm text-primary uppercase tracking-wider border-b border-outline-variant/50 pb-1">Technical Specs</h4>
          
          <div className="flex flex-col gap-1">
            <label className="font-label-sm text-label-sm text-on-surface-variant">Turbine Model</label>
            <input 
              type="text" 
              className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
              value={turbineSpecs.model}
              onChange={(e) => setTurbineSpecs({ model: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="flex flex-col gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Rated Power (MW)</label>
              <input 
                type="number" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
                value={turbineSpecs.ratedPower}
                onChange={(e) => setTurbineSpecs({ ratedPower: parseFloat(e.target.value) })}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Hub Height (m)</label>
              <input 
                type="number" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
                value={turbineSpecs.hubHeight}
                onChange={(e) => setTurbineSpecs({ hubHeight: parseFloat(e.target.value) })}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Rotor Dia (m)</label>
              <input 
                type="number" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
                value={turbineSpecs.rotorDiameter}
                onChange={(e) => setTurbineSpecs({ rotorDiameter: parseFloat(e.target.value) })}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Cut-in (m/s)</label>
              <input 
                type="number" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
                value={turbineSpecs.cutInWindSpeed}
                onChange={(e) => setTurbineSpecs({ cutInWindSpeed: parseFloat(e.target.value) })}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Rated (m/s)</label>
              <input 
                type="number" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
                value={turbineSpecs.ratedWindSpeed}
                onChange={(e) => setTurbineSpecs({ ratedWindSpeed: parseFloat(e.target.value) })}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Cut-out (m/s)</label>
              <input 
                type="number" 
                className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
                value={turbineSpecs.cutOutWindSpeed}
                onChange={(e) => setTurbineSpecs({ cutOutWindSpeed: parseFloat(e.target.value) })}
              />
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <label className="font-label-sm text-label-sm text-on-surface-variant">Foundation Type</label>
            <input 
              type="text" 
              className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
              value={turbineSpecs.foundationType}
              onChange={(e) => setTurbineSpecs({ foundationType: e.target.value })}
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="font-label-sm text-label-sm text-on-surface-variant">Export Cable</label>
            <input 
              type="text" 
              className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
              value={turbineSpecs.exportCable}
              onChange={(e) => setTurbineSpecs({ exportCable: e.target.value })}
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="font-label-sm text-label-sm text-on-surface-variant">Power Coefficient (Cp)</label>
            <input 
              type="text" 
              className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
              value={turbineSpecs.cpPowerCoefficient}
              onChange={(e) => setTurbineSpecs({ cpPowerCoefficient: e.target.value })}
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="font-label-sm text-label-sm text-on-surface-variant">Thrust Coefficient (Ct)</label>
            <input 
              type="text" 
              className="bg-surface-variant border border-outline-variant rounded-DEFAULT px-3 py-1 text-on-surface font-body-md w-full"
              value={turbineSpecs.ctThrustCoefficient}
              onChange={(e) => setTurbineSpecs({ ctThrustCoefficient: e.target.value })}
            />
          </div>
        </div>

      </div>
    </div>
  )
}
