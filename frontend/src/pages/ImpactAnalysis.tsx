import React from 'react'
import { useSimulationStore } from '../store/simulationStore'
import { useJobResult, useJobHistory } from '../api/client'
import { Link } from 'react-router-dom'

export default function ImpactAnalysis() {
  const { selectedJobId } = useSimulationStore()
  const { data: jobHistory } = useJobHistory()
  const { data: resultData, isLoading, isError } = useJobResult(selectedJobId)

  const jobInfo = jobHistory && Array.isArray(jobHistory) && selectedJobId 
    ? jobHistory.find((j: any) => j.job_id === selectedJobId) 
    : null

  if (!selectedJobId) {
    return (
      <div className="flex-1 p-margin-mobile md:p-margin-desktop bg-surface flex flex-col items-center justify-center min-h-[60vh]">
        <span className="material-symbols-outlined text-6xl text-on-surface-variant mb-4 opacity-50">analytics</span>
        <h2 className="text-2xl font-bold text-on-surface mb-2">No Job Selected</h2>
        <p className="text-on-surface-variant mb-6 text-center max-w-md">
          Please select a completed job from the Job Management Dashboard to view its analytics and impact reports.
        </p>
        <Link to="/jobs" className="px-6 py-3 bg-primary text-on-primary rounded-md shadow-sm hover:bg-opacity-90 transition-colors">
          Go to Job Management
        </Link>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex-1 p-margin-mobile md:p-margin-desktop bg-surface flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <span className="material-symbols-outlined text-4xl text-primary animate-spin">refresh</span>
          <p className="text-on-surface-variant">Loading results for {jobInfo?.description || selectedJobId}...</p>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex-1 p-margin-mobile md:p-margin-desktop bg-surface flex flex-col items-center justify-center min-h-[60vh]">
        <span className="material-symbols-outlined text-6xl text-error mb-4">error</span>
        <h2 className="text-2xl font-bold text-on-surface mb-2">Failed to load results</h2>
        <p className="text-on-surface-variant mb-6">Could not fetch data for job {selectedJobId}</p>
        <Link to="/jobs" className="px-4 py-2 border border-outline-variant rounded-md hover:bg-surface-container transition-colors">
          Back to Jobs
        </Link>
      </div>
    )
  }

  return (
    <div className="flex-1 p-margin-mobile md:p-margin-desktop bg-surface">
      <div className="mb-section-gap flex justify-between items-end">
        <div>
          <h1 className="font-display-lg-mobile md:font-display-lg text-primary mb-2">Simulation Report</h1>
          <p className="font-body-lg text-on-surface-variant">
            {jobInfo?.description || 'Analytics for selected job'} 
            <span className="ml-2 text-sm px-2 py-0.5 bg-surface-container rounded-full">{selectedJobId}</span>
          </p>
        </div>
        <Link to="/jobs" className="px-4 py-2 border border-outline-variant rounded-md text-sm hover:bg-surface-container transition-colors flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          All Jobs
        </Link>
      </div>

      <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 mb-8">
        <h3 className="font-headline-md text-on-surface mb-4">Raw Output Data</h3>
        <div className="bg-[#1e1e1e] rounded-lg p-4 overflow-auto max-h-[500px]">
          <pre className="text-sm text-green-400 font-mono">
            {JSON.stringify(resultData, null, 2)}
          </pre>
        </div>
      </div>

      {/* Bento Grid Layout (Placeholder for actual charts based on data) */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter mb-section-gap">
        
        {/* Ecological Health Score (Span 4) */}
        <div className="md:col-span-4 bg-surface-container-lowest border border-outline-variant rounded-xl p-stack-lg relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <span className="material-symbols-outlined text-6xl">eco</span>
          </div>
          <h3 className="font-headline-md text-primary mb-1">Ecological Health</h3>
          <p className="font-label-sm text-on-surface-variant mb-6 uppercase tracking-wider">Overall System Vitality</p>
          <div className="flex items-baseline gap-2 mb-4">
            <span className="font-display-lg text-on-surface">84.2</span>
            <span className="font-body-md text-on-surface-variant">/ 100</span>
          </div>
          <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
            <div className="h-full bg-primary w-[84.2%] rounded-full"></div>
          </div>
          <p className="font-label-sm text-primary mt-2 flex items-center gap-1">
            <span className="material-symbols-outlined text-[16px]">trending_up</span> +2.4% from baseline
          </p>
        </div>

        {/* Ecosystem Impact Matrix (Span 8) */}
        <div className="md:col-span-8 bg-surface-container-lowest border border-outline-variant rounded-xl p-stack-lg flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="font-headline-md text-primary mb-1">Impact Matrix</h3>
              <p className="font-label-sm text-on-surface-variant uppercase tracking-wider">Heat levels across primary domains</p>
            </div>
          </div>
          <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Flora */}
            <div className="flex flex-col gap-2">
              <div className="font-label-md text-on-surface flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined text-sm text-secondary">grass</span> Flora
              </div>
              <div className="bg-surface-container h-12 rounded flex items-center px-3 border border-outline-variant border-opacity-30">
                <span className="font-label-sm text-on-surface-variant">Kelp Forests</span>
                <div className="ml-auto w-3 h-3 rounded-full bg-secondary-container"></div>
              </div>
            </div>
            
            {/* Fauna */}
            <div className="flex flex-col gap-2">
              <div className="font-label-md text-on-surface flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined text-sm text-primary">pets</span> Fauna
              </div>
              <div className="bg-surface-container h-12 rounded flex items-center px-3 border border-outline-variant border-opacity-30">
                <span className="font-label-sm text-on-surface-variant">Marine Mammals</span>
                <div className="ml-auto w-3 h-3 rounded-full bg-tertiary-container"></div>
              </div>
            </div>
            
            {/* Water */}
            <div className="flex flex-col gap-2">
              <div className="font-label-md text-on-surface flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined text-sm text-secondary-fixed-dim">water_drop</span> Water Quality
              </div>
              <div className="bg-surface-container h-12 rounded flex items-center px-3 border border-outline-variant border-opacity-30">
                <span className="font-label-sm text-on-surface-variant">Turbidity</span>
                <div className="ml-auto w-3 h-3 rounded-full bg-surface-variant"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
