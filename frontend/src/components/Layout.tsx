import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { useJobHistory } from '../api/client';

export default function Layout() {
  const navigate = useNavigate();
  const { data: jobHistory } = useJobHistory();
  const prevHistoryRef = useRef<any>(null);
  
  const [toasts, setToasts] = useState<any[]>([]);

  useEffect(() => {
    if (!jobHistory) return;
    const currentJobs = Array.isArray(jobHistory) ? jobHistory : [];
    const prevJobs = prevHistoryRef.current ? (Array.isArray(prevHistoryRef.current) ? prevHistoryRef.current : []) : [];
    
    const newCompleted = currentJobs.filter((job: any) => 
      job.status === 'completed' && 
      prevJobs.some((p: any) => p.job_id === job.job_id && (p.status === 'running' || p.status === 'queued'))
    );

    if (newCompleted.length > 0) {
      newCompleted.forEach((job: any) => {
        const id = Date.now() + Math.random();
        setToasts(prev => [...prev, { id, title: `Simulation Complete`, message: `${job.description} finished.` }]);
        setTimeout(() => {
          setToasts(prev => prev.filter(t => t.id !== id));
        }, 10000); // Hide after 10s
      });
    }

    prevHistoryRef.current = currentJobs;
  }, [jobHistory]);
  const navClass = ({ isActive }: { isActive: boolean }) => 
    isActive 
      ? "text-primary border-b-[6px] border-primary font-extrabold pb-[0px] text-xl hover:bg-surface-container-high rounded-t-lg transition-all px-4 pt-2"
      : "text-on-surface-variant hover:text-primary transition-all text-xl font-medium hover:bg-surface-container-high rounded-t-lg px-4 pt-2 pb-[6px] border-b-[6px] border-transparent";

  return (
    <div className="bg-background text-on-background h-screen overflow-hidden flex flex-col font-body-md text-body-md antialiased">
      <header className="bg-surface w-full z-50 sticky top-0 border-b border-outline-variant transition-all duration-200 ease-in-out">
        <div className="flex justify-between items-center w-full px-[2%] h-20">
          <div className="flex items-center gap-gutter">
            <img alt="PSI Logo" className="h-10 w-auto object-contain" src="/logo.png"/>
            <span className="font-headline-lg text-headline-lg font-bold text-primary tracking-tight">Psi</span>
          </div>
          <nav className="hidden md:flex gap-stack-lg items-center relative">
            <NavLink to="/" className={navClass}>Dashboard</NavLink>
            <NavLink to="/jobs" className={navClass}>Jobs</NavLink>
            <NavLink to="/results" className={navClass}>Analytics</NavLink>
            <NavLink to="/roi" className={navClass}>Reports</NavLink>
          </nav>
          <div className="flex items-center gap-0">
            <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-full transition-all duration-200 ease-in-out">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-full transition-all duration-200 ease-in-out">
              <span className="material-symbols-outlined">settings</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 relative overflow-hidden">
        <main className="w-full h-full relative bg-surface flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      
      {/* Global Toasts */}
      <div className="fixed bottom-6 right-6 z-[999] flex flex-col gap-4 pointer-events-none">
        {toasts.map(toast => (
          <div key={toast.id} className="bg-surface border border-outline-variant shadow-xl rounded-xl p-4 w-80 flex gap-4 pointer-events-auto transition-all animate-in slide-in-from-bottom-5">
             <button onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))} className="absolute top-2 right-2 text-on-surface-variant hover:text-on-surface">
               <span className="material-symbols-outlined text-sm">close</span>
             </button>
             <div className="text-green-500 mt-1">
               <span className="material-symbols-outlined">check_circle</span>
             </div>
             <div>
               <h3 className="font-bold text-on-surface font-headline-sm">{toast.title}</h3>
               <p className="text-body-sm text-on-surface-variant mb-2">{toast.message}</p>
               <button 
                 onClick={() => {
                   setToasts(prev => prev.filter(t => t.id !== toast.id));
                   navigate('/results');
                 }}
                 className="text-primary font-bold text-label-sm hover:underline"
               >
                 View Results
               </button>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
}
