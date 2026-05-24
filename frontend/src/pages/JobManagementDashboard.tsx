import React, { useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useJobHistory } from '../api/client'
import { useSimulationStore } from '../store/simulationStore'

interface JobData {
  job_id: string
  description: string
  method: string
  tool_id: string
  status: 'running' | 'completed' | 'queued' | 'failed'
  start_time: string
  queued_at: string
  runtime_minutes?: number
}

export default function JobManagementDashboard() {
  const { data: jobHistory, isLoading, isError } = useJobHistory()
  const { setSelectedJobId } = useSimulationStore()
  const navigate = useNavigate()

  const jobs: JobData[] = useMemo(() => {
    if (!jobHistory || !Array.isArray(jobHistory)) return []
    // jobHistory is a list of JobData
    return [...jobHistory].sort((a: JobData, b: JobData) => {
      return new Date(b.queued_at).getTime() - new Date(a.queued_at).getTime()
    })
  }, [jobHistory])

  const stats = useMemo(() => {
    return {
      running: jobs.filter(j => j.status === 'running').length,
      queued: jobs.filter(j => j.status === 'queued').length,
      completed: jobs.filter(j => j.status === 'completed').length,
    }
  }, [jobs])

  const handleViewResult = (jobId: string) => {
    setSelectedJobId(jobId)
    navigate('/results')
  }

  return (
    <div className="w-full min-h-full bg-background flex flex-col items-center">
      <div className="w-full max-w-[1400px] flex-1 flex flex-col p-8 gap-10">
        
        {/* Header Section */}
        <div className="flex flex-col gap-2">
          <h1 className="text-4xl font-bold text-on-surface">Job Management</h1>
          <p className="text-on-surface-variant text-lg">Monitor, configure, and analyze active simulation clusters.</p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-surface rounded-xl p-6 border border-outline-variant shadow-sm flex flex-col gap-4">
            <div className="flex items-center gap-2 text-on-surface-variant">
              <span className="material-symbols-outlined text-[20px]">sync</span>
              <span className="font-label-md font-bold tracking-wider">IN PROGRESS</span>
            </div>
            <div className="text-6xl font-bold text-on-surface">{stats.running}</div>
            <div className="text-body-sm text-on-surface-variant">Active computational clusters</div>
          </div>
          
          <div className="bg-surface rounded-xl p-6 border border-outline-variant shadow-sm flex flex-col gap-4">
            <div className="flex items-center gap-2 text-on-surface-variant">
              <span className="material-symbols-outlined text-[20px]">hourglass_empty</span>
              <span className="font-label-md font-bold tracking-wider">QUEUED</span>
            </div>
            <div className="text-6xl font-bold text-on-surface">{stats.queued}</div>
            <div className="text-body-sm text-on-surface-variant">Awaiting resource allocation</div>
          </div>

          <div className="bg-surface rounded-xl p-6 border border-outline-variant shadow-sm flex flex-col gap-4">
            <div className="flex items-center gap-2 text-on-surface-variant">
              <span className="material-symbols-outlined text-[20px] text-green-600">check_circle</span>
              <span className="font-label-md font-bold tracking-wider">COMPLETED</span>
            </div>
            <div className="text-6xl font-bold text-on-surface">{stats.completed}</div>
            <div className="text-body-sm text-on-surface-variant">Total completed</div>
          </div>
        </div>

        {/* Toolbar Section */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 mt-4">
          <div className="relative w-full md:w-[400px]">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
            <input 
              type="text" 
              placeholder="Search by Job ID or Method..." 
              className="w-full pl-10 pr-4 py-2 bg-surface border border-outline-variant rounded-md text-on-surface focus:outline-none focus:border-primary transition-colors shadow-sm"
            />
          </div>
          <div className="flex items-center gap-3 w-full md:w-auto">
            <button className="flex items-center gap-2 px-4 py-2 bg-surface border border-outline-variant rounded-md text-on-surface hover:bg-surface-container-high transition-colors shadow-sm">
              <span className="material-symbols-outlined text-[18px]">filter_list</span>
              Filter
            </button>
            <Link to="/" className="flex items-center gap-2 px-4 py-2 bg-[#426446] text-white rounded-md hover:bg-[#344d36] transition-colors shadow-sm whitespace-nowrap">
              <span className="material-symbols-outlined text-[18px]">add</span>
              New Job
            </Link>
          </div>
        </div>

        {/* Table Section */}
        <div className="bg-white rounded-xl border border-outline-variant shadow-sm overflow-hidden mt-2">
          {isLoading ? (
             <div className="p-8 text-center text-on-surface-variant">Loading jobs...</div>
          ) : isError ? (
             <div className="p-8 text-center text-red-600">Failed to load job history.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-[#fcfcfc] border-b border-outline-variant text-on-surface-variant font-label-md">
                    <th className="px-6 py-4 font-semibold whitespace-nowrap">Job ID</th>
                    <th className="px-6 py-4 font-semibold whitespace-nowrap">Description</th>
                    <th className="px-6 py-4 font-semibold whitespace-nowrap">Tool / Method</th>
                    <th className="px-6 py-4 font-semibold whitespace-nowrap">Status</th>
                    <th className="px-6 py-4 font-semibold whitespace-nowrap">Queued At</th>
                    <th className="px-6 py-4 font-semibold whitespace-nowrap">Runtime</th>
                    <th className="px-6 py-4 font-semibold text-center whitespace-nowrap">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-8 text-center text-on-surface-variant">No jobs found. Start a new simulation to see it here.</td>
                    </tr>
                  )}
                  {jobs.map((job) => (
                    <tr key={job.job_id} className="border-b border-outline-variant hover:bg-[#fafafa] transition-colors">
                      <td className="px-6 py-4 font-bold text-on-surface whitespace-nowrap">{job.job_id.split('_')[1] || job.job_id}</td>
                      <td className="px-6 py-4 text-on-surface whitespace-nowrap">{job.description || 'Simulation Run'}</td>
                      <td className="px-6 py-4 text-on-surface-variant whitespace-nowrap capitalize">{(job.tool_id || job.method || 'Engine').replace(/_/g, ' ')}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {job.status === 'running' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-bold">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse"></span>
                            Running
                          </span>
                        )}
                        {job.status === 'completed' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-100 text-green-800 text-xs font-bold">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-600"></span>
                            Completed
                          </span>
                        )}
                        {job.status === 'queued' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gray-200 text-gray-800 text-xs font-bold">
                            <span className="w-1.5 h-1.5 rounded-full bg-gray-600"></span>
                            Queued
                          </span>
                        )}
                        {job.status === 'failed' && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-100 text-red-800 text-xs font-bold">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-600"></span>
                            Failed
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-on-surface-variant whitespace-nowrap">
                        {new Date(job.queued_at).toLocaleString(undefined, {
                          month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                        })}
                      </td>
                      <td className="px-6 py-4 text-on-surface-variant whitespace-nowrap">
                        {job.runtime_minutes !== undefined ? `${job.runtime_minutes} mins` : '-'}
                      </td>
                      <td className="px-6 py-4 text-center whitespace-nowrap">
                        {job.status === 'completed' && (
                          <button 
                            onClick={() => handleViewResult(job.job_id)}
                            className="px-3 py-1.5 bg-primary-container text-on-primary-container rounded-md hover:bg-opacity-80 transition-colors text-sm font-medium"
                          >
                            View Result
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          
          {/* Pagination */}
          <div className="px-6 py-4 flex items-center justify-between border-t border-outline-variant bg-[#fcfcfc] text-sm text-on-surface-variant">
            <span>Showing {jobs.length} jobs</span>
            <div className="flex gap-2">
              <button className="p-1 rounded hover:bg-surface-container-high text-on-surface-variant transition-colors disabled:opacity-50" disabled>
                <span className="material-symbols-outlined text-[20px]">chevron_left</span>
              </button>
              <button className="p-1 rounded hover:bg-surface-container-high text-on-surface-variant transition-colors disabled:opacity-50" disabled>
                <span className="material-symbols-outlined text-[20px]">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
        
        <div className="flex-1"></div>

        {/* Footer */}
        <footer className="mt-8 pt-8 border-t border-outline-variant flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-on-surface-variant">
          <div>© 2024 PSI Water Windmills. Professional Simulation Interface.</div>
          <div className="flex gap-6 font-medium">
            <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-primary transition-colors">Support</a>
            <a href="#" className="hover:text-primary transition-colors">Documentation</a>
          </div>
        </footer>

      </div>
    </div>
  )
}
