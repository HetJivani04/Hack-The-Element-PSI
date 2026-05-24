import { Link, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="bg-background text-on-background h-screen overflow-hidden flex flex-col font-body-md text-body-md antialiased">
      <header className="bg-surface w-full z-50 sticky top-0 border-b border-outline-variant transition-all duration-200 ease-in-out">
        <div className="flex justify-between items-center w-full px-4 h-20 max-w-container-max mx-auto">
          <div className="flex items-center gap-gutter">
            <img alt="PSI Logo" className="h-10 w-auto rounded-DEFAULT border border-outline-variant object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCkeyijhiZp8HshOwhKvfC5mUCwYK4AYu4zldyzxDyYia_RU4kBo1RlH7h2oKXhrXYcRX9MNk9zNFV3UNtIlsZJjmbeo5IjSf8sBXHjbghYGHOBMMOMqYwpSQbryCb-gxRX4wHEHcNAscTWWKgVagalcHKuJNpThaW25301xjazUgTt9wags0Xb38_ugIbwcPa1yiEegf7Tx56gx1D1RCA-ASjHt9qT2WwPq30dLtv9k4Moc-MlUjUazg6ERw1GGHIuV30m1gBl3KjQ"/>
            <span className="font-headline-lg text-headline-lg font-bold text-primary tracking-tight">PSI</span>
          </div>
          <nav className="hidden md:flex gap-stack-lg items-center">
            <Link to="/" className="text-primary border-b-2 border-primary font-bold pb-1 font-label-md text-label-md hover:bg-surface-container-high rounded-t-lg transition-colors px-2 pt-2">Dashboard</Link>
            <Link to="/results" className="text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md hover:bg-surface-container-high rounded-lg px-2 py-2">Analytics</Link>
            <Link to="/roi" className="text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md hover:bg-surface-container-high rounded-lg px-2 py-2">Reports</Link>
          </nav>
          <div className="flex items-center gap-stack-sm">
            <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-full transition-all duration-200 ease-in-out">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-full transition-all duration-200 ease-in-out">
              <span className="material-symbols-outlined">settings</span>
            </button>
            <div className="w-10 h-10 rounded-full bg-surface-variant border border-outline-variant overflow-hidden ml-stack-sm">
              <img alt="Researcher Profile" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDAEgtdpaDxSiv3npfdVvQrVQ3ufpQZ6RUiA-6N7F3NrdX3pGa0pKTmpLiNYjyOk3IAz3WqQ3PI5H2iwU70XdopcQzoapKsJdKRfOmGD4qWLogTH1uEAuqnieKjC2Uw_HyFa8p3eEnb3gf30swdgfECILhCSuv9y9sZClM8Q9_8v8mi3B1G5kY9-BRjIQ1HFhgQeaTIgs9UcAlsOZ6fSNU3mJXnS_PH8AqFG3jHbrSfQxvetIy5VHJEeD4_7H3X50ClyDLAxCrc-ogA"/>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 relative overflow-hidden">
        <main className="w-full h-full relative bg-surface flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
