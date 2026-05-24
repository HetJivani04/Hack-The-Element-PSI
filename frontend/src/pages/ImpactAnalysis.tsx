export default function ImpactAnalysis() {
  return (
    <div className="flex-1 p-margin-mobile md:p-margin-desktop bg-surface">
      <div className="mb-section-gap">
        <h1 className="font-display-lg-mobile md:font-display-lg text-primary mb-2">PSI Analysis</h1>
        <p className="font-body-lg text-on-surface-variant">Real-time environmental impact monitoring for Northern Coastal Region Alpha.</p>
      </div>

      {/* Bento Grid Layout */}
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
            <span className="material-symbols-outlined text-[16px]">trending_up</span> +2.4% from last quarter
          </p>
        </div>

        {/* Ecosystem Impact Matrix (Span 8) */}
        <div className="md:col-span-8 bg-surface-container-lowest border border-outline-variant rounded-xl p-stack-lg flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="font-headline-md text-primary mb-1">Impact Matrix</h3>
              <p className="font-label-sm text-on-surface-variant uppercase tracking-wider">Heat levels across primary domains</p>
            </div>
            <div className="flex gap-2">
              <span className="px-2 py-1 bg-surface-container text-on-surface-variant rounded font-label-sm text-[10px]">Low</span>
              <span className="px-2 py-1 bg-secondary-container text-on-secondary-container rounded font-label-sm text-[10px]">Med</span>
              <span className="px-2 py-1 bg-tertiary-container text-on-tertiary-container rounded font-label-sm text-[10px]">High</span>
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
              <div className="bg-surface-container h-12 rounded flex items-center px-3 border border-outline-variant border-opacity-30">
                <span className="font-label-sm text-on-surface-variant">Phytoplankton</span>
                <div className="ml-auto w-3 h-3 rounded-full bg-surface-variant"></div>
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
              <div className="bg-surface-container h-12 rounded flex items-center px-3 border border-outline-variant border-opacity-30">
                <span className="font-label-sm text-on-surface-variant">Benthic Species</span>
                <div className="ml-auto w-3 h-3 rounded-full bg-secondary-container"></div>
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
              <div className="bg-surface-container h-12 rounded flex items-center px-3 border border-outline-variant border-opacity-30">
                <span className="font-label-sm text-on-surface-variant">Salinity</span>
                <div className="ml-auto w-3 h-3 rounded-full bg-surface-variant"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Acoustic Disturbance Profile (Span 12) */}
        <div className="md:col-span-12 bg-surface-container-lowest border border-outline-variant rounded-xl p-stack-lg">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h3 className="font-headline-md text-primary mb-1">Acoustic Disturbance Profile</h3>
              <p className="font-label-sm text-on-surface-variant uppercase tracking-wider">Baseline vs Simulated Noise Levels (dB)</p>
            </div>
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-surface-container-highest border border-outline-variant rounded-sm"></div>
                <span className="font-label-sm text-on-surface-variant">Baseline</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-tertiary border border-tertiary rounded-sm"></div>
                <span className="font-label-sm text-on-surface-variant">Simulated</span>
              </div>
            </div>
          </div>
          
          {/* CSS Bar Chart */}
          <div className="h-64 flex items-end gap-2 sm:gap-4 md:gap-8 pb-8 border-b border-outline-variant relative">
            {/* Y-axis labels */}
            <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-[10px] text-on-surface-variant pr-2 border-r border-outline-variant opacity-50 pb-8">
              <span>120dB</span>
              <span>90dB</span>
              <span>60dB</span>
              <span>30dB</span>
              <span>0</span>
            </div>
            <div className="flex-1 flex justify-around pl-12 h-full items-end">
              {/* Zone 1 */}
              <div className="flex flex-col items-center group relative h-full justify-end">
                <div className="flex gap-1 items-end h-[80%]">
                  <div className="w-4 sm:w-8 bg-surface-container-highest border border-outline-variant rounded-t-sm h-[40%] transition-all duration-300"></div>
                  <div className="w-4 sm:w-8 bg-tertiary border border-tertiary rounded-t-sm h-[85%] transition-all duration-300"></div>
                </div>
                <span className="absolute -bottom-6 font-label-sm text-on-surface-variant text-xs">Nearshore</span>
              </div>
              {/* Zone 2 */}
              <div className="flex flex-col items-center group relative h-full justify-end">
                <div className="flex gap-1 items-end h-[80%]">
                  <div className="w-4 sm:w-8 bg-surface-container-highest border border-outline-variant rounded-t-sm h-[50%] transition-all duration-300"></div>
                  <div className="w-4 sm:w-8 bg-tertiary border border-tertiary rounded-t-sm h-[70%] transition-all duration-300"></div>
                </div>
                <span className="absolute -bottom-6 font-label-sm text-on-surface-variant text-xs">Mid-Shelf</span>
              </div>
              {/* Zone 3 */}
              <div className="flex flex-col items-center group relative h-full justify-end">
                <div className="flex gap-1 items-end h-[80%]">
                  <div className="w-4 sm:w-8 bg-surface-container-highest border border-outline-variant rounded-t-sm h-[65%] transition-all duration-300"></div>
                  <div className="w-4 sm:w-8 bg-tertiary border border-tertiary rounded-t-sm h-[95%] transition-all duration-300"></div>
                </div>
                <span className="absolute -bottom-6 font-label-sm text-on-surface-variant text-xs">Deep Trench</span>
              </div>
              {/* Zone 4 */}
              <div className="flex flex-col items-center group relative h-full justify-end">
                <div className="flex gap-1 items-end h-[80%]">
                  <div className="w-4 sm:w-8 bg-surface-container-highest border border-outline-variant rounded-t-sm h-[30%] transition-all duration-300"></div>
                  <div className="w-4 sm:w-8 bg-tertiary border border-tertiary rounded-t-sm h-[45%] transition-all duration-300"></div>
                </div>
                <span className="absolute -bottom-6 font-label-sm text-on-surface-variant text-xs">Protected Bay</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div className="mb-section-gap h-64 rounded-xl border border-outline-variant overflow-hidden relative">
        <div className="absolute inset-0 bg-secondary-fixed-dim opacity-20"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-body-md text-on-surface-variant bg-surface-container-lowest px-4 py-2 rounded-full shadow-sm border border-outline-variant flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">map</span> Map Visualization Placeholder
          </span>
        </div>
      </div>
    </div>
  );
}
