import { useRef, useState, useEffect } from 'react'
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const windmillPos = useSimulationStore(state => state.windmillPosition)
  const setWindmillPos = useSimulationStore(state => state.setWindmillPosition)
  const currentJobId = useSimulationStore(state => state.currentJobId)
  
  const [hideCompletionModal, setHideCompletionModal] = useState(false)
  useEffect(() => {
    setHideCompletionModal(false)
  }, [currentJobId])
  
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
      setIsSidebarOpen(true)
    } else if (activeMapTool === 'bounds') {
      const newPoints = [...boundsDrawingState.points, { lat, lon }]
      if (newPoints.length === 4) {
        setRegionBounds(newPoints)
        setBoundsDrawingState({ points: [] })
        setActiveMapTool(null)
        setIsSidebarOpen(true)
      } else {
        setBoundsDrawingState({ points: newPoints })
      }
    }
  }

  // Open sidebar when map tool is clicked
  useEffect(() => {
    if (activeMapTool) {
      setIsSidebarOpen(true)
    }
  }, [activeMapTool])

  // Handle Startup Zoom Animation
  useEffect(() => {
    let timeoutId: any;
    let hasAnimated = false;
    
    const checkViewer = () => {
      if (hasAnimated) return;
      const viewer = viewerRef.current?.cesiumElement;
      if (viewer) {
        hasAnimated = true;
        // Start completely zoomed out
        viewer.camera.setView({
          destination: Cartesian3.fromDegrees(-63.0, 44.0, 20000000)
        });
        
        // Wait 800ms before zooming in
        setTimeout(() => {
          if (windmillPos) {
            viewer.camera.flyTo({
              destination: Cartesian3.fromDegrees(windmillPos.lon, windmillPos.lat, 1500000),
              duration: 3
            });
          } else if (regionBounds && regionBounds.length > 0) {
            const avgLon = regionBounds.reduce((sum, p) => sum + p.lon, 0) / regionBounds.length;
            const avgLat = regionBounds.reduce((sum, p) => sum + p.lat, 0) / regionBounds.length;
            viewer.camera.flyTo({
              destination: Cartesian3.fromDegrees(avgLon, avgLat, 1500000),
              duration: 3
            });
          } else {
            if ('geolocation' in navigator) {
              navigator.geolocation.getCurrentPosition(
                (pos) => {
                  viewer.camera.flyTo({
                    destination: Cartesian3.fromDegrees(pos.coords.longitude, pos.coords.latitude, 1500000),
                    duration: 3
                  });
                },
                () => {
                  viewer.camera.flyTo({
                    destination: Cartesian3.fromDegrees(-63.0, 44.0, 1500000),
                    duration: 3
                  });
                }
              );
            } else {
              viewer.camera.flyTo({
                destination: Cartesian3.fromDegrees(-63.0, 44.0, 1500000),
                duration: 3
              });
            }
          }
        }, 800);
      } else {
        timeoutId = setTimeout(checkViewer, 100);
      }
    };
    checkViewer();
    return () => clearTimeout(timeoutId);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="relative w-full h-full overflow-hidden bg-background text-on-background flex flex-col font-body-md text-body-md antialiased">
      {/* Main Content Area */}
      <div className="flex flex-1 relative overflow-hidden">
        
        {/* Left Side Pane */}
        <div 
          className={`h-full bg-surface border-r border-outline-variant flex flex-col z-40 flex-shrink-0 overflow-y-auto custom-scrollbar transition-all duration-300 ${
            isSidebarOpen ? 'w-[400px] translate-x-0' : 'w-0 -translate-x-full border-r-0'
          }`}
        >
          {isSidebarOpen && (
            <>
              <div className="p-4 border-b border-outline-variant bg-surface-container-low flex-shrink-0 flex justify-between items-center">
                <div>
                  <h2 className="font-headline-sm font-bold text-on-surface">Simulation Setup</h2>
                  <p className="text-body-sm text-on-surface-variant">Configure environment and turbine parameters</p>
                </div>
                <button 
                  onClick={() => setIsSidebarOpen(false)}
                  className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-variant text-on-surface-variant transition-colors"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
              
              <div className="flex-1 p-4 flex flex-col gap-4 bg-surface-container-lowest">
                <VariableSelectorPanel />
                <AnalysisMethodsPanel />
                <RegionPanel />
                <TurbineSpecPanel />
              </div>
            </>
          )}
        </div>

        {/* Map Area */}
        <main className={`h-full relative bg-surface flex-1 ${activeMapTool ? 'cursor-crosshair' : ''}`}>
          
          {/* Hamburger Menu Toggle (When Sidebar is Closed) */}
          {!isSidebarOpen && (
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="absolute top-4 left-4 z-50 w-12 h-12 bg-surface text-on-surface shadow-md rounded-full flex items-center justify-center hover:bg-surface-variant transition-colors"
            >
              <span className="material-symbols-outlined">menu</span>
            </button>
          )}
          
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

          {/* Job Submitted Modal */}
          {currentJobId && !hideCompletionModal && (
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-surface border border-outline-variant shadow-lg p-6 rounded-2xl max-w-sm w-full text-center">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="material-symbols-outlined text-primary text-2xl">rocket_launch</span>
              </div>
              <h2 className="font-headline-md font-bold text-on-surface mb-2">Job Submitted</h2>
              <p className="font-body-md text-on-surface-variant mb-6">
                Your simulation has been queued. You can track its progress in the Jobs tab.
              </p>
              <div className="flex gap-4 w-full">
                <button 
                  onClick={() => {
                     setHideCompletionModal(true)
                     useSimulationStore.getState().setCurrentJobId(null)
                  }}
                  className="flex-1 px-4 py-2 bg-surface-variant text-on-surface hover:bg-surface-container-high rounded-full font-bold transition-colors"
                >
                  Queue Another
                </button>
                <button 
                  onClick={() => {
                     setHideCompletionModal(true)
                     window.location.hash = '#/jobs'
                  }}
                  className="flex-1 px-4 py-2 bg-primary text-on-primary hover:bg-opacity-90 rounded-full font-bold transition-colors"
                >
                  View Jobs
                </button>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  )
}
