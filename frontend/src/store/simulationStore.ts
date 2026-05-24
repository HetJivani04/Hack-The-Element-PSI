import { create } from 'zustand'

export interface RegionBounds {
  southwest: { lat: number, lon: number }
  northeast: { lat: number, lon: number }
}

export interface WindmillPosition {
  lat: number
  lon: number
}

interface SimulationState {
  // Region Selection
  regionBounds: RegionBounds | null
  setRegionBounds: (bounds: RegionBounds | null) => void
  
  // Windmill Placement
  windmillPosition: WindmillPosition | null
  setWindmillPosition: (pos: WindmillPosition | null) => void
  windmillType: 'grounded' | 'floating'
  setWindmillType: (type: 'grounded' | 'floating') => void
  
  // Floating Panel A: Variables
  selectedVariables: string[]
  toggleVariable: (varId: string) => void
  setVariables: (varIds: string[]) => void
  
  // Floating Panel B: Analysis
  selectedTools: string[]
  toggleTool: (toolId: string) => void
  toolParams: Record<string, Record<string, unknown>> // tool_id -> { paramName: value }
  setToolParam: (toolId: string, paramName: string, value: unknown) => void
  
  // Floating Panel C: Turbine Specs
  turbineSpecs: {
    hubHeight: number
    rotorDiameter: number
    ratedPower: number
    columnDiameter?: number
    floaterRadius?: number
    materialGrade: string
  }
  setTurbineSpecs: (specs: Partial<SimulationState['turbineSpecs']>) => void
  
  // Floating Panel D: Time Range
  timeRange: { startYear: number, endYear: number }
  setTimeRange: (range: { startYear: number, endYear: number }) => void
  
  // Job Status
  currentJobId: string | null
  setCurrentJobId: (id: string | null) => void
}

// Defaults based on type
const DEFAULT_GROUNDED = { hubHeight: 150, rotorDiameter: 236, ratedPower: 15, materialGrade: 's355' }
const DEFAULT_FLOATING = { hubHeight: 150, rotorDiameter: 236, ratedPower: 15, materialGrade: 's355', columnDiameter: 12.5, floaterRadius: 45.0 }

export const useSimulationStore = create<SimulationState>((set) => ({
  regionBounds: {
    southwest: { lat: 43.68, lon: -64.33 },
    northeast: { lat: 44.83, lon: -61.94 }
  },
  setRegionBounds: (bounds) => set({ regionBounds: bounds }),
  
  windmillPosition: null,
  setWindmillPosition: (pos) => set({ windmillPosition: pos }),
  
  windmillType: 'grounded',
  setWindmillType: (type) => set({ 
    windmillType: type,
    turbineSpecs: type === 'grounded' ? DEFAULT_GROUNDED : DEFAULT_FLOATING
  }),
  
  selectedVariables: [],
  toggleVariable: (varId) => set((state) => ({
    selectedVariables: state.selectedVariables.includes(varId)
      ? state.selectedVariables.filter(id => id !== varId)
      : [...state.selectedVariables, varId]
  })),
  setVariables: (varIds) => set({ selectedVariables: varIds }),
  
  selectedTools: [],
  toggleTool: (toolId) => set((state) => ({
    selectedTools: state.selectedTools.includes(toolId)
      ? state.selectedTools.filter(id => id !== toolId)
      : [...state.selectedTools, toolId]
  })),
  
  toolParams: {},
  setToolParam: (toolId, paramName, value) => set((state) => ({
    toolParams: {
      ...state.toolParams,
      [toolId]: {
        ...(state.toolParams[toolId] || {}),
        [paramName]: value
      }
    }
  })),
  
  turbineSpecs: DEFAULT_GROUNDED,
  setTurbineSpecs: (specs) => set((state) => ({
    turbineSpecs: { ...state.turbineSpecs, ...specs }
  })),
  
  timeRange: { startYear: 2024, endYear: 2024 },
  setTimeRange: (range) => set({ timeRange: range }),
  
  currentJobId: null,
  setCurrentJobId: (id) => set({ currentJobId: id }),
}))
