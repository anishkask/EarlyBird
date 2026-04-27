import Badge from '../components/Badge'

const FRESH_JOBS = [
  { title: 'ML Engineering Intern 2026',  company: 'Brex',   age: '2h ago', score: 100 },
  { title: 'Software Engineering Intern', company: 'Airbnb', age: '4h ago', score: 85 },
  { title: 'Backend Engineer Intern',     company: 'Notion', age: '5h ago', score: 75 },
]

const CONTACTS = [
  { initials: 'CW', name: 'Caitlin Wright', role: 'Recruiter',          company: 'Airbnb' },
  { initials: 'SP', name: 'Shivani Patel',  role: 'Campus Recruiter',   company: 'Notion' },
  { initials: 'MK', name: 'Maya Kim',        role: 'Univ. Recruiting',  company: 'Vercel' },
]

const SOURCES = [
  { label: 'Greenhouse ATS', count: 28, max: 47, color: 'bg-jay-blue' },
  { label: 'LinkedIn / Indeed', count: 14, max: 47, color: 'bg-purple-400' },
  { label: 'Lever ATS',      count: 5,  max: 47, color: 'bg-emerald-400' },
  { label: 'Wellfound',      count: 0,  max: 47, color: 'bg-amber-400' },
]

const AVATAR_COLORS = ['bg-blue-100 text-blue-600', 'bg-purple-100 text-purple-600', 'bg-green-100 text-green-600']

export default function Dashboard() {
  return (
    <div className="space-y-4">
      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total Jobs Found', value: 47,  sub: '↑ 12 from yesterday',   color: 'text-slate-800' },
          { label: 'Fresh (< 6h)',     value: 3,   sub: 'Apply immediately',      color: 'text-green-600' },
          { label: 'Outreach Drafted', value: 18,  sub: '4 emails sent',          color: 'text-jay-blue' },
          { label: 'Cold Contacts',    value: 10,  sub: 'via web search',         color: 'text-purple-600' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl p-5 shadow-sm border border-slate-100">
            <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-slate-400 mt-1">{s.sub}</p>
          </div>
        ))}
      </div>

      {/* Two-column row */}
      <div className="grid grid-cols-2 gap-4">
        {/* Fresh jobs */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-slate-700 text-sm">Apply Right Now</h2>
            <span className="text-xs text-slate-400">Posted &lt; 6h ago</span>
          </div>
          <div className="space-y-2">
            {FRESH_JOBS.map(j => (
              <div key={j.title} className="flex items-start gap-3 p-3 rounded-lg bg-green-50 border border-green-100">
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm text-slate-800 truncate">{j.title}</p>
                  <p className="text-xs text-slate-500">{j.company} · Remote</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <Badge color="green">{j.age}</Badge>
                  <p className="text-xs mt-1 font-bold text-green-700">Score {j.score}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Outreach to-do */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-slate-700 text-sm">Outreach To-Do</h2>
            <button className="text-xs text-jay-blue hover:underline">View all</button>
          </div>
          <div className="space-y-2">
            {CONTACTS.map((c, i) => (
              <div key={c.name} className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${AVATAR_COLORS[i]}`}>
                  {c.initials}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{c.name}</p>
                  <p className="text-xs text-slate-400 truncate">{c.role} · {c.company}</p>
                </div>
                <button className="text-xs bg-jay-blue text-white px-3 py-1 rounded-lg hover:bg-jay-crest transition-colors flex-shrink-0">
                  Send
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Source breakdown */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
        <h2 className="font-semibold text-slate-700 text-sm mb-3">Source Breakdown</h2>
        <div className="space-y-2.5">
          {SOURCES.map(s => (
            <div key={s.label} className="flex items-center gap-3">
              <span className="text-xs text-slate-500 w-40 flex-shrink-0">{s.label}</span>
              <div className="flex-1 h-1.5 rounded-full bg-slate-100">
                <div
                  className={`h-full rounded-full ${s.color} transition-all`}
                  style={{ width: `${(s.count / s.max) * 100}%` }}
                />
              </div>
              <span className="text-xs font-medium text-slate-700 w-6 text-right">{s.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
