import BluejayLogo from './BluejayLogo'

const NAV = [
  { id: 'dashboard', label: 'Dashboard',     icon: DashIcon },
  { id: 'jobs',      label: 'Job Leads',     icon: BriefcaseIcon, badge: 12 },
  { id: 'outreach',  label: 'Outreach',      icon: MailIcon },
  { id: 'cold',      label: 'Cold Outreach', icon: SearchIcon },
  { id: 'settings',  label: 'Settings',      icon: GearIcon },
]

export default function Sidebar({ page, setPage, onRun }) {
  return (
    <aside className="w-56 flex-shrink-0 flex flex-col bg-navy">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <BluejayLogo size={34} />
          <div>
            <p className="text-white font-bold text-base tracking-tight leading-none">EarlyBird</p>
            <p className="text-jay-sky text-xs mt-0.5">Apply before the crowd</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto scrollbar-thin">
        {NAV.map(({ id, label, icon: Icon, badge }) => {
          const active = page === id
          return (
            <button
              key={id}
              onClick={() => setPage(id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors text-left ${
                active
                  ? 'bg-jay-blue text-white font-semibold'
                  : 'text-slate-400 hover:bg-navy-light hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{label}</span>
              {badge && (
                <span className="ml-auto bg-jay-blue/80 text-white text-xs rounded-full px-1.5 py-0.5 leading-none">
                  {badge}
                </span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Run button */}
      <div className="px-4 py-4 border-t border-white/10">
        <button
          onClick={onRun}
          className="w-full py-2 rounded-lg text-sm font-semibold bg-jay-blue text-white hover:bg-jay-crest transition-colors flex items-center justify-center gap-2"
        >
          <TriangleIcon className="w-3 h-3" />
          Run Pipeline
        </button>
        <p className="text-slate-500 text-xs text-center mt-2">Last run: 2h ago</p>
      </div>
    </aside>
  )
}

/* ── inline SVG icon components ── */
function DashIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="1" y="1" width="6" height="6" rx="1" />
      <rect x="9" y="1" width="6" height="6" rx="1" />
      <rect x="1" y="9" width="6" height="6" rx="1" />
      <rect x="9" y="9" width="6" height="6" rx="1" />
    </svg>
  )
}
function BriefcaseIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="1" y="5" width="14" height="9" rx="1.5" />
      <path d="M5 5V3.5A1.5 1.5 0 0 1 6.5 2h3A1.5 1.5 0 0 1 11 3.5V5" />
      <path d="M1 9h14" />
    </svg>
  )
}
function MailIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="1" y="3" width="14" height="10" rx="1.5" />
      <path d="M1 4l7 5 7-5" />
    </svg>
  )
}
function SearchIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="6.5" cy="6.5" r="4" />
      <path d="M10 10l3.5 3.5" strokeLinecap="round" />
    </svg>
  )
}
function GearIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="8" cy="8" r="2.5" />
      <path d="M8 1v2M8 13v2M1 8h2M13 8h2M2.93 2.93l1.41 1.41M11.66 11.66l1.41 1.41M2.93 13.07l1.41-1.41M11.66 4.34l1.41-1.41" strokeLinecap="round" />
    </svg>
  )
}
function TriangleIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 12 12" fill="currentColor">
      <path d="M2 1l9 5-9 5V1z" />
    </svg>
  )
}
