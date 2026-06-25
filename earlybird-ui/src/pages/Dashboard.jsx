import Badge from '../components/Badge'

const AVATAR_COLORS = ['bg-blue-100 text-blue-600', 'bg-purple-100 text-purple-600', 'bg-green-100 text-green-600']

function initialsFrom(name) {
  return name
    .split(' ')
    .filter(Boolean)
    .map(part => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

export default function Dashboard({ pipeline, loading }) {
  // If still loading, render usual loading skeleton managed by App
  // If pipeline is null (fetch succeeded but no data), show explicit empty state
  if (!loading && !pipeline) {
    return (
      <div className="space-y-4">
        <div className="bg-white rounded-xl p-8 shadow-sm border border-slate-100 text-center">
          <h2 className="text-lg font-semibold text-slate-800 mb-2">No pipeline data yet</h2>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Go to <strong>Settings</strong>, enter your Anthropic API key, then click <strong>Run Pipeline</strong> to discover internships and research contacts.
          </p>
          <p className="text-xs text-slate-400 mt-3">Pipeline takes 3-5 minutes and polls live job boards.</p>
        </div>
      </div>
    )
  }

  const jobs = pipeline?.jobs || []
  const outreach = pipeline?.outreach || []
  const summary = pipeline?.summary || null

  const freshJobs = jobs.filter(j => j.hoursAgo <= 6).slice(0, 3)
  const recentContacts = outreach.slice(0, 3)

  const sourceCounts = Object.entries(
    jobs.reduce((acc, job) => {
      acc[job.source] = (acc[job.source] || 0) + 1
      return acc
    }, {})
  ).map(([label, count]) => ({ label, count, max: Math.max(count, 1), color: 'bg-jay-blue' }))

  const cards = summary
    ? [
        { label: 'Total Jobs Found', value: summary.totalJobs, sub: 'Updated from pipeline output', color: 'text-slate-800' },
        { label: 'Fresh (< 6h)', value: summary.freshJobs, sub: 'Apply immediately', color: 'text-green-600' },
        { label: 'Outreach Drafted', value: summary.outreachCount, sub: 'Recruiter contacts ready', color: 'text-jay-blue' },
        { label: 'Cold Contacts', value: summary.coldOutreachCount, sub: 'VC & founder outreach', color: 'text-purple-600' },
      ]
    : [
        { label: 'Total Jobs Found', value: jobs.length, sub: 'From latest pipeline run', color: 'text-slate-800' },
        { label: 'Fresh (< 6h)', value: freshJobs.length, sub: 'Apply immediately', color: 'text-green-600' },
        { label: 'Outreach Drafted', value: outreach.length, sub: 'Recruiter contacts ready', color: 'text-jay-blue' },
        { label: 'Cold Contacts', value: 0, sub: 'VC & founder outreach', color: 'text-purple-600' },
      ]

  return (
    <div className="space-y-4">
      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-4">
        {cards.map(s => (
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
            {freshJobs.length > 0 ? (
              freshJobs.map((j, idx) => (
                <div key={`${j.title}-${idx}`} className="flex items-start gap-3 p-3 rounded-lg bg-green-50 border border-green-100">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-800 truncate">{j.title}</p>
                    <p className="text-xs text-slate-500">{j.company} · {j.location || 'Remote'}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <Badge color="green">{j.posted || j.age}</Badge>
                    <p className="text-xs mt-1 font-bold text-green-700">Score {j.score}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400 py-4">No jobs posted in the last 6 hours</p>
            )}
          </div>
        </div>

        {/* Outreach to-do */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-slate-700 text-sm">Outreach To-Do</h2>
            <button className="text-xs text-jay-blue hover:underline">View all</button>
          </div>
          <div className="space-y-2">
            {recentContacts.length > 0 ? (
              recentContacts.map((c, i) => (
                <div key={`${c.name}-${i}`} className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${AVATAR_COLORS[i % AVATAR_COLORS.length]}`}>
                    {c.initials || initialsFrom(c.name || c.contactName || '')}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate">{c.name || c.contactName || 'Recruiter'}</p>
                    <p className="text-xs text-slate-400 truncate">{c.role || c.contactTitle || c.title} · {c.company}</p>
                  </div>
                  <button className="text-xs bg-jay-blue text-white px-3 py-1 rounded-lg hover:bg-jay-crest transition-colors flex-shrink-0">
                    Send
                  </button>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400 py-4">No outreach contacts yet</p>
            )}
          </div>
        </div>
      </div>

      {/* Source breakdown */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
        <h2 className="font-semibold text-slate-700 text-sm mb-3">Source Breakdown</h2>
        {sourceCounts.length > 0 ? (
          <div className="space-y-2.5">
            {sourceCounts.map(s => (
              <div key={s.label} className="flex items-center gap-3">
                <span className="text-xs text-slate-500 w-40 flex-shrink-0">{s.label}</span>
                <div className="flex-1 h-1.5 rounded-full bg-slate-100">
                  <div
                    className={`h-full rounded-full ${s.color} transition-all`}
                    style={{ width: `${Math.min(100, Math.round((s.count / s.max) * 100))}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-slate-700 w-6 text-right">{s.count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400 py-4">No job sources to display</p>
        )}
      </div>
    </div>
  )
}
