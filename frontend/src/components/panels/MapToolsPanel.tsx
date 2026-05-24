import { useSimulationStore } from '../../store/simulationStore'

export default function MapToolsPanel() {
  const activeMapTool = useSimulationStore(state => state.activeMapTool)
  const setActiveMapTool = useSimulationStore(state => state.setActiveMapTool)

  const toggleTool = (tool: 'bounds' | 'pin') => {
    setActiveMapTool(activeMapTool === tool ? null : tool)
  }

  return (
    <div className="liquid-glass rounded-xl p-2 flex flex-col gap-2 pointer-events-auto">
      <button 
        onClick={() => toggleTool('bounds')}
        className={`p-2 rounded-lg flex flex-col items-center gap-1 transition-colors ${
          activeMapTool === 'bounds' 
            ? 'bg-[#6B8E6D] text-white border-2 border-[#6B8E6D]' 
            : 'hover:bg-white/50 text-on-surface border-2 border-transparent'
        }`}
        title="Set Environment Bounds"
      >
        <span className="material-symbols-outlined text-[20px]">public</span>
        <span className="text-[10px] font-label-sm">Bounds</span>
      </button>
      
      <button 
        onClick={() => toggleTool('pin')}
        className={`p-2 rounded-lg flex flex-col items-center gap-1 transition-colors ${
          activeMapTool === 'pin' 
            ? 'bg-[#6B8E6D] text-white border-2 border-[#6B8E6D]' 
            : 'hover:bg-white/50 text-on-surface border-2 border-transparent'
        }`}
        title="Place Turbine"
      >
        <span className="material-symbols-outlined text-[20px]">push_pin</span>
        <span className="text-[10px] font-label-sm">Pin</span>
      </button>

      <div className="w-[1px] bg-outline-variant my-1" />

      <button 
        onClick={() => {
          useSimulationStore.getState().setRegionBounds(null);
          useSimulationStore.getState().setWindmillPosition(null);
          useSimulationStore.getState().setBoundsDrawingState({ points: [] });
          setActiveMapTool(null);
        }}
        className="p-2 rounded-lg flex flex-col items-center gap-1 transition-colors hover:bg-error/10 text-error border border-transparent"
        title="Clear Map Selections"
      >
        <span className="material-symbols-outlined text-[20px]">delete</span>
        <span className="text-[10px] font-label-sm">Clear</span>
      </button>
    </div>
  )
}
