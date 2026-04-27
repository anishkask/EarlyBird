import { useState } from 'react'
import Badge from '../components/Badge'

const ALL_JOBS = [
  { id: 1, title: 'ML Engineering Intern 2026',     company: 'Brex',     location: 'Remote',         source: 'Greenhouse', age: '2h ago',  ageH: 2,  score: 100, status: 'Not Applied' },
  { id: 2, title: 'Software Engineering Intern',    company: 'Airbnb',   location: 'Remote',         source: 'Greenhouse', age: '4h ago',  ageH: 4,  score: 85,  status: 'Applied' },
  { id: 3, title: 'Backend Engineer Intern',        company: 'Notion',   location: 'United States',  source: 'Greenhouse', age: '18h ago', ageH: 18, score: 75,  status: 'Not Applied' },
  { id: 4, title: 'Data Engineering Intern',        company: 'Coinbase', location: 'Remote',         source: 'Lever',      age: '22h ago', ageH: 22, score: 100, status: 'Not Applied' },
  { id: 5, title: 'Fullstack Intern 2026',          company: 'Vercel',   location: 'Remote',         source: 'Lever',      age: '36h ago', ageH: 36, score: 45,  status: 'Not Applied' },
  { id: 6, title: 'AI/LLM Research Intern',         company: 'Linear',   location: 'Remote',         source: 'Lever',      age: '48h ago', ageH: 48, score: 100, status: 'Not Applied' },
  { id: 7, title: 'Software Engineering Co-op',     company: 'Retool',   location: 'Philadelphia PA', source: 'Greenhouse', age: '55h ago', ageH: 55, score: 60,  status: 'Not Applied' },
]

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

export default function Jobs() {
  const [search, setSearch] = useState('')
  const [source, setSource] = useState('All')

  const filtered = ALL_JOBS.filter(j => {
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
          {['All', 'Greenhouse', 'Lever', 'LinkedIn', 'Indeed'].map(s => (
            <option key={s}>{s}</option>
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
              <tr key={j.id} className={`border-b border-slate-50 transition-colors ${rowColor(j.ageH)}`}>
                <td className="px-4 py-3 text-slate-400 text-xs">{idx + 1}</td>
                <td className="px-4 py-3 font-medium text-slate-800 max-w-xs">
                  <span className="truncate block">{j.title}</span>
                </td>
                <td className="px-4 py-3 text-slate-600">{j.company}</td>
                <td className="px-4 py-3 text-slate-500 text-xs">{j.location}</td>
                <td className="px-4 py-3 text-slate-500 text-xs">{j.source}</td>
                <td className="px-4 py-3"><Badge color={ageColor(j.ageH)}>{j.age}</Badge></td>
                <td className="px-4 py-3">
                  <span className={`font-bold text-sm ${j.score >= 75 ? 'text-green-600' : j.score >= 40 ? 'text-amber-600' : 'text-slate-400'}`}>
                    {j.score}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <Badge color={j.status === 'Applied' ? 'green' : 'gray'}>{j.status}</Badge>
                </td>
                <td className="px-4 py-3">
                  <a href="#" className="text-xs text-jay-blue hover:underline whitespace-nowrap">Apply</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Showing {filtered.length} of {ALL_JOBS.length} jobs
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
