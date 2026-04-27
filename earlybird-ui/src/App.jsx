import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Outreach from './pages/Outreach'
import ColdOutreach from './pages/ColdOutreach'
import Settings from './pages/Settings'
import RunModal from './components/RunModal'

const PAGES = {
  dashboard: { label: 'Dashboard', sub: 'Sunday, April 27 2026 — 72h window' },
  jobs:      { label: 'Job Leads',      sub: '47 internships found · 3 fresh' },
  outreach:  { label: 'Outreach',       sub: '18 contacts drafted · 4 emails sent' },
  cold:      { label: 'Cold Outreach',  sub: '10 companies researched via web search' },
  settings:  { label: 'Settings',       sub: 'Configure your pipeline' },
}

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [runOpen, setRunOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden w-full">
      <Sidebar page={page} setPage={setPage} onRun={() => setRunOpen(true)} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={PAGES[page].label} sub={PAGES[page].sub} />
        <main className="flex-1 overflow-y-auto scrollbar-thin p-6 bg-slate-50">
          {page === 'dashboard' && <Dashboard />}
          {page === 'jobs'      && <Jobs />}
          {page === 'outreach'  && <Outreach />}
          {page === 'cold'      && <ColdOutreach />}
          {page === 'settings'  && <Settings />}
        </main>
      </div>
      {runOpen && <RunModal onClose={() => setRunOpen(false)} />}
    </div>
  )
}
