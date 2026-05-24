// import { Viewer, Camera, Entity, PointGraphics } from 'resium'
// import { Cartesian3, Color } from 'cesium'
// import VariableSelectorPanel from '../components/panels/VariableSelectorPanel'
// import AnalysisMethodsPanel from '../components/panels/AnalysisMethodsPanel'
// import TurbineSpecPanel from '../components/panels/TurbineSpecPanel'
// import TimeRangePanel from '../components/panels/TimeRangePanel'
// import { useSimulationStore } from '../store/simulationStore'
// import { useJobStatus } from '../api/client'

// export default function SimulationDashboard() {
//   const windmillPos = useSimulationStore(state => state.windmillPosition)
//   const setWindmillPos = useSimulationStore(state => state.setWindmillPosition)
//   const currentJobId = useSimulationStore(state => state.currentJobId)
  
//   const { data: jobStatus } = useJobStatus(currentJobId)

//   // Map Click Handler for placing the windmill
//   const handleMapClick = (_movement: unknown) => {
//     // In a real implementation we would pick the ellipsoid and convert to cartographic lat/lon
//     // For now we will mock the location on click so the UI can proceed
//     setWindmillPos({ lat: 44.1, lon: -63.2 }) 
//   }

//   return (
//     <div className="relative w-full h-screen overflow-hidden bg-black">
      
//       {/* 3D Globe */}
//       <Viewer 
//         full 
//         timeline={false} 
//         animation={false} 
//         baseLayerPicker={false}
//         navigationHelpButton={false}
//         sceneModePicker={false}
//         homeButton={false}
//         geocoder={false}
//         infoBox={false}
//         selectionIndicator={false}
//         onClick={handleMapClick}
//       >
//         <Camera 
//           // Default view locked to Scotian Shelf
//           destination={Cartesian3.fromDegrees(-63.0, 44.0, 1500000)}
//         />
        
//         {/* Draw Windmill Pin if set */}
//         {windmillPos && (
//           <Entity position={Cartesian3.fromDegrees(windmillPos.lon, windmillPos.lat)}>
//             <PointGraphics pixelSize={10} color={Color.RED} outlineColor={Color.WHITE} outlineWidth={2} />
//           </Entity>
//         )}
//       </Viewer>

//       {/* Floating UI Panels */}
//       <VariableSelectorPanel />
//       <AnalysisMethodsPanel />
//       <TurbineSpecPanel />
//       <TimeRangePanel />

//       {/* Job Progress Overlay */}
//       {jobStatus && (jobStatus.status === 'queued' || jobStatus.status === 'running') && (
//         <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
//           <div className="bg-surface p-8 rounded-2xl flex flex-col items-center gap-4 max-w-sm w-full text-center">
//              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
//              <h2 className="font-headline-md font-bold text-on-surface">Running Simulation</h2>
//              <p className="font-body-md text-on-surface-variant">
//                {jobStatus.status === 'queued' ? 'Queued...' : 'Computing trajectories...'}
//              </p>
//              {jobStatus.progress && (
//                <div className="w-full mt-4">
//                  <div className="flex justify-between text-label-sm mb-1">
//                    <span>{jobStatus.progress.percent}%</span>
//                  </div>
//                  <div className="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
//                    <div className="bg-primary h-full" style={{ width: `${jobStatus.progress.percent}%` }}></div>
//                  </div>
//                </div>
//              )}
//           </div>
//         </div>
//       )}

//       {/* Job Complete Overlay (Mock transition to Results) */}
//       {jobStatus?.status === 'completed' && (
//         <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
//            <div className="bg-surface p-8 rounded-2xl flex flex-col items-center gap-4 max-w-sm w-full text-center">
//              <span className="material-symbols-outlined text-green-500 text-5xl">check_circle</span>
//              <h2 className="font-headline-md font-bold text-on-surface">Simulation Complete!</h2>
//              <p className="font-body-md text-on-surface-variant">
//                Trajectories and density maps have been computed.
//              </p>
//              <button 
//                className="mt-4 px-6 py-2 bg-primary text-on-primary rounded-full font-bold"
//                onClick={() => window.location.hash = '#/results'} // Just a mock action
//              >
//                View Results
//              </button>
//            </div>
//         </div>
//       )}
//     </div>
//   )
// }

