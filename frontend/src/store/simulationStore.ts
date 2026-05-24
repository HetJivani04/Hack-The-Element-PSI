// import { create } from 'zustand'

// export interface RegionBounds {
//   southwest: { lat: number, lon: number }
//   northeast: { lat: number, lon: number }
// }

// export interface WindmillPosition {
//   lat: number
//   lon: number
// }

// interface SimulationState {
//   // Region Selection
//   regionBounds: RegionBounds | null
//   setRegionBounds: (bounds: RegionBounds | null) => void
  
//   // Windmill Placement
//   windmillPosition: WindmillPosition | null
//   setWindmillPosition: (pos: WindmillPosition | null) => void
//   windmillType: 'grounded' | 'floating'
//   setWindmillType: (type: 'grounded' | 'floating') => void
  
//   // Floating Panel A: Variables
//   selectedVariables: string[]
//   toggleVariable: (varId: string) => void
//   setVariables: (varIds: string[]) => void
  
//   // Floating Panel B: Analysis
//   selectedTools: string[]
//   toggleTool: (toolId: string) => void
//   toolParams: Record<string, Record<string, unknown>> // tool_id -> { paramName: value }
//   setToolParam: (toolId: string, paramName: string, value: unknown) => void
  
//   // Floating Panel C: Turbine Specs
//   turbineSpecs: {
//     hubHeight: number
//     rotorDiameter: number
//     ratedPower: number
//     columnDiameter?: number
//     floaterRadius?: number
//     materialGrade: string
//   }
//   setTurbineSpecs: (specs: Partial<SimulationState['turbineSpecs']>) => void
  
//   // Floating Panel D: Time Range
//   timeRange: { startYear: number, endYear: number }
//   setTimeRange: (range: { startYear: number, endYear: number }) => void
  
//   // Job Status
//   currentJobId: string | null
//   setCurrentJobId: (id: string | null) => void
// }

// // Defaults based on type
// const DEFAULT_GROUNDED = { hubHeight: 150, rotorDiameter: 236, ratedPower: 15, materialGrade: 's355' }
// const DEFAULT_FLOATING = { hubHeight: 150, rotorDiameter: 236, ratedPower: 15, materialGrade: 's355', columnDiameter: 12.5, floaterRadius: 45.0 }

// export const useSimulationStore = create<SimulationState>((set) => ({
//   regionBounds: null,
//   setRegionBounds: (bounds) => set({ regionBounds: bounds }),
  
//   windmillPosition: null,
//   setWindmillPosition: (pos) => set({ windmillPosition: pos }),
  
//   windmillType: 'grounded',
//   setWindmillType: (type) => set({ 
//     windmillType: type,
//     turbineSpecs: type === 'grounded' ? DEFAULT_GROUNDED : DEFAULT_FLOATING
//   }),
  
//   selectedVariables: [],
//   toggleVariable: (varId) => set((state) => ({
//     selectedVariables: state.selectedVariables.includes(varId)
//       ? state.selectedVariables.filter(id => id !== varId)
//       : [...state.selectedVariables, varId]
//   })),
//   setVariables: (varIds) => set({ selectedVariables: varIds }),
  
//   selectedTools: [],
//   toggleTool: (toolId) => set((state) => ({
//     selectedTools: state.selectedTools.includes(toolId)
//       ? state.selectedTools.filter(id => id !== toolId)
//       : [...state.selectedTools, toolId]
//   })),
  
//   toolParams: {},
//   setToolParam: (toolId, paramName, value) => set((state) => ({
//     toolParams: {
//       ...state.toolParams,
//       [toolId]: {
//         ...(state.toolParams[toolId] || {}),
//         [paramName]: value
//       }
//     }
//   })),
  
//   turbineSpecs: DEFAULT_GROUNDED,
//   setTurbineSpecs: (specs) => set((state) => ({
//     turbineSpecs: { ...state.turbineSpecs, ...specs }
//   })),
  
//   timeRange: { startYear: 2024, endYear: 2024 },
//   setTimeRange: (range) => set({ timeRange: range }),
  
//   currentJobId: null,
//   setCurrentJobId: (id) => set({ currentJobId: id }),
// }))

import { create } from 'zustand'

export interface RegionBounds {
  southwest: { lat: number, lon: number }
  northeast: { lat: number, lon: number }
}

export interface WindmillPosition {
  lat: number
  lon: number
}

