import { useSimulationStore } from '../../store/simulationStore'

export default function MapToolsPanel() {
  const activeMapTool = useSimulationStore(state => state.activeMapTool)
  const setActiveMapTool = useSimulationStore(state => state.setActiveMapTool)

  const toggleTool = (tool: 'bounds' | 'pin') => {
    setActiveMapTool(activeMapTool === tool ? null : tool)
  }

  return (
    <div className="relative bg-white border border-outline-variant rounded-xl p-2 shadow-md flex gap-2 w-max">
      <button 
        onClick={() => toggleTool('bounds')}
        className={`p-2 rounded-lg flex flex-col items-center gap-1 transition-colors ${
          activeMapTool === 'bounds' 
            ? 'bg-primary/10 text-primary border border-primary/30' 
            : 'hover:bg-[#f5f5f5] text-on-surface border border-transparent'
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
            ? 'bg-primary/10 text-primary border border-primary/30' 
            : 'hover:bg-[#f5f5f5] text-on-surface border border-transparent'
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
