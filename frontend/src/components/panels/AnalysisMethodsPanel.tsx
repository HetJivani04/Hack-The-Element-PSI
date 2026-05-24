// import { useState } from 'react'
// import { useTools, useToolDetails } from '../../api/client'
// import { useSimulationStore } from '../../store/simulationStore'

// export default function AnalysisMethodsPanel() {
//   const [isOpen, setIsOpen] = useState(true)
  
//   const { data: toolsList, isLoading: toolsLoading } = useTools()
//   const selectedTools = useSimulationStore(state => state.selectedTools)
//   const toggleTool = useSimulationStore(state => state.toggleTool)
  
//   // We only support one active tool form right now for simplicity
//   const activeToolId = selectedTools[0]
//   const { data: toolDetails } = useToolDetails(activeToolId)
  
//   const toolParams = useSimulationStore(state => state.toolParams)
//   const setToolParam = useSimulationStore(state => state.setToolParam)

//   if (!isOpen) {
//     return (
//       <div 
//         className="absolute top-[80px] right-stack-md bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-sm z-20 hover:bg-surface-variant transition-colors"
//         onClick={() => setIsOpen(true)}
//       >
//         <span className="material-symbols-outlined text-tertiary">science</span>
//         <span className="font-label-md text-label-md text-on-surface">Analysis Methods</span>
//       </div>
//     )
//   }

//   return (
//     <div className="absolute top-[80px] right-stack-md w-[360px] max-h-[calc(100vh-200px)] flex flex-col bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl shadow-sm z-20 overflow-hidden">
//       <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-surface">
//         <div className="flex items-center gap-2">
//           <span className="material-symbols-outlined text-tertiary">science</span>
//           <h3 className="font-headline-sm text-headline-sm font-semibold text-on-surface">Analysis Modules</h3>
//         </div>
//         <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
//           <span className="material-symbols-outlined">close</span>
//         </button>
//       </div>

//       <div className="flex-1 overflow-y-auto p-stack-md flex flex-col gap-4">
//         {toolsLoading ? (
//            <div className="flex justify-center"><div className="w-6 h-6 border-2 border-tertiary border-t-transparent rounded-full animate-spin"></div></div>
//         ) : (
//           <div className="flex flex-col gap-2">
//             <h4 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Available Tools</h4>
//             {toolsList?.map((tool: Record<string, unknown>) => (
//               <div 
//                 key={tool.tool_id as string}
//                 onClick={() => toggleTool(tool.tool_id as string)}
//                 className={`p-3 rounded-lg border cursor-pointer transition-all ${
//                   selectedTools.includes(tool.tool_id as string) 
//                     ? 'bg-tertiary-container border-tertiary text-on-tertiary-container' 
//                     : 'bg-surface-container-low border-outline-variant hover:border-tertiary'
//                 }`}
//               >
//                 <div className="flex justify-between items-center mb-1">
//                   <span className="font-label-md text-label-md font-semibold">{tool.name as string}</span>
//                   {selectedTools.includes(tool.tool_id as string) && <span className="material-symbols-outlined text-tertiary text-[18px]">check_circle</span>}
//                 </div>
//                 <p className="font-body-sm text-body-sm opacity-80 line-clamp-2">{tool.description as string}</p>
//               </div>
//             ))}
//           </div>
//         )}

//         {selectedTools.length > 0 && toolDetails && (
//           <div className="flex flex-col gap-3 pt-4 border-t border-outline-variant">
//             <h4 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Configuration</h4>
            
//             {toolDetails.user_parameters?.map((param: Record<string, unknown>) => (
//               <div key={param.name as string} className="flex flex-col gap-1">
//                 <div className="flex justify-between items-end">
//                   <label className="font-label-sm text-label-sm text-on-surface">{param.label as string}</label>
//                   {param.type !== 'select' && <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">
//                     {toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
//                   </span>}
//                 </div>
                