export type WindmillType = 'grounded' | 'floating'

export type StabilityRegime = 'auto' | 'neutral' | 'stable' | 'unstable'

export interface GaussianWakeParams {
  kStarOverride: boolean
  kStar: number         // 0.01 – 0.10, default from TI
  epsilon: number       // initial wake width 0.05 – 0.50
  stabilityRegime: StabilityRegime
  dyerExponent: number  // -0.5 – 0.0
  wakeTurbulenceModel: 'frandsen' | 'none'
}

export interface AcousticParams {
  geometricSpread: 'spherical' | 'cylindrical' | 'shallow'
  includeConstruction: boolean
  pileStrokes: number
}

export interface ScourParams {
  sedimentGradeOverride: boolean
  d50mm: number
}

export interface LagrangianParams {
  integrator: 'euler' | 'rk2' | 'rk4'
  nParticles: number
  dtSeconds: number
  includeStokes: boolean
  includeTides: boolean
  includeWindage: boolean
}

export interface MaxEntParams {
  nOccurrences: number
  regularizationMultiplier: number
  featureTypes: string[]
}

export interface MethodParams {
  gaussian_wake: GaussianWakeParams
  acoustic: AcousticParams
  scour: ScourParams
  lagrangian: LagrangianParams
  maxent: MaxEntParams
}

interface SimulationState {
  // Region Selection
  regionBounds: RegionBounds | null
  setRegionBounds: (bounds: RegionBounds | null) => void

  // Windmill Placement
  windmillPosition: WindmillPosition | null
  setWindmillPosition: (pos: WindmillPosition | null) => void
  windmillType: WindmillType
  setWindmillType: (type: WindmillType) => void

  // Manual coordinate input
  manualLat: string
  manualLon: string
  setManualLat: (v: string) => void
  setManualLon: (v: string) => void
  applyManualCoords: () => void

  // Map Interactive Tools
  activeMapTool: 'bounds' | 'pin' | null
  setActiveMapTool: (tool: 'bounds' | 'pin' | null) => void
  boundsDrawingState: { corner1: { lat: number, lon: number } | null }
  setBoundsDrawingState: (state: { corner1: { lat: number, lon: number } | null }) => void

  // Floating Panel A: Variables
  selectedVariables: string[]
  toggleVariable: (varId: string) => void
  setVariables: (varIds: string[]) => void

  // Floating Panel B: Analysis methods + per-method params
  selectedTools: string[]
  toggleTool: (toolId: string) => void
  // Legacy generic params (kept for API compatibility)
  toolParams: Record<string, Record<string, unknown>>
  setToolParam: (toolId: string, paramName: string, value: unknown) => void
  // Typed method params
  methodParams: MethodParams
  setGaussianWakeParam: <K extends keyof GaussianWakeParams>(key: K, value: GaussianWakeParams[K]) => void
  setAcousticParam: <K extends keyof AcousticParams>(key: K, value: AcousticParams[K]) => void
  setScourParam: <K extends keyof ScourParams>(key: K, value: ScourParams[K]) => void
  setLagrangianParam: <K extends keyof LagrangianParams>(key: K, value: LagrangianParams[K]) => void
  setMaxEntParam: <K extends keyof MaxEntParams>(key: K, value: MaxEntParams[K]) => void

