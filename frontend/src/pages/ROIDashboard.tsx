
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
);

export default function ROIDashboard() {
  const colorPrimary = '#426446';
  const colorOutline = '#727971';

  const lineData = {
    labels: ['2025', '2027', '2029', '2031', '2033', '2035', '2037', '2039', '2041', '2043'],
    datasets: [
      {
        label: 'Floating Platform',
        data: [1.2, 1.5, 2.1, 2.8, 3.2, 3.4, 3.5, 3.4, 3.2, 3.0],
        borderColor: colorPrimary,
        backgroundColor: 'rgba(66, 100, 70, 0.2)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6
      },
      {
        label: 'Grounded Monopile',
        data: [1.5, 1.8, 2.0, 2.2, 2.3, 2.3, 2.2, 2.0, 1.8, 1.5],
        borderColor: colorOutline,
        backgroundColor: 'rgba(114, 121, 113, 0.15)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6
      }
    ]
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        align: 'end' as const,
        labels: {
          usePointStyle: true,
          boxWidth: 8,
          font: { family: "'Public Sans', sans-serif", size: 12 }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(27, 28, 28, 0.9)',
        titleFont: { family: "'Public Sans', sans-serif", size: 14 },
        bodyFont: { family: "'Public Sans', sans-serif", size: 13 },
        padding: 12,
        cornerRadius: 4
      }
    },
    scales: {
      x: {
        grid: { display: false, drawBorder: false },
        ticks: { font: { family: "'Public Sans', sans-serif", size: 12 }, color: '#727971' }
      },
      y: {
        grid: { color: '#f2f0f0', drawBorder: false },
        ticks: { font: { family: "'Public Sans', sans-serif", size: 12 }, color: '#727971', stepSize: 1 }
      }
    },
    interaction: { mode: 'index' as const, intersect: false }
  };

  const donutData = {
    labels: ['Turbines', 'Foundations', 'Grid Connection', 'Installation'],
    datasets: [{
      data: [40, 25, 20, 15],
      backgroundColor: [
        colorPrimary,
        '#c6e9e9',
        '#456648',
        '#dbd9d9'
      ],
      borderWidth: 0,
      hoverOffset: 4
    }]
  };

  const donutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '75%',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(27, 28, 28, 0.9)',
        callbacks: {
          label: function(context: any) {
            return ' ' + context.label + ': ' + context.parsed + '%';
          }
        }
      }
    }
  };

  return (
    <div className="max-w-container-max mx-auto px-margin-desktop py-stack-lg flex flex-col gap-section-gap pb-20">
      {/* Header Section */}
      <section className="flex flex-col gap-stack-sm">
        <h1 className="font-display-lg text-display-lg text-primary">Stakeholder ROI Dashboard</h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant max-w-3xl">Financial performance and production metrics analysis for ongoing and proposed offshore wind initiatives.</p>
      </section>

      {/* KPI Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
        {/* KPI 1 */}
        <div className="bg-surface/90 backdrop-blur-md border border-outline-variant p-stack-md rounded-xl flex flex-col gap-stack-sm hover:shadow-sm transition-shadow duration-300 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary-container opacity-10 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
          <div className="flex justify-between items-start">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Annual Energy Yield</span>
            <span className="material-symbols-outlined text-primary">bolt</span>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="font-headline-lg text-headline-lg text-on-surface">3.2</span>
            <span className="font-label-md text-label-md text-on-surface-variant">GWh</span>
          </div>
          <div className="flex items-center gap-1 mt-auto">
            <span className="material-symbols-outlined text-primary text-sm">trending_up</span>
            <span className="font-label-sm text-label-sm text-primary">+4.2% vs baseline</span>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="bg-surface/90 backdrop-blur-md border border-outline-variant p-stack-md rounded-xl flex flex-col gap-stack-sm hover:shadow-sm transition-shadow duration-300 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-secondary-container opacity-10 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
          <div className="flex justify-between items-start">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Project ROI</span>
            <span className="material-symbols-outlined text-secondary">show_chart</span>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="font-headline-lg text-headline-lg text-on-surface">14.8</span>
            <span className="font-label-md text-label-md text-on-surface-variant">%</span>
          </div>
          <div className="flex items-center gap-1 mt-auto">
            <span className="material-symbols-outlined text-primary text-sm">trending_up</span>
            <span className="font-label-sm text-label-sm text-primary">Target exceeded</span>
          </div>
        </div>

        {/* KPI 3 */}
        <div className="bg-surface/90 backdrop-blur-md border border-outline-variant p-stack-md rounded-xl flex flex-col gap-stack-sm hover:shadow-sm transition-shadow duration-300 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-tertiary-container opacity-10 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
          <div className="flex justify-between items-start">
            <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">Break-even Year</span>
            <span className="material-symbols-outlined text-tertiary">calendar_month</span>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="font-headline-lg text-headline-lg text-on-surface">2032</span>
          </div>
          <div className="flex items-center gap-1 mt-auto">
            <span className="material-symbols-outlined text-on-surface-variant text-sm">info</span>
            <span className="font-label-sm text-label-sm text-on-surface-variant">Estimated based on current CAPEX</span>
          </div>
        </div>
      </section>

      {/* Bento Layout: Charts & Imagery */}
      <section className="grid grid-cols-12 gap-gutter">
        {/* Main Chart Area */}
        <div className="col-span-12 md:col-span-8 bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-lg flex flex-col gap-stack-md">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface">Energy Production Forecast</h2>
              <p className="font-body-md text-body-md text-on-surface-variant">20-year projection: Floating vs Grounded Models</p>
            </div>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-surface-container-low text-on-surface-variant font-label-sm text-label-sm rounded-full border border-outline-variant">GWh</span>
              <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors">download</button>
            </div>
          </div>
          <div className="relative h-80 w-full">
            <Line data={lineData} options={lineOptions} />
          </div>
        </div>

        {/* Right Column: CAPEX & Image */}
        <div className="col-span-12 md:col-span-4 flex flex-col gap-gutter">
          {/* CAPEX Donut Chart */}
          <div className="bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl p-stack-lg flex flex-col gap-stack-md flex-grow">
            <div>
              <h3 className="font-headline-md text-headline-md text-on-surface text-center">CAPEX Breakdown</h3>
              <p className="font-body-md text-body-md text-on-surface-variant text-center">Initial Capital Expenditure</p>
            </div>
            <div className="relative h-48 w-full flex justify-center items-center">
              <Doughnut data={donutData} options={donutOptions} />
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="font-headline-md text-headline-md text-on-surface mt-4">$1.2B</span>
                <span className="font-label-sm text-label-sm text-on-surface-variant">Total</span>
              </div>
            </div>
            <div className="mt-auto grid grid-cols-2 gap-2 text-sm">
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-primary"></div><span className="font-label-sm text-on-surface">Turbines</span></div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-secondary-container"></div><span className="font-label-sm text-on-surface">Foundations</span></div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-surface-tint"></div><span className="font-label-sm text-on-surface">Grid Connect</span></div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-surface-dim"></div><span className="font-label-sm text-on-surface">Installation</span></div>
            </div>
          </div>

          {/* Turbine Reference Image */}
          <div className="bg-surface/90 backdrop-blur-md border border-outline-variant rounded-xl overflow-hidden h-48 relative group">
            <img alt="Turbine Visualization" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" src="https://lh3.googleusercontent.com/aida/ADBb0ujB6nsIyVk2koRqq3H081b_V582eYamBVLQn5SV3DiVEMSDLzDk-jbQRJJ3qdi7GodOu2zgdn2c24itEcbL-oeyYd4ubijOYIj3SKym5-PM0KHLWCoC-Y2c3eFdruOD22mEZUvpHUYOOrx494VnnUa04QG1eTbSPKGYuQGKKAB9oyxV4lkcW_B9OF7ey4k6j1ViWGqwjjRVmKn6URtirehrXVtlkbQJso9QfmihkB5z5xMg2PeRQnv3eHc"/>
            <div className="absolute inset-0 bg-gradient-to-t from-on-background/80 to-transparent flex items-end p-stack-md">
              <p className="font-label-md text-label-md text-on-primary">Platform Model Alpha - Deployed</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
