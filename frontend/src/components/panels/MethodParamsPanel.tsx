import { useState } from 'react'
import { useSimulationStore } from '../../store/simulationStore'

type ActiveTab = 'gaussian_wake' | 'acoustic' | 'scour' | 'lagrangian' | 'maxent'

const TAB_META: Record<string, { label: string; icon: string }> = {
  gaussian_wake:  { label: 'Gaussian Wake', icon: 'air' },
  jensen_wake:    { label: 'Jensen Wake',   icon: 'air' },
  acoustic:       { label: 'Acoustics',     icon: 'graphic_eq' },
  acoustic_construction: { label: 'Construction SEL', icon: 'construction' },
  scour:          { label: 'Scour',         icon: 'landslide' },
  lagrangian:     { label: 'Lagrangian',    icon: 'route' },
  maxent:         { label: 'MaxEnt',        icon: 'hive' },
  bayesian_occupancy: { label: 'Bayesian', icon: 'functions' },
  random_forest_sdm: { label: 'RF SDM',   icon: 'forest' },
  emf:            { label: 'EMF',           icon: 'electric_bolt' },
}

// Methods that have configurable params
const PARAM_METHODS = new Set(['gaussian_wake', 'acoustic', 'acoustic_construction', 'scour', 'lagrangian', 'maxent'])

function SliderRow({
  label,
  value,
  min,
  max,
  step,
  display,
  onChange,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  display?: string
  onChange: (v: number) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-end">
        <label className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant">
          {label}
        </label>
        <span className="font-label-sm text-[11px] font-mono text-on-surface font-semibold">
          {display ?? value}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-tertiary"
      />
    </div>
  )
}

