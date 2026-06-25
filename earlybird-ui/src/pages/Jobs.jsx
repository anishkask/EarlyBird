import { useState, useMemo } from 'react'
import Badge from '../components/Badge'

function rowColor(ageH) {
  if (ageH <= 6)  return 'bg-green-50 hover:bg-green-100'
  if (ageH <= 24) return 'bg-blue-50  hover:bg-blue-100'
  if (ageH <= 48) return 'bg-yellow-50 hover:bg-yellow-100'
  return 'bg-white hover:bg-slate-50'
}

function ageColor(ageH) {
  if (ageH <= 6)  return 'green'
  if (ageH <= 24) return 'blue'
  if (ageH <= 48) return 'yellow'
  return 'gray'
}

export default function Jobs({ pipeline, loading }) {
  const [search, setSearch] = useState('')
  const [source, setSource] = useState('All')

  if (!loading && !pipeline) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
        <h2 className="text-lg font-semibold text-slate-800">No job leads yet</h2>
        <p className="text-sm text-slate-500 mt-2">Go to <strong>Settings</strong>, enter your Anthropic API key, then click <strong>Run Pipeline</strong>.</p>
      </div>
    )
  }

  const sources = useMemo(() => {
    const distinct = Array.from(new Set(jobs.map(j => j.source).filter(Boolean)))
    return ['All', ...distinct]
  }, [jobs])

  const filtered = jobs.filter(j => {
    const q = search.toLowerCase()
    const matchSearch = j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q)
    const matchSource = source === 'All' || j.source === source
    return matchSearch && matchSource
  })

  return (
    <div>
      {/* Filters */}
      <div className="flex items-center gap-3 mb-4">
        <input
          type="text"
          placeholder="Search jobs or companies..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-jay-blue bg-white"
        />
        <select
          value={source}
          onChange={e => setSource(e.target.value)}
          className="border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none bg-white"
        >
          {sources.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 text-left bg-slate-50">
              {['#', 'Role', 'Company', 'Location', 'Source', 'Posted', 'Score', 'Status', ''].map(h => (
                <th key={h} className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((j, idx) => (
              <tr key={`${j.id}-${idx}`} className={`border-b border-slate-50 transition-colors ${rowColor(j.hoursAgo)}`}>
                <td className="px-4 py-3 text-slate-400 text-xs">{idx + 1}</td>
                <td className="px-4 py-3 font-medium text-slate-800 max-w-xs">
                  <span className="truncate block">{j.title}</span>
                </td>
                <td className="px-4 py-3 text-slate-600">{j.company}</td>
                <td className="px-4 py-3 text-slate-500 text-xs">{j.location}</td>
                <td className="px-4 py-3 text-slate-500 text-xs">{j.source}</td>
                <td className="px-4 py-3"><Badge color={ageColor(j.hoursAgo)}>{j.posted}</Badge></td>
                <td className="px-4 py-3">
                  <span className={`font-bold text-sm ${j.score >= 75 ? 'text-green-600' : j.score >= 40 ? 'text-amber-600' : 'text-slate-400'}`}>
                    {j.score}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <Badge color={j.status === 'Applied' ? 'green' : 'gray'}>{j.status || 'Not Applied'}</Badge>
                </td>
                <td className="px-4 py-3">
                  <a
                    href={j.jobUrl || '#'}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-jay-blue hover:underline whitespace-nowrap"
                  >
                    Apply
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Showing {filtered.length} of {jobs.length} jobs
          </p>
          <div className="flex gap-2">
            <button className="px-3 py-1 rounded border border-slate-200 text-xs text-slate-500 hover:bg-slate-50">Prev</button>
            <button className="px-3 py-1 rounded border border-slate-200 text-xs text-slate-500 hover:bg-slate-50">Next</button>
          </div>
        </div>
      </div>
    </div>
  )
}
