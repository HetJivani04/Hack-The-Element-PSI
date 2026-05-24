
import { useRegion, useSubmitJob } from '../../api/client'
import { useSimulationStore } from '../../store/simulationStore'

export default function TimeRangePanel() {
  const { data: regionData } = useRegion()
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

  // Extract years from region temporal coverage (fallback to 1993-2026)
  const startYearBound = regionData ? new Date(regionData.temporal_coverage.earliest).getFullYear() : 1993
  const endYearBound = regionData ? new Date(regionData.temporal_coverage.latest).getFullYear() : 2026

  return (
    <div className="absolute bottom-stack-lg left-1/2 -translate-x-1/2 w-[600px] bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center justify-between shadow-sm z-20">
      
      <div className="flex-1 px-4 flex flex-col gap-1">
        <div className="flex justify-between text-label-sm font-label-sm text-on-surface-variant">
          <span>{startYearBound}</span>
          <span className="text-primary font-semibold">{timeRange.startYear} - {timeRange.endYear}</span>
          <span>{endYearBound}</span>
        </div>
        
        {/* Simple single slider for now, ideally this would be a dual-thumb range slider */}
        <input 
          type="range" 
          min={startYearBound} 
          max={endYearBound} 
          value={timeRange.startYear}
          onChange={(e) => setTimeRange({ startYear: Number(e.target.value), endYear: timeRange.endYear })}
          className="w-full h-2 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary"
        />
        
        <div className="flex justify-between text-[10px] text-on-surface-variant uppercase mt-1">
          <span>Reanalysis</span>
          <span className="w-1 h-3 bg-outline-variant relative -top-3"></span>
          <span>Near Real-Time</span>
        </div>
      </div>
      
      <div className="border-l border-outline-variant pl-4 py-1">
        <button 
          onClick={handleSubmit}
          disabled={!canSubmit || submitJob.isPending}
          className={`px-6 py-2 rounded-full font-label-lg font-bold transition-all ${
            canSubmit && !submitJob.isPending
              ? 'bg-primary text-on-primary hover:bg-primary/90 shadow-md' 
              : 'bg-surface-variant text-on-surface-variant opacity-50 cursor-not-allowed'
          }`}
        >
          {submitJob.isPending ? 'Submitting...' : 'Run Simulation'}
        </button>
      </div>
      
    </div>
  )
}