function SelectRow({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: { value: string; label: string }[]
  onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-2 text-[12px] text-on-surface focus:border-tertiary outline-none cursor-pointer"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  )
}

function CheckRow({
  label,
  checked,
  onChange,
  note,
}: {
  label: string
  checked: boolean
  onChange: (v: boolean) => void
  note?: string
}) {
  return (
    <label className="flex items-start gap-2 cursor-pointer group">
      <div
        onClick={() => onChange(!checked)}
        className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center transition-colors flex-shrink-0 ${
          checked ? 'bg-tertiary border-tertiary' : 'border-outline group-hover:border-tertiary'
        }`}
      >
        {checked && <span className="text-on-tertiary text-[10px] font-bold">✓</span>}
      </div>
      <div>
        <span className="font-label-sm text-[12px] text-on-surface">{label}</span>
        {note && <p className="font-body-sm text-[10px] text-on-surface-variant mt-0.5">{note}</p>}
      </div>
    </label>
  )
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="font-label-sm text-[10px] uppercase tracking-wider text-on-surface-variant mt-2">
      {children}
    </p>
  )
}

function InfoBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-2 p-2 rounded-lg bg-primary-container/20 border border-primary/20">
      <span className="material-symbols-outlined text-[13px] text-primary flex-shrink-0 mt-0.5">info</span>
      <p className="text-[11px] text-on-surface-variant leading-relaxed">{children}</p>
    </div>
  )
}

// ─── Per-method param sections ───────────────────────────────────────────────

function GaussianWakeSection() {
  const p = useSimulationStore((s) => s.methodParams.gaussian_wake)
  const set = useSimulationStore((s) => s.setGaussianWakeParam)

  return (
    <div className="flex flex-col gap-3">
      <SectionLabel>Wake expansion</SectionLabel>
      <InfoBox>k* = 0.35 · TI from real ERA5 friction velocity u*. Enable override to fix manually.</InfoBox>
      <CheckRow
        label="Override k*"
        checked={p.kStarOverride}
        onChange={(v) => set('kStarOverride', v)}
      />
      {p.kStarOverride && (
        <SliderRow
          label="k* wake expansion rate"
          value={p.kStar}
          min={0.01} max={0.10} step={0.001}
          display={p.kStar.toFixed(3)}
          onChange={(v) => set('kStar', v)}
        />
      )}
      <SliderRow
        label="Initial wake width ε"
        value={p.epsilon}
        min={0.05} max={0.50} step={0.01}
        display={p.epsilon.toFixed(2)}
        onChange={(v) => set('epsilon', v)}
      />

      <SectionLabel>Atmospheric stability</SectionLabel>
      <SelectRow
        label="Stability regime"
        value={p.stabilityRegime}
        options={[
          { value: 'auto',     label: 'Auto — from ERA5 fluxes' },
          { value: 'neutral',  label: 'Force neutral' },
          { value: 'stable',   label: 'Force stable' },
          { value: 'unstable', label: 'Force unstable' },
        ]}
        onChange={(v) => set('stabilityRegime', v as typeof p.stabilityRegime)}
      />
      <SliderRow
        label="Dyer ψ_m exponent (unstable)"
        value={p.dyerExponent}
        min={-0.50} max={0} step={0.01}
        display={p.dyerExponent.toFixed(2)}
        onChange={(v) => set('dyerExponent', v)}
      />

      <SectionLabel>Wake-added turbulence</SectionLabel>
      <SelectRow
        label="TI model"
        value={p.wakeTurbulenceModel}
        options={[
          { value: 'frandsen', label: 'Frandsen 2007' },
          { value: 'none',     label: 'Disabled' },
        ]}
        onChange={(v) => set('wakeTurbulenceModel', v as typeof p.wakeTurbulenceModel)}
      />
    </div>
  )
}

function AcousticSection() {
  const p = useSimulationStore((s) => s.methodParams.acoustic)
  const set = useSimulationStore((s) => s.setAcousticParam)

  return (
    <div className="flex flex-col gap-3">
      <SectionLabel>Geometric spreading</SectionLabel>
      <InfoBox>
        Shelf: cylindrical (15 log r) · Deep: spherical (20 log r) · Very shallow: 10 log r.
        Set to match site bathymetry.
      </InfoBox>
      <SelectRow
        label="Spreading regime"
        value={p.geometricSpread}
        options={[
          { value: 'cylindrical', label: 'Cylindrical (Scotian Shelf)' },
          { value: 'spherical',   label: 'Spherical (deep water)' },
          { value: 'shallow',     label: 'Very shallow (10 log r)' },
        ]}
        onChange={(v) => set('geometricSpread', v as typeof p.geometricSpread)}
      />
      <SectionLabel>Construction noise</SectionLabel>
      <CheckRow
        label="Include pile-driving SEL"
        checked={p.includeConstruction}
        onChange={(v) => set('includeConstruction', v)}
        note="SEL_cum = SEL_ss + 10·log₁₀(N). Monopile 8-10m: 220-240 dB peak SL."
      />
      {p.includeConstruction && (
        <SliderRow
          label="Hammer strokes N"
          value={p.pileStrokes}
          min={200} max={3000} step={50}
          display={p.pileStrokes.toString()}
          onChange={(v) => set('pileStrokes', v)}
        />
      )}
    </div>
  )
}

function ScourSection() {
  const p = useSimulationStore((s) => s.methodParams.scour)
  const set = useSimulationStore((s) => s.setScourParam)

  return (
    <div className="flex flex-col gap-3">
      <InfoBox>
        Shear stress τ_c, τ_w, τ_cw always computed from real currents + waves. Scour depth S/D
        requires d50 — if NRCan data unavailable, only shear stress is output.
      </InfoBox>
      <SectionLabel>Sediment grain size</SectionLabel>
      <CheckRow
        label="Override d50 (skip NRCan lookup)"
        checked={p.sedimentGradeOverride}
        onChange={(v) => set('sedimentGradeOverride', v)}
      />
      {p.sedimentGradeOverride && (
        <SliderRow
          label="d50 (mm)"
          value={p.d50mm}
          min={0.06} max={2.0} step={0.01}
          display={p.d50mm.toFixed(2) + ' mm'}
          onChange={(v) => set('d50mm', v)}
        />
      )}
    </div>
  )
}

function LagrangianSection() {
  const p = useSimulationStore((s) => s.methodParams.lagrangian)
  const set = useSimulationStore((s) => s.setLagrangianParam)

  return (
    <div className="flex flex-col gap-3">
      <SectionLabel>Integrator</SectionLabel>
      <SelectRow
        label="Time-stepping scheme"
        value={p.integrator}
        options={[
          { value: 'rk4',   label: 'RK4 — O(Δt⁵) error (recommended)' },
          { value: 'rk2',   label: 'RK2 — O(Δt³) error' },
          { value: 'euler', label: 'Euler — O(Δt²) error (fast)' },
        ]}
        onChange={(v) => set('integrator', v as typeof p.integrator)}
      />

      <SectionLabel>Particles & timestep</SectionLabel>
      <SliderRow
        label="N particles"
        value={p.nParticles}
        min={100} max={10000} step={100}
        display={p.nParticles.toLocaleString()}
        onChange={(v) => set('nParticles', v)}
      />
      <SliderRow
        label="Δt (seconds)"
        value={p.dtSeconds}
        min={60} max={7200} step={60}
        display={p.dtSeconds + 's'}
        onChange={(v) => set('dtSeconds', v)}
      />

      <SectionLabel>Physics toggles</SectionLabel>
      <CheckRow
        label="Stokes drift"
        checked={p.includeStokes}
        onChange={(v) => set('includeStokes', v)}
        note="Copernicus WAV VSDX/VSDY preferred. Falls back to monochromatic approximation."
      />
      <CheckRow
        label="10-constituent tidal currents"
        checked={p.includeTides}
        onChange={(v) => set('includeTides', v)}
        note="M2·S2·N2·K2·K1·O1·P1·Q1·M4·MSf from DFO WebTide (Scotian Shelf)."
      />
      <CheckRow
        label="Windage"
        checked={p.includeWindage}
        onChange={(v) => set('includeWindage', v)}
        note="C_d = 0.01 + 0.003·(U₁₀ - 5) from ERA5 10m wind."
      />
    </div>
  )
}

function MaxEntSection() {
  const p = useSimulationStore((s) => s.methodParams.maxent)
  const set = useSimulationStore((s) => s.setMaxEntParam)
  const featureOptions = ['linear', 'quadratic', 'product', 'threshold', 'hinge']

  return (
    <div className="flex flex-col gap-3">
      <InfoBox>
        Features: SST, SST range, SSS, depth, chl mean/max, sea ice, SST fronts, slope.
        50,000 OBIS occurrence records from Scotian Shelf ROI.
      </InfoBox>
      <SectionLabel>Sampling</SectionLabel>
      <SliderRow
        label="Occurrence records"
        value={p.nOccurrences}
        min={5000} max={100000} step={1000}
        display={p.nOccurrences.toLocaleString()}
        onChange={(v) => set('nOccurrences', v)}
      />
      <SliderRow
        label="L1 regularization multiplier"
        value={p.regularizationMultiplier}
        min={0.1} max={5.0} step={0.1}
        display={p.regularizationMultiplier.toFixed(1)}
        onChange={(v) => set('regularizationMultiplier', v)}
      />
      <SectionLabel>Feature types</SectionLabel>
      <div className="flex flex-wrap gap-2">
        {featureOptions.map((f) => {
          const active = p.featureTypes.includes(f)
          return (
            <button
              key={f}
              onClick={() =>
                set('featureTypes', active
                  ? p.featureTypes.filter((x) => x !== f)
                  : [...p.featureTypes, f]
                )
              }
              className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-all ${
                active
                  ? 'bg-tertiary-container border-tertiary text-on-surface'
                  : 'bg-surface-container-low border-outline-variant text-on-surface-variant hover:border-tertiary'
              }`}
            >
              {f}
            </button>
          )
        })}
      </div>
    </div>
  )
}

