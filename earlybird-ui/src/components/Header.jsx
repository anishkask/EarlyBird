export default function Header({ title, sub }) {
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between flex-shrink-0">
      <div>
        <h1 className="text-slate-800 font-bold text-lg leading-tight">{title}</h1>
        <p className="text-slate-400 text-xs mt-0.5">{sub}</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-green-700 text-xs font-medium">Web Search Active</span>
        </div>
        <div className="flex items-center gap-2 text-slate-500 text-xs bg-slate-100 rounded-lg px-3 py-1.5">
          <KeyIcon className="w-3.5 h-3.5" />
          API Key Set
        </div>
      </div>
    </header>
  )
}

function KeyIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="5.5" cy="8" r="3.5" />
      <path d="M8.5 8h6M12 8v2" strokeLinecap="round" />
    </svg>
  )
}
