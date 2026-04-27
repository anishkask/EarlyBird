import { useState } from 'react'

const COLD = [
  { company: 'Airbnb',        contact: 'Caitlin Wright', title: 'Recruiter',          email: 'c.wright@airbnb.com',   domain: 'airbnb.com',   found: true },
  { company: 'Notion',        contact: 'Shivani Patel',  title: 'Campus Recruiter',   email: 's.patel@notion.so',     domain: 'notion.so',    found: true },
  { company: 'Brex',          contact: '',               title: '',                   email: '',                      domain: 'brex.com',     found: false },
  { company: 'Vercel',        contact: 'Maya Kim',       title: 'Univ. Recruiting',   email: 'm.kim@vercel.com',      domain: 'vercel.com',   found: true },
  { company: 'Coinbase',      contact: '',               title: '',                   email: '',                      domain: 'coinbase.com', found: false },
  { company: 'Linear',        contact: 'James Park',     title: 'Recruiting Lead',    email: '',                      domain: 'linear.app',   found: true },
  { company: 'Retool',        contact: '',               title: '',                   email: '',                      domain: 'retool.com',   found: false },
  { company: 'Eulerity',      contact: 'Sara Chen',      title: 'Campus Recruiter',   email: 's.chen@eulerity.com',   domain: 'eulerity.com', found: true },
  { company: 'Monarch Money', contact: '',               title: '',                   email: '',                      domain: 'monarchmoney.com', found: false },
  { company: 'Glydways',      contact: 'Tom Nguyen',     title: 'HR Generalist',      email: '',                      domain: 'glydways.com', found: true },
]

export default function ColdOutreach() {
  const [patterns, setPatterns] = useState({})
  const found = COLD.filter(c => c.found).length

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-slate-500">
          Campus recruiters found via live web search &mdash; {found}/{COLD.length} contacts found
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
            {COLD.map(row => (
              <tr key={row.company} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-800">{row.company}</td>
                <td className="px-4 py-3">
                  {row.contact
                    ? <span className="text-slate-700 font-medium">{row.contact}</span>
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
                <td className="px-4 py-3 text-slate-400 text-xs">{row.domain}</td>
                <td className="px-4 py-3">
                  <a
                    href={`https://app.apollo.io/#/people?q_organization_domains[]=${row.domain}`}
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
                  {row.found ? (
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
            {found} contacts found via web search · {COLD.length - found} pending · Apollo links open by domain
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
