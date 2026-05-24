import { useState } from 'react'
import { useTools, useToolDetails } from '../../api/client'
import { useSimulationStore } from '../../store/simulationStore'

export default function AnalysisMethodsPanel() {
  const [isOpen, setIsOpen] = useState(true)
  
  const { data: toolsList, isLoading: toolsLoading } = useTools()
  const selectedTools = useSimulationStore(state => state.selectedTools)
  const toggleTool = useSimulationStore(state => state.toggleTool)
  
  // We only support one active tool form right now for simplicity
  const activeToolId = selectedTools[0]
  const { data: toolDetails } = useToolDetails(activeToolId)
  
  const toolParams = useSimulationStore(state => state.toolParams)
  const setToolParam = useSimulationStore(state => state.setToolParam)

  if (!isOpen) {
    return (
      <div 
        className="absolute top-[80px] right-stack-md bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-sm z-20 hover:bg-surface-variant transition-colors"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-tertiary">science</span>
        <span className="font-label-md text-label-md text-on-surface">Analysis Methods</span>
      </div>
    )
  }

  return (
    <div className="absolute top-[80px] right-stack-md w-[360px] max-h-[calc(100vh-200px)] flex flex-col bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl shadow-sm z-20 overflow-hidden">
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-surface">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-tertiary">science</span>
          <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface">Analysis Modules</h3>
        </div>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-stack-md flex flex-col gap-4">
        {toolsLoading ? (
           <div className="flex justify-center"><div className="w-6 h-6 border-2 border-tertiary border-t-transparent rounded-full animate-spin"></div></div>
        ) : (
          <div className="flex flex-col gap-2">
            <h4 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Available Tools</h4>
            {toolsList?.map((tool: Record<string, unknown>) => (
              <div 
                key={tool.tool_id as string}
                onClick={() => toggleTool(tool.tool_id as string)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedTools.includes(tool.tool_id as string) 
                    ? 'bg-tertiary-container border-tertiary text-on-tertiary-container' 
                    : 'bg-surface-container-low border-outline-variant hover:border-tertiary'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="font-label-md text-label-md font-semibold">{tool.name as string}</span>
                  {selectedTools.includes(tool.tool_id as string) && <span className="material-symbols-outlined text-tertiary text-[18px]">check_circle</span>}
                </div>
                <p className="font-body-sm text-body-sm opacity-80 line-clamp-2">{tool.description as string}</p>
              </div>
            ))}
          </div>
        )}

        {selectedTools.length > 0 && toolDetails && (
          <div className="flex flex-col gap-3 pt-4 border-t border-outline-variant">
            <h4 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Configuration</h4>
            
            {toolDetails.user_parameters?.map((param: Record<string, unknown>) => (
              <div key={param.name as string} className="flex flex-col gap-1">
                <div className="flex justify-between items-end">
                  <label className="font-label-sm text-label-sm text-on-surface">{param.label as string}</label>
                  {param.type !== 'select' && <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">
                    {toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
                  </span>}
                </div>
                
                {param.type === 'integer' || param.type === 'float' ? (
                  <input 
                    type="range" 
                    min={param.min as number} 
                    max={param.max as number}
                    value={toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
                    onChange={(e) => setToolParam(activeToolId, param.name as string, Number(e.target.value))}
                    className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-tertiary" 
                  />
                ) : param.type === 'select' ? (
                  <select 
                    value={toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
                    onChange={(e) => setToolParam(activeToolId, param.name as string, e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded p-2 text-body-sm text-on-surface focus:border-tertiary outline-none"
                  >
                    {(param.options as Record<string, unknown>[]).map((opt) => (
                      <option key={opt.value as string} value={opt.value as string}>{opt.label as string}</option>
                    ))}
                  </select>
                ) : (
                  <input 
                    type="text" 
                    value={toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
                    onChange={(e) => setToolParam(activeToolId, param.name as string, e.target.value)}
                    className="w-full bg-surface-container-low border border-outline-variant rounded p-2 text-body-sm text-on-surface focus:border-tertiary outline-none"
                  />
                )}
              </div>
            ))}
            
            <div className="mt-2 p-3 bg-surface-variant rounded-lg flex items-center justify-between">
              <span className="font-label-sm text-label-sm text-on-surface">Est. Runtime</span>
              <span className="font-mono text-body-sm font-semibold text-on-surface">
                ~30s
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
