import { useState } from 'react'
import { ChevronDown, ChevronRight, Check } from 'lucide-react'

import { useSimulationStore } from '../../store/simulationStore'

export default function VariableSelectorPanel() {
  const [isOpen, setIsOpen] = useState(true)
  const [expandedGroups, setExpandedGroups] = useState<string[]>([])
  

  const selectedVariables = useSimulationStore(state => state.selectedVariables)
  const toggleVariable = useSimulationStore(state => state.toggleVariable)

  // Assuming variableData has domains array and actual variables mapping
  // Since our mock GET /api/variables isn't fully returning the 169 vars yet, we'll mock the UI.

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupId) ? prev.filter(id => id !== groupId) : [...prev, groupId]
    )
  }

  const mockGroups = [
    { id: 'physics', name: '3D Physics', vars: [{id: '1.12', name: 'Eastward current velocity (uo)'}, {id: '1.13', name: 'Northward current velocity (vo)'}] },
    { id: 'waves', name: 'Waves & Stokes', vars: [{id: '3.20', name: 'Stokes drift — eastward'}, {id: '3.21', name: 'Stokes drift — northward'}] },
    { id: 'atmosphere', name: 'Atmosphere', vars: [{id: '4.1', name: 'Wind speed at 10m — eastward'}] }
  ]

  if (!isOpen) {
    return (
      <div 
        className="absolute top-[80px] left-stack-md bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-sm z-20 hover:bg-surface-variant transition-colors"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-primary">layers</span>
        <span className="font-label-md text-label-md text-on-surface">Variables</span>
        {selectedVariables.length > 0 && (
          <span className="w-5 h-5 bg-primary text-on-primary rounded-full flex items-center justify-center text-[10px] font-bold">
            {selectedVariables.length}
          </span>
        )}
      </div>
    )
  }

  return (
    <div className="absolute top-[80px] left-stack-md w-[320px] max-h-[calc(100vh-200px)] flex flex-col bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl shadow-sm z-20 overflow-hidden">
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-surface">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">layers</span>
          <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface">Data Variables</h3>
        </div>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-stack-md flex flex-col gap-2">
        {mockGroups.map(group => (
          <div key={group.id} className="border border-outline-variant rounded-lg overflow-hidden">
            <button 
              onClick={() => toggleGroup(group.id)}
              className="w-full flex items-center justify-between p-3 bg-surface-container-low hover:bg-surface-variant transition-colors"
            >
              <span className="font-label-md text-label-md text-on-surface">{group.name}</span>
              {expandedGroups.includes(group.id) ? <ChevronDown size={18}/> : <ChevronRight size={18}/>}
            </button>
            
            {expandedGroups.includes(group.id) && (
              <div className="flex flex-col gap-1 p-2 bg-surface">
                {group.vars.map(v => {
                  const isSelected = selectedVariables.includes(v.id)
                  return (
                    <label key={v.id} onClick={() => toggleVariable(v.id)} className="flex items-center gap-3 p-2 hover:bg-surface-variant rounded-md cursor-pointer transition-colors group">
                      <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${isSelected ? 'bg-primary border-primary' : 'border-outline group-hover:border-primary'}`}>
                        {isSelected && <Check size={14} className="text-on-primary" />}
                      </div>
                      <span className="font-body-sm text-body-sm text-on-surface flex-1">{v.name}</span>
                    </label>
                  )
                })}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="border-t border-outline-variant p-stack-sm bg-surface-container-lowest">
        <div className="flex items-center justify-between">
          <span className="font-label-sm text-label-sm text-on-surface-variant">Selected: {selectedVariables.length}</span>
          <button className="text-primary font-label-sm text-label-sm hover:underline">Clear all</button>
        </div>
      </div>
    </div>
  )
}