import { Viewer, Camera, Entity, PointGraphics } from 'resium'
import { Cartesian3, Color } from 'cesium'
import VariableSelectorPanel from '../components/panels/VariableSelectorPanel'
import AnalysisMethodsPanel from '../components/panels/AnalysisMethodsPanel'
import MethodParamsPanel from '../components/panels/Methodparamspanel'
import TurbineSpecPanel from '../components/panels/TurbineSpecPanel'
import TimeRangePanel from '../components/panels/TimeRangePanel'
import { useSimulationStore } from '../store/simulationStore'
import { useJobStatus } from '../api/client' 

export default function SimulationDashboard() {
  const windmillPos    = useSimulationStore((s) => s.windmillPosition)
  const setWindmillPos = useSimulationStore((s) => s.setWindmillPosition)
  const setManualLat   = useSimulationStore((s) => s.setManualLat)
  const setManualLon   = useSimulationStore((s) => s.setManualLon)
  const currentJobId   = useSimulationStore((s) => s.currentJobId)

  const { data: jobStatus } = useJobStatus(currentJobId)

  // Map click: place pin and sync manual coord inputs
  const handleMapClick = (_movement: unknown) => {
    const lat = 44.1
    const lon = -63.2
    setWindmillPos({ lat, lon })
    setManualLat(lat.toFixed(3))
    setManualLon(lon.toFixed(3))
  }

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">

      {/* 3D Globe */}
      <Viewer
        full
        timeline={false}
        animation={false}
        baseLayerPicker={false}
        navigationHelpButton={false}
        sceneModePicker={false}
        homeButton={false}
        geocoder={false}
        infoBox={false}
        selectionIndicator={false}
        onClick={handleMapClick}
      >
        <Camera
          position={Cartesian3.fromDegrees(-63.0, 44.0, 1500000)}
        />

        {windmillPos && (
          <Entity position={Cartesian3.fromDegrees(windmillPos.lon, windmillPos.lat)}>
            <PointGraphics
              pixelSize={10}
              color={Color.fromCssColorString('#426446')}
              outlineColor={Color.WHITE}
              outlineWidth={2}
            />
          </Entity>
        )}
      </Viewer>

      {/* Floating panels — left column */}
      <VariableSelectorPanel />
      <TurbineSpecPanel />

      {/* Floating panels — right column */}
      <AnalysisMethodsPanel />
      {/* MethodParamsPanel auto-hides when no methods are selected */}
      <MethodParamsPanel />

      {/* Bottom bar */}
      <TimeRangePanel />

      {/* Job progress overlay */}
      {jobStatus && (jobStatus.status === 'queued' || jobStatus.status === 'running') && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-surface p-8 rounded-2xl flex flex-col items-center gap-4 max-w-sm w-full text-center">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <h2 className="font-headline-md font-bold text-on-surface">Running Simulation</h2>
            <p className="font-body-md text-on-surface-variant">
              {jobStatus.status === 'queued' ? 'Queued…' : 'Computing trajectories…'}
            </p>
            {jobStatus.progress && (
              <div className="w-full mt-4">
                <div className="flex justify-between text-label-sm mb-1">
                  <span>{jobStatus.progress.percent}%</span>
                </div>
                <div className="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-primary h-full transition-all duration-300"
                    style={{ width: `${jobStatus.progress.percent}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Job complete overlay */}
      {jobStatus?.status === 'completed' && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-surface p-8 rounded-2xl flex flex-col items-center gap-4 max-w-sm w-full text-center">
            <span className="material-symbols-outlined text-green-500 text-5xl">check_circle</span>
            <h2 className="font-headline-md font-bold text-on-surface">Simulation Complete!</h2>
            <p className="font-body-md text-on-surface-variant">
              Trajectories and density maps have been computed.
            </p>
            <button
              className="mt-4 px-6 py-2 bg-primary text-on-primary rounded-full font-bold"
              onClick={() => (window.location.hash = '#/results')}
            >
              View Results
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
