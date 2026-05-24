import { useSubmitJob } from '../../api/client'
import { useSimulationStore } from '../../store/simulationStore'

export default function TimeRangePanel() {
  const timeRange = useSimulationStore(state => state.timeRange)
  const setTimeRange = useSimulationStore(state => state.setTimeRange)
  
  const submitJob = useSubmitJob()
  const setCurrentJobId = useSimulationStore(state => state.setCurrentJobId)
  
  const windmillPos = useSimulationStore(state => state.windmillPosition)
  const selectedVars = useSimulationStore(state => state.selectedVariables)
  const selectedTools = useSimulationStore(state => state.selectedTools)
  
  const canSubmit = windmillPos !== null && selectedVars.length > 0 && selectedTools.length > 0
  
  const handleSubmit = () => {
    if (!canSubmit) return
    submitJob.mutate({
      tool_id: selectedTools[0],
      site: windmillPos,
      variables: selectedVars.reduce((acc, v) => ({...acc, [v]: true}), {}),
      params: { timeRange }
    }, {
      onSuccess: (data) => {
        setCurrentJobId(data.job_id)
      }
    })
  }

  return (
    <div className="absolute bottom-stack-lg right-margin-desktop left-margin-desktop max-w-[900px] mx-auto liquid-glass rounded-xl p-stack-sm flex items-center justify-between z-20">
      <div className="flex justify-between items-center w-full">
        <div className="flex gap-stack-md items-center">
          <button className="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface hover:text-primary hover:bg-surface-variant transition-colors">
            <span className="material-symbols-outlined">play_arrow</span>
          </button>
          <div className="flex flex-col w-96 gap-2">
            <div className="flex gap-4 items-center">
              <span className="text-xs font-bold text-[#2F4F4F] w-10">Start:</span>
              <input 
                type="range" 
                min={1993} 
                max={timeRange.endYear} 
                value={timeRange.startYear}
                onChange={(e) => setTimeRange({ startYear: Number(e.target.value), endYear: timeRange.endYear })}
                className="w-full h-1 bg-surface-variant rounded-full appearance-none cursor-pointer accent-[#2F4F4F]"
              />
              <span className="text-xs text-[#2F4F4F] font-bold font-mono w-10">{timeRange.startYear}</span>
            </div>
            <div className="flex gap-4 items-center">
              <span className="text-xs font-bold text-[#2F4F4F] w-10">End:</span>
              <input 
                type="range" 
                min={timeRange.startYear} 
                max={2026} 
                value={timeRange.endYear}
                onChange={(e) => setTimeRange({ startYear: timeRange.startYear, endYear: Number(e.target.value) })}
                className="w-full h-1 bg-surface-variant rounded-full appearance-none cursor-pointer accent-[#2F4F4F]"
              />
              <span className="text-xs text-[#2F4F4F] font-bold font-mono w-10">{timeRange.endYear}</span>
            </div>
          </div>
        </div>
        
        <div className="flex gap-stack-sm items-center">
          <span className="px-3 py-1 bg-secondary-container text-on-secondary-container rounded-full font-label-sm text-[11px] flex items-center gap-1 border border-secondary/20">
            <span className="w-2 h-2 rounded-full bg-secondary"></span> Live Telemetry
          </span>
          <button 
            onClick={handleSubmit}
            disabled={!canSubmit || submitJob.isPending}
            className={`ml-2 px-6 py-2 rounded-full font-label-sm text-[12px] font-bold transition-all ${
              canSubmit && !submitJob.isPending
                ? 'bg-primary text-on-primary hover:bg-primary/90 shadow-md' 
                : 'bg-surface-variant text-on-surface-variant opacity-50 cursor-not-allowed'
            }`}
          >
            {submitJob.isPending ? 'Submitting...' : 'Run Simulation'}
          </button>
        </div>
      </div>
    </div>
  )
}
