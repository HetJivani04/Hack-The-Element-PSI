export default function SimulationDashboard() {
  return (
    <>
      <div className="absolute inset-0 w-full h-full bg-cover bg-center bg-no-repeat z-0" data-alt="A highly detailed, technical, high-fidelity 3D visualization of Earth" style={{backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuAsinrt6Kbncl5bK628Fdogyfgr0tpH2q2i0F3-ozleOZPCYmLWJ1RXFm7ai4rVSsuXl9IptJmPm8-DQmfnnpGTRP0G0yM1Lile8wJqgkVnLtlkFc9P0KddcHsePp7lZjtmhPjnx0CBoZPH3v2t9GE8Zrzkk18cCuc51pF8qrU5I2ouGkHYHhBImVyrXGzPaBKdDglKwUknbaMDn35XrcY9pOL4kk2xu2J6GNeCj2n2mhI7T3Fk4peiyopr4ucrEsxa7bgspzEtPZuP')"}}>
        <div className="absolute inset-0 bg-background/20 backdrop-blur-[2px]"></div>
      </div>
      
      <div className="absolute top-stack-lg right-margin-desktop w-[360px] bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-md flex flex-col gap-stack-md shadow-sm z-20">
        <div className="flex items-center justify-between border-b border-outline-variant pb-stack-sm">
          <h3 className="font-headline-md text-headline-md font-semibold text-on-surface">Windmill Mechanics</h3>
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary transition-colors">info</span>
        </div>
        <div className="flex flex-col gap-stack-md pt-stack-sm">
          <div className="flex flex-col gap-unit">
            <div className="flex justify-between items-end">
              <label className="font-label-md text-label-md text-on-surface">Column Diameter</label>
              <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">12.5 m</span>
            </div>
            <input className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary" max="25" min="5" type="range" defaultValue="12.5"/>
          </div>
          <div className="flex flex-col gap-unit">
            <div className="flex justify-between items-end">
              <label className="font-label-md text-label-md text-on-surface">Floater Radius</label>
              <span className="font-label-sm text-label-sm text-on-surface-variant font-mono">45.0 m</span>
            </div>
            <input className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary" max="80" min="20" type="range" defaultValue="45"/>
          </div>
          <div className="flex flex-col gap-unit mt-stack-sm">
            <label className="font-label-md text-label-md text-on-surface">Material Grade</label>
            <select className="w-full bg-transparent border-b border-outline-variant text-on-surface font-body-md text-body-md py-2 focus:outline-none focus:border-primary focus:border-b-2 transition-all cursor-pointer">
              <option value="s355">S355 Structural Steel</option>
              <option value="s420">S420 High Strength</option>
              <option value="s460">S460 Ultra High Strength</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-stack-sm mt-stack-sm">
            <div className="bg-surface-container-low border border-outline-variant rounded-lg p-3 flex flex-col gap-1">
              <span className="font-label-sm text-label-sm text-on-surface-variant">Est. Fatigue Life</span>
              <span className="font-headline-md text-headline-md text-primary">24.5<span className="text-label-sm">yrs</span></span>
            </div>
            <div className="bg-surface-container-low border border-outline-variant rounded-lg p-3 flex flex-col gap-1">
              <span className="font-label-sm text-label-sm text-on-surface-variant">Displacement</span>
              <span className="font-headline-md text-headline-md text-on-surface">14.2<span className="text-label-sm">kt</span></span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="absolute bottom-stack-lg right-margin-desktop left-margin-desktop max-w-[800px] mx-auto bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-sm flex items-center justify-between shadow-sm z-20">
        <div className="flex gap-stack-md items-center">
          <button className="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface hover:text-primary hover:bg-surface-variant transition-colors">
            <span className="material-symbols-outlined">play_arrow</span>
          </button>
          <div className="h-1 w-64 bg-surface-variant rounded-full overflow-hidden">
            <div className="h-full bg-primary w-1/3 rounded-full"></div>
          </div>
          <span className="font-label-sm text-label-sm text-on-surface-variant font-mono w-20">T+ 04:12:00</span>
        </div>
        <div className="flex gap-stack-sm">
          <span className="px-3 py-1 bg-secondary-container text-on-secondary-container rounded-full font-label-sm text-label-sm flex items-center gap-1 border border-secondary/20">
            <span className="w-2 h-2 rounded-full bg-secondary"></span>
            Live Telemetry
          </span>
          <span className="px-3 py-1 bg-surface-container-low text-on-surface-variant rounded-full font-label-sm text-label-sm border border-outline-variant">
            Grid: Hexagonal
          </span>
        </div>
      </div>
    </>
  );
}