//                 {param.type === 'integer' || param.type === 'float' ? (
//                   <input 
//                     type="range" 
//                     min={param.min as number} 
//                     max={param.max as number}
//                     value={toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
//                     onChange={(e) => setToolParam(activeToolId, param.name as string, Number(e.target.value))}
//                     className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-tertiary" 
//                   />
//                 ) : param.type === 'select' ? (
//                   <select 
//                     value={toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
//                     onChange={(e) => setToolParam(activeToolId, param.name as string, e.target.value)}
//                     className="w-full bg-surface-container-low border border-outline-variant rounded p-2 text-body-sm text-on-surface focus:border-tertiary outline-none"
//                   >
//                     {(param.options as Record<string, unknown>[]).map((opt) => (
//                       <option key={opt.value as string} value={opt.value as string}>{opt.label as string}</option>
//                     ))}
//                   </select>
//                 ) : (
//                   <input 
//                     type="text" 
//                     value={toolParams[activeToolId]?.[param.name as string] as string ?? param.default as string}
//                     onChange={(e) => setToolParam(activeToolId, param.name as string, e.target.value)}
//                     className="w-full bg-surface-container-low border border-outline-variant rounded p-2 text-body-sm text-on-surface focus:border-tertiary outline-none"
//                   />
//                 )}
//               </div>
//             ))}
            
//             <div className="mt-2 p-3 bg-surface-variant rounded-lg flex items-center justify-between">
//               <span className="font-label-sm text-label-sm text-on-surface">Est. Runtime</span>
//               <span className="font-mono text-body-sm font-semibold text-on-surface">
//                 ~30s
//               </span>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   )
// }

import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

// ─── Static method catalogue ────────────────────────────────────────────────

const METHOD_GROUPS = [
  {
    id: 'wake',
    label: 'Wind Wake Modeling',
    icon: 'air',
    color: 'text-primary',
    methods: [
      {
        id: 'gaussian_wake',
        name: 'Gaussian Wake',
        ref: 'Bastankhah & Porté-Agel 2014',
        tag: 'Recommended',
        tagClass: 'bg-primary-container text-on-primary-container',
        desc: 'Velocity deficit with real TI-derived wake expansion k*. Monin-Obukhov stability correction from ERA5 fluxes.',
        hasParams: true,
        runtime: '~8s',
      },
      {
        id: 'jensen_wake',
        name: 'Jensen Top-Hat',
        ref: 'Jensen 1983',
        tag: 'Fallback',
        tagClass: 'bg-surface-container-highest text-on-surface-variant',
        desc: 'Cone model. α = 0.5 / ln(z_hub / z₀) where z₀ from real Charnock relation. Faster but less accurate.',
        hasParams: false,
        runtime: '~2s',
      },
    ],
  },
  {
    id: 'acoustic',
    label: 'Underwater Acoustics',
    icon: 'graphic_eq',
    color: 'text-secondary',
    methods: [
      {
        id: 'acoustic',
        name: 'Transmission Loss (François-Garrison)',
        ref: 'François & Garrison 1982',
        tag: 'Exact',
        tagClass: 'bg-primary-container text-on-primary-container',
        desc: 'Full 3-term absorption coefficient. Inputs: T, S, pH, depth from Copernicus. Wenz ambient noise curves.',
        hasParams: true,
        runtime: '~5s',
      },
      {
        id: 'acoustic_construction',
        name: 'Construction Noise (SEL)',
        ref: 'Tougaard et al. 2009',
        tag: 'Optional',
        tagClass: 'bg-surface-container-highest text-on-surface-variant',
        desc: 'Pile-driving SEL_cum = SEL_ss + 10·log₁₀(N). 15 MW monopile 8-10m: 220-240 dB SL peak.',
        hasParams: true,
        runtime: '~3s',
      },
    ],
  },
  {
    id: 'scour',
    label: 'Scour & Sediment',
    icon: 'landslide',
    color: 'text-tertiary',
    methods: [
      {
        id: 'scour',
        name: 'Combined Wave-Current Scour',
        ref: 'Soulsby 1997 · Sumer & Fredsøe 2002',
        tag: 'Recommended',
        tagClass: 'bg-primary-container text-on-primary-container',
        desc: 'τ_mean + τ_max from real H_s, T_p, u(z). Scour depth S/D requires NRCan d50. Shear stress always computed.',
        hasParams: true,
        runtime: '~6s',
      },
    ],
  },
  {
    id: 'species',
    label: 'Species Distribution',
    icon: 'hive',
    color: 'text-secondary',
    methods: [
      {
        id: 'maxent',
        name: 'MaxEnt',
        ref: 'Phillips et al. 2017',
        tag: 'Recommended',
        tagClass: 'bg-primary-container text-on-primary-container',
        desc: '50,000 OBIS occurrences · 9 Copernicus features · elapid · L1 regularization · jackknife importance.',
        hasParams: true,
        runtime: '~40s',
      },
      {
        id: 'bayesian_occupancy',
        name: 'Bayesian Hierarchical Occupancy',
        ref: 'MacKenzie et al. 2002',
        tag: 'Preferred',
        tagClass: 'bg-tertiary-container text-on-tertiary-container',
        desc: 'Accounts for imperfect detection. PyMC + NUTS sampler. logit(ψ) ~ SST + depth + chl.',
        hasParams: false,
        runtime: '~120s',
      },
      {
        id: 'random_forest_sdm',
        name: 'Random Forest SDM',
        ref: 'Breiman 2001',
        tag: 'Alternative',
        tagClass: 'bg-surface-container-highest text-on-surface-variant',
        desc: '10,000 pseudo-absence background points. Permutation feature importance.',
        hasParams: false,
        runtime: '~20s',
      },
    ],
  },
  {
    id: 'lagrangian',
    label: 'Lagrangian Particle',
    icon: 'route',
    color: 'text-primary',
    methods: [
      {
        id: 'lagrangian',
        name: 'RK4 + Stochastic Diffusion',
        ref: 'Van Sebille et al. 2018 · Visser 1997',
        tag: 'Default',
        tagClass: 'bg-primary-container text-on-primary-container',
        desc: 'RK4 advection · Smagorinsky K_h · Pacanowski-Philander K_z · 10-constituent DFO tides · Stokes drift.',
        hasParams: true,
        runtime: '~30s',
      },
    ],
  },
  {
    id: 'emf',
    label: 'Electromagnetic Field',
    icon: 'electric_bolt',
    color: 'text-tertiary',
    methods: [
      {
        id: 'emf',
        name: 'Biot-Savart / Three-Phase AC',
        ref: 'Griffiths 1999',
        tag: 'Simple',
        tagClass: 'bg-surface-container-highest text-on-surface-variant',
        desc: 'Far-field dipole approximation. B_net(r) ≈ 3μ₀Is / (4πr³). 66 kV at 138 A. E_ind = v·B from real currents.',
        hasParams: false,
        runtime: '~1s',
      },
    ],
  },
]

