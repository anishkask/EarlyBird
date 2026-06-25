import { useState } from 'react'

export default function RunModal({ apiUrl, apiKey: propApiKey, onClose, onComplete }) {
  const [hours, setHours] = useState(72)
  const [coldOutreach, setColdOutreach] = useState(true)
  const [localApiKey, setLocalApiKey] = useState('')
  const [running, setRunning] = useState(false)
  const [statusMsg, setStatusMsg] = useState('')

  const effectiveKey = propApiKey || localApiKey

  const pollStatus = async (runId) => {
    const maxWait = 360000
    const start = Date.now()

    return new Promise((resolve) => {
      const timer = setInterval(async () => {
        try {
          const res = await fetch(`${apiUrl}/status/${runId}`)

          if (res.status === 404) {
            // Run expired or purged from the server before we read it.
            clearInterval(timer)
            setStatusMsg('Run expired before results could be retrieved. Please run again.')
            setRunning(false)
            resolve()
            return
          }

          const data = await res.json()
          const s = data.status

          if (s === 'running') setStatusMsg('Scraping job boards and researching contacts...')
          if (s === 'queued')  setStatusMsg('Queued — starting now...')

          if (s === 'complete') {
            clearInterval(timer)
            setStatusMsg('Run complete — loading results...')
            await onComplete(runId)
            resolve(data)
            setRunning(false)
            onClose()
          } else if (s === 'error') {
            clearInterval(timer)
            setStatusMsg(data.error || 'Pipeline run failed.')
            setRunning(false)
            resolve(data)
          } else if (Date.now() - start > maxWait) {
            clearInterval(timer)
            setStatusMsg('Timed out waiting for pipeline to finish.')
            setRunning(false)
            resolve()
          }
        } catch (e) {
          console.warn('Status poll failed:', e)
        }
      }, 5000)
    })
  }

  const handleRun = async () => {
    if (!effectiveKey) {
      setStatusMsg('Enter your Anthropic API key to run the pipeline.')
      return
    }
    try {
      setRunning(true)
      setStatusMsg('Starting pipeline run...')
      const res = await fetch(`${apiUrl}/run-pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          anthropic_api_key: effectiveKey,
          hours: Number(hours),
          cold_outreach: coldOutreach,
          cold_outreach_limit: 10,
        }),
      })
      if (!res.ok) {
        let detail = `Server error: ${res.status}`
        try {
          const err = await res.json()
          if (err.detail) detail = typeof err.detail === 'string' ? err.detail : 'Invalid request.'
        } catch { /* non-JSON error body */ }
        throw new Error(detail)
      }
      const { run_id } = await res.json()
      setStatusMsg(`Run started (ID: ${run_id}) — polling every 5 seconds...`)
      await pollStatus(run_id)
    } catch (e) {
      console.error('Run failed:', e)
      setStatusMsg(`Error: ${e.message}`)
      setRunning(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-xl p-6 w-96">
        <h2 className="font-bold text-slate-800 text-lg mb-1">Run Pipeline</h2>
        <p className="text-slate-400 text-sm mb-5">
          {running ? statusMsg || 'Starting...' : 'Configure and launch a scrape run'}
        </p>

        {!running && (
          <div className="space-y-4 mb-6">
            {!propApiKey && (
              <div>
                <label className="text-xs text-slate-500 font-medium block mb-1">
                  Anthropic API Key
                </label>
                <input
                  type="password"
                  placeholder="sk-ant-..."
                  value={localApiKey}
                  onChange={e => setLocalApiKey(e.target.value)}
                  autoComplete="off"
                  autoCorrect="off"
                  autoCapitalize="off"
                  spellCheck={false}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-jay-blue"
                />
                <p className="text-xs text-slate-400 mt-1">
                  Or save it in Settings to skip this step.
                </p>
              </div>
            )}
            <div>
              <label className="text-xs text-slate-500 font-medium block mb-1">Hours Window</label>
              <input
                type="number"
                value={hours}
                onChange={e => setHours(e.target.value)}
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-jay-blue"
              />
            </div>
            <Toggle label="Include Cold Outreach" value={coldOutreach} onChange={setColdOutreach} />
          </div>
        )}

        {running && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <p className="text-sm font-medium text-blue-700">Running...</p>
            </div>
            <p className="text-xs text-blue-600 leading-relaxed">{statusMsg}</p>
            <p className="text-xs text-slate-400 mt-2">Pipeline takes 3-5 minutes. This page will update automatically.</p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={onClose}
            disabled={running}
            className="flex-1 border border-slate-200 rounded-lg py-2 text-sm text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            {running ? 'Running...' : 'Cancel'}
          </button>
          <button
            onClick={handleRun}
            disabled={running}
            className="flex-1 bg-jay-blue text-white rounded-lg py-2 text-sm font-semibold hover:bg-jay-crest transition-colors disabled:opacity-50"
          >
            {running ? 'Running...' : 'Run Now'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Toggle({ label, value, onChange }) {
  return (
    <div className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2.5">
      <span className="text-sm text-slate-700">{label}</span>
      <button
        onClick={() => onChange(!value)}
        className={`w-10 h-5 rounded-full relative transition-colors ${value ? 'bg-jay-blue' : 'bg-slate-300'}`}
      >
        <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${value ? 'right-0.5' : 'left-0.5'}`} />
      </button>
    </div>
  )
}
