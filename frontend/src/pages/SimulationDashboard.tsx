import { useRef } from 'react'
import { Viewer, CameraFlyTo, Entity, PointGraphics, PolygonGraphics, PolylineGraphics, type CesiumComponentRef } from 'resium'
import { Cartesian3, Cartesian2, Color, type Viewer as CesiumViewer, Cartographic, Math as CesiumMath } from 'cesium'
import VariableSelectorPanel from '../components/panels/VariableSelectorPanel'
import AnalysisMethodsPanel from '../components/panels/AnalysisMethodsPanel'
import TurbineSpecPanel from '../components/panels/TurbineSpecPanel'
import RegionPanel from '../components/panels/RegionPanel'
import TimeRangePanel from '../components/panels/TimeRangePanel'
import MapToolsPanel from '../components/panels/MapToolsPanel'
import { useSimulationStore } from '../store/simulationStore'
import { useJobStatus } from '../api/client'

export default function SimulationDashboard() {
  const windmillPos = useSimulationStore(state => state.windmillPosition)
  const setWindmillPos = useSimulationStore(state => state.setWindmillPosition)
  const currentJobId = useSimulationStore(state => state.currentJobId)
  
  const { data: jobStatus } = useJobStatus(currentJobId)
  const viewerRef = useRef<CesiumComponentRef<CesiumViewer>>(null)

  const activeMapTool = useSimulationStore(state => state.activeMapTool)
  const setActiveMapTool = useSimulationStore(state => state.setActiveMapTool)
  const boundsDrawingState = useSimulationStore(state => state.boundsDrawingState)
  const setBoundsDrawingState = useSimulationStore(state => state.setBoundsDrawingState)
  const setRegionBounds = useSimulationStore(state => state.setRegionBounds)
  const regionBounds = useSimulationStore(state => state.regionBounds)
  const setManualLat = useSimulationStore(state => state.setManualLat)
  const setManualLon = useSimulationStore(state => state.setManualLon)

  // Map Click Handler
  const handleMapClick = (position: Cartesian2) => {
    if (!activeMapTool) return

    const viewer = viewerRef.current?.cesiumElement
    if (!viewer) return

    const cartesian = viewer.camera.pickEllipsoid(position, viewer.scene.globe.ellipsoid)
    if (!cartesian) return

    const cartographic = Cartographic.fromCartesian(cartesian)
    const lat = CesiumMath.toDegrees(cartographic.latitude)
    const lon = CesiumMath.toDegrees(cartographic.longitude)

    if (activeMapTool === 'pin') {
      setWindmillPos({ lat, lon })
      setManualLat(lat.toFixed(3))
      setManualLon(lon.toFixed(3))
      setActiveMapTool(null)
    } else if (activeMapTool === 'bounds') {
      const newPoints = [...boundsDrawingState.points, { lat, lon }]
      if (newPoints.length === 4) {
        setRegionBounds(newPoints)
        setBoundsDrawingState({ points: [] })
        setActiveMapTool(null)
      } else {
        setBoundsDrawingState({ points: newPoints })
      }
    }
  }

  return (
    <div className="relative w-full h-full overflow-hidden bg-background text-on-background flex flex-col font-body-md text-body-md antialiased">
      {/* Main Content Area */}
      <div className="flex flex-1 relative overflow-hidden">
        
        {/* Left Side Pane */}
        <div className="w-[400px] h-full bg-surface border-r border-outline-variant flex flex-col z-40 flex-shrink-0 overflow-y-auto custom-scrollbar">
          <div className="p-4 border-b border-outline-variant bg-surface-container-low flex-shrink-0">
            <h2 className="font-headline-sm font-bold text-on-surface">Simulation Setup</h2>
            <p className="text-body-sm text-on-surface-variant">Configure environment and turbine parameters</p>
          </div>
          
          <div className="flex-1 p-4 flex flex-col gap-4 bg-surface-container-lowest">
            <VariableSelectorPanel />
            <AnalysisMethodsPanel />
            <RegionPanel />
            <TurbineSpecPanel />
          </div>
        </div>

        {/* Map Area */}
        <main className={`h-full relative bg-surface flex-1 ${activeMapTool ? 'cursor-crosshair' : ''}`}>
          
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
            onClick={(e) => handleMapClick(e.position)}
          >
            <CameraFlyTo 
              duration={0}
              // Default view locked to Scotian Shelf
              destination={Cartesian3.fromDegrees(-63.0, 44.0, 1500000)}
            />
            
            {/* Draw Windmill Pin if set */}
            {windmillPos && (
              <Entity position={Cartesian3.fromDegrees(windmillPos.lon, windmillPos.lat)}>
                <PointGraphics
                  pixelSize={12}
                  color={Color.fromCssColorString('#426446')}
                  outlineColor={Color.WHITE}
                  outlineWidth={3}
                />
              </Entity>
            )}

            {/* Draw current boundary points if drawing */}
            {boundsDrawingState.points.map((p, idx) => (
              <Entity key={idx} position={Cartesian3.fromDegrees(p.lon, p.lat)}>
                <PointGraphics
                  pixelSize={8}
                  color={Color.RED}
                  outlineColor={Color.WHITE}
                  outlineWidth={2}
                />
              </Entity>
            ))}

            {/* Draw lines connecting drawing points */}
            {boundsDrawingState.points.length > 1 && (
              <Entity>
                <PolylineGraphics
                  positions={Cartesian3.fromDegreesArray(
                    boundsDrawingState.points.flatMap(p => [p.lon, p.lat])
                  )}
                  width={2}
                  material={Color.RED.withAlpha(0.8)}
                />
              </Entity>
            )}

            {/* Draw Completed Polygon Box */}
            {regionBounds && regionBounds.length === 4 && (
              <Entity>
                <PolygonGraphics
                  hierarchy={Cartesian3.fromDegreesArray(
                    regionBounds.flatMap(p => [p.lon, p.lat])
                  )}
                  material={Color.RED.withAlpha(0.2)}
                  outline={true}
                  outlineColor={Color.RED}
                  outlineWidth={2}
                />
              </Entity>
            )}
          </Viewer>

          {/* Map Tools Floating on Top Right */}
          <div className="absolute top-[20px] right-[20px] z-30 pointer-events-auto">
            <MapToolsPanel />
          </div>

          {/* Bottom Time Controller */}
          <TimeRangePanel />

          {/* Job progress overlay */}
          {jobStatus && (jobStatus.status === 'queued' || jobStatus.status === 'running') && (
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center pointer-events-auto">
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
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center pointer-events-auto">
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

        </main>
      </div>
    </div>
  )
}
