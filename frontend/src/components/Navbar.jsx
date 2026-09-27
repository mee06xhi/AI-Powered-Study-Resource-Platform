function Navbar({ onAskAgent, onOpenPlanner  }) {
  return (
    <header className="glass-panel sticky top-0 z-50 w-full border-b border-white/5">
      <div className="max-w-[1440px] mx-auto flex items-center justify-between h-20 px-6 md:px-16">
        <span className="font-display text-2xl font-bold text-primary tracking-tight">
          VTU SmartPrep
        </span>

        <nav className="hidden md:flex items-center gap-8">
          <a
            href="#"
            className="text-primary font-semibold text-xs uppercase tracking-wider border-b-2 border-primary pb-1"
          >
            Explore Resources
          </a>
          <button
            onClick={onOpenPlanner}
            className="text-on-surface-variant text-xs uppercase tracking-wider hover:text-primary transition-colors"
            >
              Study Planner
          </button>
          <button
            onClick={onAskAgent}
            className="text-on-surface-variant text-xs uppercase tracking-wider hover:text-primary transition-colors"
          >
            Ask Agent
          </button>
        </nav>

        <div className="flex items-center gap-4 text-on-surface-variant">
          <button className="hover:text-primary transition-colors" title="Notifications">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.4-1.4A2 2 0 0118 14.2V11a6 6 0 10-12 0v3.2a2 2 0 01-.6 1.4L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>
          <button className="hover:text-primary transition-colors" title="Saved">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 4h12a1 1 0 011 1v15l-7-4-7 4V5a1 1 0 011-1z" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  )
}
export default Navbar