  // Floating Panel C: Turbine Specs
  turbineSpecs: {
    model: string
    hubHeight: number
    rotorDiameter: number
    ratedPower: number
    cutInWindSpeed: number
    ratedWindSpeed: number
    cutOutWindSpeed: number
    foundationType: string
    exportCable: string
    cpPowerCoefficient: string
    ctThrustCoefficient: string
    columnDiameter: number
    floaterRadius: number
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

const DEFAULT_GROUNDED_SPECS = {
  model: 'Siemens Gamesa SG 14-236 DD',
  hubHeight: 150,
  rotorDiameter: 236,
  ratedPower: 15,
  cutInWindSpeed: 3.5,
  ratedWindSpeed: 11.0,
  cutOutWindSpeed: 25.0,
  foundationType: 'Monopile (9 m diameter, 30 m burial)',
  exportCable: '66 kV AC, ~130 A',
  cpPowerCoefficient: 'Peaks at ~0.48 at rated speed',
  ctThrustCoefficient: '~0.85 in partial load, decreases above rated',
  columnDiameter: 0,
  floaterRadius: 0,
  materialGrade: 's355',
}

const DEFAULT_FLOATING_SPECS = {
  model: 'Siemens Gamesa SG 14-236 DD',
  hubHeight: 150,
  rotorDiameter: 236,
  ratedPower: 15,
  cutInWindSpeed: 3.5,
  ratedWindSpeed: 11.0,
  cutOutWindSpeed: 25.0,
  foundationType: 'Floating Platform',
  exportCable: '66 kV AC, ~130 A',
  cpPowerCoefficient: 'Peaks at ~0.48 at rated speed',
  ctThrustCoefficient: '~0.85 in partial load, decreases above rated',
  columnDiameter: 12.5,
  floaterRadius: 45.0,
  materialGrade: 's355',
}

const DEFAULT_METHOD_PARAMS: MethodParams = {
  gaussian_wake: {
    kStarOverride: false,
    kStar: 0.035,
    epsilon: 0.25,
    stabilityRegime: 'auto',
    dyerExponent: -0.25,
    wakeTurbulenceModel: 'frandsen',
  },
  acoustic: {
    geometricSpread: 'cylindrical',
    includeConstruction: false,
    pileStrokes: 1000,
  },
  scour: {
    sedimentGradeOverride: false,
    d50mm: 0.25,
  },
  lagrangian: {
    integrator: 'rk4',
    nParticles: 1000,
    dtSeconds: 3600,
    includeStokes: true,
    includeTides: true,
    includeWindage: true,
  },
  maxent: {
    nOccurrences: 50000,
    regularizationMultiplier: 1.0,
    featureTypes: ['linear', 'quadratic', 'hinge'],
  },
}

export const useSimulationStore = create<SimulationState>((set, get) => ({
  regionBounds: null,
  setRegionBounds: (bounds) => set({ regionBounds: bounds }),

  windmillPosition: null,
  setWindmillPosition: (pos) => set({ windmillPosition: pos }),

  windmillType: 'grounded',
  setWindmillType: (type) => set({
    windmillType: type,
    turbineSpecs: type === 'grounded' ? DEFAULT_GROUNDED_SPECS : DEFAULT_FLOATING_SPECS,
  }),

  manualLat: '44.100',
  manualLon: '-63.200',
  setManualLat: (v) => set({ manualLat: v }),
  setManualLon: (v) => set({ manualLon: v }),
  applyManualCoords: () => {
    const { manualLat, manualLon } = get()
    const lat = parseFloat(manualLat)
    const lon = parseFloat(manualLon)
    if (!isNaN(lat) && !isNaN(lon)) {
      set({ windmillPosition: { lat, lon } })
    }
  },

  activeMapTool: null,
  setActiveMapTool: (tool) => set({ activeMapTool: tool }),
  boundsDrawingState: { corner1: null },
  setBoundsDrawingState: (state) => set({ boundsDrawingState: state }),

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
      [toolId]: { ...(state.toolParams[toolId] || {}), [paramName]: value }
    }
  })),

  methodParams: DEFAULT_METHOD_PARAMS,
  setGaussianWakeParam: (key, value) => set((s) => ({
    methodParams: { ...s.methodParams, gaussian_wake: { ...s.methodParams.gaussian_wake, [key]: value } }
  })),
  setAcousticParam: (key, value) => set((s) => ({
    methodParams: { ...s.methodParams, acoustic: { ...s.methodParams.acoustic, [key]: value } }
  })),
  setScourParam: (key, value) => set((s) => ({
    methodParams: { ...s.methodParams, scour: { ...s.methodParams.scour, [key]: value } }
  })),
  setLagrangianParam: (key, value) => set((s) => ({
    methodParams: { ...s.methodParams, lagrangian: { ...s.methodParams.lagrangian, [key]: value } }
  })),
  setMaxEntParam: (key, value) => set((s) => ({
    methodParams: { ...s.methodParams, maxent: { ...s.methodParams.maxent, [key]: value } }
  })),

  turbineSpecs: DEFAULT_GROUNDED_SPECS,
  setTurbineSpecs: (specs) => set((state) => ({
    turbineSpecs: { ...state.turbineSpecs, ...specs }
  })),

  timeRange: { startYear: 2024, endYear: 2024 },
  setTimeRange: (range) => set({ timeRange: range }),

  currentJobId: null,
  setCurrentJobId: (id) => set({ currentJobId: id }),
}))