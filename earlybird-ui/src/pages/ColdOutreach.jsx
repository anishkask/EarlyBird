import { useState } from 'react'

export default function ColdOutreach({ pipeline }) {
  const [patterns, setPatterns] = useState({})

  if (!pipeline) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
        <h2 className="text-lg font-semibold text-slate-800">No cold outreach data yet</h2>
        <p className="text-sm text-slate-500 mt-2">Go to <strong>Settings</strong>, enter your Anthropic API key, then click <strong>Run Pipeline</strong>.</p>
      </div>
    )
  }

  const rows = pipeline?.coldOutreach || []
  const found = rows.filter(r => r.contactName).length

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-slate-500">
          Campus recruiters found via live web search &mdash; {found}/{rows.length} contacts found
        </p>
        <button className="bg-jay-blue text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-jay-crest transition-colors flex items-center gap-2">
          <SearchIcon className="w-4 h-4" />
          Run Cold Search
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50 text-left">
              {['Company', 'Contact Name', 'Title', 'Email', 'Domain', 'Apollo', 'Email Pattern', ''].map(h => (
                <th key={h} className="px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row.company} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-800">{row.company}</td>
                <td className="px-4 py-3">
                  {row.contactName
                    ? <span className="text-slate-700 font-medium">{row.contactName}</span>
                    : <span className="text-slate-300 italic text-xs">Not found</span>
                  }
                </td>
                <td className="px-4 py-3 text-slate-500 text-xs">{row.title || '—'}</td>
                <td className="px-4 py-3">
                  {row.email
                    ? <span className="text-jay-blue text-xs">{row.email}</span>
                    : <span className="text-slate-300 text-xs">—</span>
                  }
                </td>
                <td className="px-4 py-3 text-slate-400 text-xs">{row.companyDomain}</td>
                <td className="px-4 py-3">
                  <a
                    href={row.apolloLookup || `https://app.apollo.io/#/people?q_organization_domains[]=${row.companyDomain}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-purple-500 text-xs hover:underline whitespace-nowrap"
                  >
                    Open Apollo
                  </a>
                </td>
                <td className="px-4 py-3">
                  <input
                    className="border border-slate-200 rounded px-2 py-1 text-xs w-36 outline-none focus:border-jay-blue"
                    placeholder="first.last@..."
                    value={patterns[row.company] || ''}
                    onChange={e => setPatterns(p => ({ ...p, [row.company]: e.target.value }))}
                  />
                </td>
                <td className="px-4 py-3">
                  {row.contactName ? (
                    <button className="text-xs bg-jay-blue text-white px-3 py-1 rounded-lg hover:bg-jay-crest transition-colors whitespace-nowrap">
                      Reach Out
                    </button>
                  ) : (
                    <button disabled className="text-xs border border-slate-200 text-slate-300 px-3 py-1 rounded-lg whitespace-nowrap cursor-not-allowed">
                      No Contact
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-4 py-3 border-t border-slate-100">
          <p className="text-xs text-slate-400">
            {found} contacts found via web search · {rows.length - found} pending · Apollo links open by domain
          </p>
        </div>
      </div>
    </div>
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