// ─── Component ───────────────────────────────────────────────────────────────

export default function AnalysisMethodsPanel() {
  const [isOpen, setIsOpen] = useState(true)
  const [expandedGroups, setExpandedGroups] = useState<string[]>([
    'wake',
    'lagrangian',
  ])

  const selectedTools = useSimulationStore((s) => s.selectedTools)
  const toggleTool = useSimulationStore((s) => s.toggleTool)

  const toggleGroup = (id: string) =>
    setExpandedGroups((prev) =>
      prev.includes(id) ? prev.filter((g) => g !== id) : [...prev, id]
    )

  const totalRuntime = (() => {
    const runtimes = METHOD_GROUPS.flatMap((g) => g.methods)
      .filter((m) => selectedTools.includes(m.id))
      .map((m) => parseInt(m.runtime.replace(/\D/g, ''), 10) || 0)

    const sum = runtimes.reduce((a, b) => a + b, 0)

    return sum === 0 ? '—' : `~${sum}s`
  })()

  if (!isOpen) {
    return (
      <div
        className="absolute top-[80px] right-stack-md bg-white border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-md z-20 hover:bg-[#f5f5f5] transition-colors"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-tertiary">
          science
        </span>

        <span className="font-label-md text-label-md text-on-surface">
          Analysis Methods
        </span>

        {selectedTools.length > 0 && (
          <span className="w-5 h-5 bg-tertiary text-on-tertiary rounded-full flex items-center justify-center text-[10px] font-bold">
            {selectedTools.length}
          </span>
        )}
      </div>
    )
  }

  return (
    <div className="absolute top-[80px] right-stack-md w-[360px] max-w-[calc(100vw-24px)] max-h-[calc(100vh-120px)] flex flex-col bg-white border border-outline-variant rounded-xl shadow-xl z-20 overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-white flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-tertiary">
            science
          </span>

          <h3 className="font-headline-sm font-semibold text-on-surface">
            Analysis Modules
          </h3>
        </div>

        <button
          onClick={() => setIsOpen(false)}
          className="text-on-surface-variant hover:text-on-surface"
        >
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      {/* Scrollable body */}
      <div
        className="flex-1 overflow-y-auto p-stack-md flex flex-col gap-3"
        style={{
          minHeight: 0,
          scrollbarWidth: 'thin',
        }}
      >
        {METHOD_GROUPS.map((group) => {
          const isExpanded = expandedGroups.includes(group.id)

          const groupSelected = group.methods.filter((m) =>
            selectedTools.includes(m.id)
          ).length

          return (
            <div
              key={group.id}
              className="border border-outline-variant rounded-lg overflow-hidden bg-white"
            >
              {/* Group header */}
              <button
                onClick={() => toggleGroup(group.id)}
                className="w-full flex items-center justify-between p-3 bg-[#fafafa] hover:bg-[#f3f3f3] transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`material-symbols-outlined text-[18px] ${group.color}`}
                  >
                    {group.icon}
                  </span>

                  <span className="font-label-md font-semibold text-on-surface">
                    {group.label}
                  </span>

                  {groupSelected > 0 && (
                    <span className="w-4 h-4 bg-primary text-on-primary rounded-full flex items-center justify-center text-[9px] font-bold">
                      {groupSelected}
                    </span>
                  )}
                </div>

                <span className="material-symbols-outlined text-on-surface-variant text-[18px]">
                  {isExpanded ? 'expand_less' : 'expand_more'}
                </span>
              </button>

              {/* Smooth accordion */}
              <div
                style={{
                  maxHeight: isExpanded ? '700px' : '0px',
                  overflow: 'hidden',
                  transition: 'max-height 0.25s ease',
                  background: '#ffffff',
                }}
              >
                <div className="flex flex-col gap-2 p-2 bg-white">
                  {group.methods.map((method) => {
                    const active = selectedTools.includes(method.id)

                    return (
                      <div
                        key={method.id}
                        onClick={() => toggleTool(method.id)}
                        className={`relative p-3 rounded-lg border cursor-pointer transition-all ${
                          active
                            ? 'border-[#7e4e5b] bg-[#fff5f7]'
                            : 'bg-[#fafafa] border-outline-variant hover:border-[#7e4e5b]/60 hover:bg-[#f3f3f3]'
                        }`}
                      >
                        {/* Check badge */}
                        {active && (
                          <span className="absolute top-2 right-2 w-4 h-4 bg-[#7e4e5b] text-white rounded-full flex items-center justify-center text-[9px]">
                            ✓
                          </span>
                        )}

                        <div className="flex items-start gap-2 mb-1 pr-5">
                          <div className="flex-1 min-w-0">
                            <p className="font-label-md font-semibold text-on-surface">
                              {method.name}
                            </p>

                            <p className="font-label-sm text-on-surface-variant text-[10px] mt-0.5">
                              {method.ref}
                            </p>
                          </div>

                          <span
                            className={`text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded flex-shrink-0 ${method.tagClass}`}
                          >
                            {method.tag}
                          </span>
                        </div>

                        <p className="font-body-sm text-[11px] text-on-surface-variant leading-relaxed">
                          {method.desc}
                        </p>

                        <div className="flex items-center gap-1 mt-2">
                          <span className="material-symbols-outlined text-[12px] text-on-surface-variant">
                            schedule
                          </span>

                          <span className="text-[10px] text-on-surface-variant">
                            {method.runtime}
                          </span>

                          {method.hasParams && (
                            <span className="ml-auto text-[9px] uppercase tracking-wide text-[#7e4e5b] font-semibold">
                              Has params →
                            </span>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Footer */}
      <div className="border-t border-outline-variant p-stack-sm bg-[#f5f3f3] flex-shrink-0">
        <div className="flex items-center justify-between">
          <span className="font-label-sm text-on-surface-variant">
            {selectedTools.length} method
            {selectedTools.length !== 1 ? 's' : ''} selected
          </span>

          <div className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[12px] text-on-surface-variant">
              schedule
            </span>

            <span className="font-label-sm text-on-surface font-semibold font-mono">
              {totalRuntime}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