function NoParams({ name }: { name: string }) {
  return (
    <div className="flex flex-col items-center gap-2 py-8 text-center">
      <span className="material-symbols-outlined text-3xl text-on-surface-variant">check_circle</span>
      <p className="font-label-md text-on-surface">{name}</p>
      <p className="font-body-sm text-[11px] text-on-surface-variant max-w-[220px]">
        This method uses sensible defaults derived entirely from real Copernicus data. No manual parameters needed.
      </p>
    </div>
  )
}

// ─── Main panel ──────────────────────────────────────────────────────────────

export default function MethodParamsPanel() {
  const selectedTools = useSimulationStore((s) => s.selectedTools)
  const [isOpen, setIsOpen] = useState(true)

  // Only show tabs for selected methods
  const activeTabs = selectedTools.filter((id) => TAB_META[id])
  const [activeTab, setActiveTab] = useState<string | null>(null)

  const currentTab = activeTab && activeTabs.includes(activeTab)
    ? activeTab
    : activeTabs[0] ?? null

  if (activeTabs.length === 0) return null

  if (!isOpen) {
    return (
      <div
        className="absolute top-[80px] right-[384px] bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center gap-2 cursor-pointer shadow-sm z-20 hover:bg-surface-variant transition-colors"
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-tertiary">tune</span>
        <span className="font-label-md text-label-md text-on-surface">Method Params</span>
      </div>
    )
  }

  return (
    <div className="absolute top-[80px] right-[384px] w-[300px] max-h-[calc(100vh-200px)] flex flex-col bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl shadow-sm z-20 overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-outline-variant p-stack-md bg-surface flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-tertiary">tune</span>
          <h3 className="font-headline-sm font-semibold text-on-surface">Method Params</h3>
        </div>
        <button onClick={() => setIsOpen(false)} className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      {/* Tab strip */}
      {activeTabs.length > 1 && (
        <div className="flex overflow-x-auto border-b border-outline-variant bg-surface-container-low flex-shrink-0 scrollbar-hide">
          {activeTabs.map((id) => {
            const meta = TAB_META[id]
            if (!meta) return null
            return (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex items-center gap-1 px-3 py-2 text-[11px] font-semibold whitespace-nowrap border-b-2 transition-colors flex-shrink-0 ${
                  currentTab === id
                    ? 'border-tertiary text-tertiary'
                    : 'border-transparent text-on-surface-variant hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[13px]">{meta.icon}</span>
                {meta.label}
              </button>
            )
          })}
        </div>
      )}

      {/* Active tab title (single tab) */}
      {activeTabs.length === 1 && currentTab && (
        <div className="px-stack-md py-2 bg-surface-container-lowest border-b border-outline-variant flex-shrink-0">
          <div className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[14px] text-tertiary">
              {TAB_META[currentTab]?.icon}
            </span>
            <span className="font-label-md text-[12px] text-on-surface-variant">
              {TAB_META[currentTab]?.label} — active
            </span>
          </div>
        </div>
      )}

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-stack-md">
        {currentTab === 'gaussian_wake'  && <GaussianWakeSection />}
        {currentTab === 'acoustic'       && <AcousticSection />}
        {currentTab === 'acoustic_construction' && <AcousticSection />}
        {currentTab === 'scour'          && <ScourSection />}
        {currentTab === 'lagrangian'     && <LagrangianSection />}
        {currentTab === 'maxent'         && <MaxEntSection />}
        {currentTab && !PARAM_METHODS.has(currentTab) && (
          <NoParams name={TAB_META[currentTab]?.label ?? currentTab} />
        )}
      </div>
    </div>
  )
}
