
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import SimulationDashboard from './pages/SimulationDashboard'
import ImpactAnalysis from './pages/ImpactAnalysis'
import ROIDashboard from './pages/ROIDashboard'
import JobManagementDashboard from './pages/JobManagementDashboard'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<SimulationDashboard />} />
          <Route path="results" element={<ImpactAnalysis />} />
          <Route path="roi" element={<ROIDashboard />} />
          <Route path="jobs" element={<JobManagementDashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
