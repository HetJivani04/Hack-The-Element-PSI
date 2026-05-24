import { useRef } from 'react'
import { Viewer, CameraFlyTo, Entity, PointGraphics, RectangleGraphics, type CesiumComponentRef } from 'resium'
import { Cartesian3, Color, Rectangle, Math as CesiumMath, type Viewer as CesiumViewer } from 'cesium'
import VariableSelectorPanel from '../components/panels/VariableSelectorPanel'
import AnalysisMethodsPanel from '../components/panels/AnalysisMethodsPanel'
import TurbineSpecPanel from '../components/panels/TurbineSpecPanel'
import RegionPanel from '../components/panels/RegionPanel'
import TimeRangePanel from '../components/panels/TimeRangePanel'
import { useSimulationStore } from '../store/simulationStore'
import { useJobStatus, useRegion } from '../api/client'

export default function SimulationDashboard() {
  const windmillPos = useSimulationStore(state => state.windmillPosition)
  const setWindmillPos = useSimulationStore(state => state.setWindmillPosition)
  const regionBounds = useSimulationStore(state => state.regionBounds)
  const currentJobId = useSimulationStore(state => state.currentJobId)
  
  const { data: jobStatus } = useJobStatus(currentJobId)
  const { data: regionData } = useRegion()
  const viewerRef = useRef<CesiumComponentRef<CesiumViewer>>(null)

  // Map Click Handler for placing the windmill
  const handleMapClick = (movement: any) => {
    const viewer = viewerRef.current?.cesiumElement
    if (!viewer) return
    
    // Pick the ellipsoid to get the true 3D position
    const pickedPosition = viewer.scene.camera.pickEllipsoid(movement.position, viewer.scene.globe.ellipsoid)
    
    if (pickedPosition) {
      const cartographic = viewer.scene.globe.ellipsoid.cartesianToCartographic(pickedPosition)
      const lon = CesiumMath.toDegrees(cartographic.longitude)
      const lat = CesiumMath.toDegrees(cartographic.latitude)
      
      // Validate against bounding box if available
      if (regionBounds) {
        const { southwest, northeast } = regionBounds
        if (lon >= southwest.lon && lon <= northeast.lon && lat >= southwest.lat && lat <= northeast.lat) {
          setWindmillPos({ lat, lon }) 
        } else {
          // Optionally alert the user they clicked out of bounds, or just ignore
          console.warn("Clicked outside the simulation bounding box.")
        }
      } else {
        setWindmillPos({ lat, lon })
      }
    }
  }

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      
      {/* 3D Globe */}
      <Viewer 
        ref={viewerRef}
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
        <CameraFlyTo 
          duration={0}
          once={true}
          // Default view locked to Scotian Shelf
          destination={Cartesian3.fromDegrees(-63.0, 44.0, 1500000)}
        />
        {/* Draw Region Bounding Box */}
        {regionBounds && (
          <Entity>
            <RectangleGraphics
              coordinates={Rectangle.fromDegrees(
                regionBounds.southwest.lon,
                regionBounds.southwest.lat,
                regionBounds.northeast.lon,
                regionBounds.northeast.lat
              )}
              material={Color.TEAL.withAlpha(0.1)}
              outline={true}
              outlineColor={Color.TEAL}
              outlineWidth={2}
            />
          </Entity>
        )}
        
        {/* Draw Windmill Pin if set */}
        {windmillPos && (
          <Entity position={Cartesian3.fromDegrees(windmillPos.lon, windmillPos.lat)}>
            <PointGraphics pixelSize={10} color={Color.RED} outlineColor={Color.WHITE} outlineWidth={2} />
          </Entity>
        )}
      </Viewer>

      {/* Floating UI Panels */}
      <VariableSelectorPanel />
      <AnalysisMethodsPanel />
      <TurbineSpecPanel />
      <RegionPanel />
      <TimeRangePanel />

      {/* Job Progress Overlay */}
      {jobStatus && (jobStatus.status === 'queued' || jobStatus.status === 'running') && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-surface p-8 rounded-2xl flex flex-col items-center gap-4 max-w-sm w-full text-center">
             <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
             <h2 className="font-headline-md font-bold text-on-surface">Running Simulation</h2>
             <p className="font-body-md text-on-surface-variant">
               {jobStatus.status === 'queued' ? 'Queued...' : 'Computing trajectories...'}
             </p>
             {jobStatus.progress && (
               <div className="w-full mt-4">
                 <div className="flex justify-between text-label-sm mb-1">
                   <span>{jobStatus.progress.percent}%</span>
                 </div>
                 <div className="w-full bg-surface-variant h-2 rounded-full overflow-hidden">
                   <div className="bg-primary h-full" style={{ width: `${jobStatus.progress.percent}%` }}></div>
                 </div>
               </div>
             )}
          </div>
        </div>
      )}

      {/* Job Complete Overlay (Mock transition to Results) */}
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
               onClick={() => window.location.hash = '#/results'} // Just a mock action
             >
               View Results
             </button>
           </div>
        </div>
      )}
    </div>
  )
}
