import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

export default function AnalysisMethodsPanel() {
  const [isOpen, setIsOpen] = useState(false)
  
  const selectedTools = useSimulationStore(state => state.selectedTools)
  const toggleTool = useSimulationStore(state => state.toggleTool)
  
  const availableTools = [
    { id: 'gaussian_wake', name: 'Gaussian Wake Model', icon: 'air', desc: 'Predict wind speed deficit downwind' },
    { id: 'acoustic', name: 'Acoustic Propagation', icon: 'volume_up', desc: 'Noise impact from pile driving' },
    { id: 'scour', name: 'Scour Prediction', icon: 'waves', desc: 'Seabed erosion around foundations' },
    { id: 'lagrangian', name: 'Lagrangian Particle Tracking', icon: 'scatter_plot', desc: 'Track spills or larval dispersal' },
    { id: 'maxent', name: 'Habitat Suitability (MaxEnt)', icon: 'biotech', desc: 'Predict species distribution' },
  ]

  if (!isOpen) {
    return (
      <div 
        className="relative bg-white border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-md hover:bg-[#f5f5f5] transition-colors w-full"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-tertiary">science</span>
        <span className="font-label-md text-label-md text-on-surface font-semibold flex-1">Analysis Methods</span>
        {selectedTools.length > 0 && (
          <span className="ml-2 w-5 h-5 bg-primary text-on-primary rounded-full flex items-center justify-center text-[10px] font-bold">
            {selectedTools.length}
          </span>
        )}
      </div>
    )
  }

  return (
    <div className="relative w-full flex flex-col bg-white border border-outline-variant rounded-xl shadow-xl overflow-hidden transition-all duration-200">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-white">
        <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-tertiary">science</span>
          Analysis Methods
        </h3>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <div className="p-stack-md flex flex-col gap-stack-sm">
        {availableTools.map(tool => {
          const isSelected = selectedTools.includes(tool.id)
          return (
            <div 
              key={tool.id} 
              className={`p-stack-sm border rounded-lg cursor-pointer transition-colors ${isSelected ? 'border-primary bg-primary/5' : 'border-outline-variant hover:border-outline'}`}
              onClick={() => toggleTool(tool.id)}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className={`material-symbols-outlined text-[20px] ${isSelected ? 'text-primary' : 'text-on-surface-variant'}`}>{tool.icon}</span>
                <span className={`font-label-md ${isSelected ? 'text-primary font-bold' : 'text-on-surface'}`}>{tool.name}</span>
              </div>
              <p className="text-[11px] text-on-surface-variant pl-7">{tool.desc}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
