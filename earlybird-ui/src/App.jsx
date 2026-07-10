import { useState, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Outreach from './pages/Outreach'
import ColdOutreach from './pages/ColdOutreach'
import Settings from './pages/Settings'
import RunModal from './components/RunModal'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const PAGES = {
  dashboard: { label: 'Dashboard',      sub: 'Live pipeline summary and job health' },
  jobs:      { label: 'Job Leads',      sub: 'Internship opportunities discovered by the pipeline' },
  outreach:  { label: 'Outreach',       sub: 'Recruiter and hiring contact drafts' },
  cold:      { label: 'Cold Outreach',  sub: 'Founder/CEO cold outreach research' },
  settings:  { label: 'Settings',       sub: 'Configure your pipeline and API keys' },
}

function normalizeJobs(jobs) {
  return (jobs || []).map((j, i) => ({
    id: i + 1,
    title:    j.title    || '',
    company:  j.company  || '',
    location: j.location || '',
    source:   j.source   || '',
    hoursAgo: j.hours_ago ?? 999,
    posted:   j.hours_ago < 999 ? `${j.hours_ago}h ago` : 'Unknown',
    jobUrl:   j.job_url  || '#',
    score:    j.score    || 0,
    status:   'Not Applied',
    description: j.description || '',
  }))
}

function normalizeOutreach(outreach) {
  return (outreach || []).map(c => {
    const domain = (c.email || '').split('@')[1] || ''
    return {
      name:          c.name        || '',
      title:         c.title       || '',
      company:       c.company     || '',
      role:          c.role        || '',
      email:         c.email       || '',
      linkedinUrl:   c.linkedin_url || '#',
      linkedinMsg:   c.linkedin_msg || '',
      emailSubject:  c.email_subj  || '',
      emailBody:     c.email_body  || '',
      emailSent:     c.email_sent  || '',
      apolloLookup:  domain
        ? `https://app.apollo.io/#/people?q_organization_domains[]=${domain}`
        : '#',
    }
  })
}

function normalizeColdOutreach(coldOutreach) {
  return (coldOutreach || []).map(c => {
    const domain = c.domain
      || (c.website_url ? (() => { try { return new URL(c.website_url).hostname.replace('www.', '') } catch { return '' } })() : '')
    return {
      company:      c.company_name || '',
      contactName:  `${c.first_name || ''} ${c.last_name || ''}`.trim(),
      title:        c.title        || '',
      email:        c.email        || '',
      companyDomain: domain,
      apolloLookup: domain
        ? `https://app.apollo.io/#/people?q_organization_domains[]=${domain}`
        : '#',
      linkedinUrl:  c.linkedin_url || '#',
      site:         c.vc_source    || '',
      found:        !!(c.first_name || c.last_name),
    }
  })
}

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [runOpen, setRunOpen] = useState(false)
  const [pipeline, setPipeline] = useState(null)
  const [runError, setRunError] = useState(null)

  const [settings, setSettings] = useState({
    anthropicApiKey: '',
    targetLocations: [],
    roleKeywords: [],
    skills: [],
    school: '',
  })

  const handleRunComplete = useCallback(async (runId) => {
    try {
      const res = await fetch(`${API_URL}/results/${runId}`)
      const data = await res.json()
      if (!res.ok || data.error || data.detail) {
        setRunError(data.error || data.detail || `Could not load results (${res.status}).`)
        return
      }
      setRunError(null)
      setPipeline({
        jobs:         normalizeJobs(data.jobs),
        outreach:     normalizeOutreach(data.outreach),
        coldOutreach: normalizeColdOutreach(data.cold_outreach),
        summary: {
          totalJobs:          data.summary?.total_jobs          ?? 0,
          freshJobs:          data.summary?.fresh_jobs          ?? 0,
          outreachCount:      data.summary?.outreach_count      ?? 0,
          coldOutreachCount:  data.summary?.cold_outreach_count ?? 0,
        },
        timestamp: data.timestamp,
      })
    } catch (e) {
      setRunError(e.message)
    }
  }, [])

  return (
    <div className="flex h-screen overflow-hidden w-full relative">
      <Sidebar page={page} setPage={setPage} onRun={() => setRunOpen(true)} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={PAGES[page].label} sub={PAGES[page].sub} />
        <main className="flex-1 overflow-y-auto scrollbar-thin p-6 bg-slate-50">
          {runError && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
              Pipeline error: {runError}
            </div>
          )}
          {page === 'dashboard' && <Dashboard pipeline={pipeline} loading={false} error={null} />}
          {page === 'jobs'      && <Jobs      pipeline={pipeline} loading={false} error={null} />}
          {page === 'outreach'  && <Outreach  pipeline={pipeline} loading={false} error={null} />}
          {page === 'cold'      && <ColdOutreach pipeline={pipeline} loading={false} error={null} />}
          {page === 'settings'  && (
            <Settings
              settings={settings}
              onSave={setSettings}
              onRun={() => setRunOpen(true)}
            />
          )}
        </main>
      </div>
      {runOpen && (
        <RunModal
          apiUrl={API_URL}
          apiKey={settings.anthropicApiKey}
          settings={settings}
          onClose={() => setRunOpen(false)}
          onComplete={handleRunComplete}
        />
      )}
    </div>
  )
}
