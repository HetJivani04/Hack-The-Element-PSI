import { useQuery, useMutation } from '@tanstack/react-query'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export const fetchRegion = async () => {
  const res = await fetch(`${API_BASE_URL}/api/region`)
  if (!res.ok) throw new Error('Failed to fetch region')
  return res.json()
}

export const useRegion = () => {
  return useQuery({
    queryKey: ['region'],
    queryFn: fetchRegion,
  })
}

export const fetchSiteValidation = async (lat: number, lon: number) => {
  const res = await fetch(`${API_BASE_URL}/api/site/validate?lat=${lat}&lon=${lon}`)
  if (!res.ok) throw new Error('Failed to validate site')
  return res.json()
}

export const useSiteValidation = (lat: number | null, lon: number | null) => {
  return useQuery({
    queryKey: ['siteValidation', lat, lon],
    queryFn: () => fetchSiteValidation(lat!, lon!),
    enabled: lat !== null && lon !== null,
  })
}

export const fetchTools = async () => {
  const res = await fetch(`${API_BASE_URL}/api/tools`)
  if (!res.ok) throw new Error('Failed to fetch tools')
  return res.json()
}

export const useTools = () => {
  return useQuery({
    queryKey: ['tools'],
    queryFn: fetchTools,
  })
}

export const fetchToolDetails = async (toolId: string) => {
  const res = await fetch(`${API_BASE_URL}/api/tools/${toolId}`)
  if (!res.ok) throw new Error('Failed to fetch tool details')
  return res.json()
}

export const useToolDetails = (toolId: string | null) => {
  return useQuery({
    queryKey: ['tool', toolId],
    queryFn: () => fetchToolDetails(toolId!),
    enabled: !!toolId,
  })
}

export const submitJob = async (jobPayload: Record<string, unknown>) => {
  const res = await fetch(`${API_BASE_URL}/api/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jobPayload),
  })
  if (!res.ok) throw new Error('Failed to submit job')
  return res.json()
}

export const useSubmitJob = () => {
  return useMutation({
    mutationFn: submitJob,
  })
}

export const fetchJobStatus = async (jobId: string) => {
  const res = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`)
  if (!res.ok) throw new Error('Failed to fetch job status')
  return res.json()
}

export const useJobStatus = (jobId: string | null, pollIntervalMs: number = 2000) => {
  return useQuery({
    queryKey: ['job', jobId],
    queryFn: () => fetchJobStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      // Stop polling if completed or error
      if (query.state.data?.status === 'completed' || query.state.data?.status === 'failed') {
        return false
      }
      return pollIntervalMs
    },
  })
}

export const fetchJobHistory = async () => {
  const res = await fetch(`${API_BASE_URL}/api/jobs/history`)
  if (!res.ok) throw new Error('Failed to fetch job history')
  return res.json()
}

export const useJobHistory = () => {
  return useQuery({
    queryKey: ['jobHistory'],
    queryFn: fetchJobHistory,
    refetchInterval: (query) => {
      // Auto-poll if any jobs are running or queued
      const hasActive = Array.isArray(query.state.data) && query.state.data.some(
        (j: any) => j.status === 'running' || j.status === 'queued'
      )
      return hasActive ? 3000 : false
    }
  })
}

export const fetchJobResult = async (jobId: string) => {
  const res = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/result`)
  if (!res.ok) throw new Error('Failed to fetch job result')
  return res.json()
}

export const useJobResult = (jobId: string | null) => {
  return useQuery({
    queryKey: ['jobResult', jobId],
    queryFn: () => fetchJobResult(jobId!),
    enabled: !!jobId,
  })
}
