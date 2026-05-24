# Offshore Wind Simulation Platform - Frontend

This directory contains the React-based frontend for the Offshore Wind Simulation Platform, built with Vite, TypeScript, and Tailwind CSS.

## Work Completed (Phases 1 & 2)

We have successfully built an interactive 3D environment for planning and simulating offshore wind farms.

1. **Core Setup**
   - Initialized the project with React, Vite, and TypeScript.
   - Configured Tailwind CSS for utility-first styling alongside standard design tokens.
   - Set up `react-router-dom` for navigating between different views (e.g., the primary Dashboard and ROI Dashboard).

2. **State Management & Data Fetching**
   - Built a global state store using **Zustand** (`simulationStore.ts`) to keep the floating UI panels and the 3D globe perfectly in sync.
   - Integrated **React Query** (`@tanstack/react-query`) in `api/client.ts` to manage fetching, caching, and polling data from the Python FastAPI backend.

3. **3D Globe Integration**
   - Integrated **CesiumJS** via the `resium` React wrapper (`SimulationDashboard.tsx`).
   - Configured the camera to default to the Scotian Shelf region.
   - Implemented map click interactions to drop a turbine pin (fetching coordinates).

4. **Interactive Floating Panels**
   Built four major configuration panels that float over the 3D map:
   - **VariableSelectorPanel**: Fetches and groups relevant environmental variables (Physics, Waves, Atmosphere).
   - **AnalysisMethodsPanel**: Dynamically renders configuration sliders and inputs based on the selected tool's JSON schema returned from the backend.
   - **TurbineSpecPanel**: Allows tweaking of physical parameters like Hub Height, Rotor Diameter, and Material Grade.
   - **TimeRangePanel**: Uses the temporal bounds from the backend to set the simulation timeframe and trigger the API job submission.

5. **End-to-End Simulation Flow**
   - Clicking "Run Simulation" fires a POST request to the backend.
   - Displays a dynamic loading overlay.
   - Polls the backend for progress until the simulation returns `completed`.

## Running Locally

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start the Development Server**
   ```bash
   npm run dev
   ```

   The UI will be available at `http://localhost:5173` (or `5174` if port is in use). Ensure the backend server is running on `127.0.0.1:8000` so that the React Query hooks can successfully fetch the mock API data.
