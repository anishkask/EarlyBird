import { useState } from 'react'

function Field({ label, hint, ...props }) {
  return (
    <div>
      <label className="text-xs text-slate-500 font-medium block mb-1">{label}</label>
      <input
        className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-jay-blue bg-white"
        {...props}
      />
      {hint && <p className="text-xs text-slate-400 mt-1">{hint}</p>}
    </div>
  )
}

function Toggle({ label, value, onChange }) {
  return (
    <div className="flex items-center justify-between py-2">
      <span className="text-sm text-slate-700">{label}</span>
      <button
        onClick={() => onChange(!value)}
        className={`w-10 h-5 rounded-full relative transition-colors flex-shrink-0 ${value ? 'bg-jay-blue' : 'bg-slate-300'}`}
      >
        <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${value ? 'right-0.5' : 'left-0.5'}`} />
      </button>
    </div>
  )
}

function Card({ title, children }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-5">
      <h2 className="font-semibold text-slate-700 text-sm mb-4">{title}</h2>
      <div className="space-y-3">{children}</div>
    </div>
  )
}

export default function Settings({ settings, onSave, onRun }) {
  const [anthropicApiKey, setAnthropicApiKey] = useState(settings?.anthropicApiKey || '')
  const [school,          setSchool]          = useState(settings?.school          || '')
  const [locations,       setLocations]       = useState((settings?.targetLocations || []).join(', '))
  const [keywords,        setKeywords]        = useState((settings?.roleKeywords    || []).join(', '))
  const [skills,          setSkills]          = useState((settings?.skills          || []).join(', '))
  const [cold,            setCold]            = useState(true)
  const [jobspy,          setJobspy]          = useState(true)
  const [saved,           setSaved]           = useState(false)

  const splitCsv = str => str.split(',').map(s => s.trim()).filter(Boolean)

  const handleSave = () => {
    onSave({
      anthropicApiKey,
      school,
      targetLocations: splitCsv(locations),
      roleKeywords:    splitCsv(keywords),
      skills:          splitCsv(skills),
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const keySet = !!anthropicApiKey

  return (
    <div className="grid grid-cols-2 gap-4 max-w-2xl">
      <Card title="API Keys">
        <div>
          <label className="text-xs text-slate-500 font-medium block mb-1">
            Anthropic API Key <span className="text-red-400">*</span>
          </label>
          <div className="flex gap-2 items-center">
            <input
              type="password"
              placeholder="sk-ant-..."
              value={anthropicApiKey}
              onChange={e => { setAnthropicApiKey(e.target.value); setSaved(false) }}
              className={`flex-1 border rounded-lg px-3 py-2 text-sm outline-none ${
                keySet
                  ? 'border-green-300 bg-green-50 focus:border-green-400'
                  : 'border-slate-200 bg-white focus:border-jay-blue'
              }`}
            />
            {keySet && <CheckIcon className="w-5 h-5 text-green-500 flex-shrink-0" />}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Required for contact research. Never stored to disk —{' '}
            <span className="font-medium">session only</span>.
          </p>
        </div>
        <div className="pt-2">
          <button
            onClick={handleSave}
            className={`w-full py-2 rounded-lg text-sm font-semibold transition-colors ${
              saved
                ? 'bg-green-100 text-green-700 border border-green-200'
                : 'bg-jay-blue text-white hover:bg-jay-crest'
            }`}
          >
            {saved ? 'Saved' : 'Save Settings'}
          </button>
        </div>
        <div className="pt-1">
          <button
            onClick={onRun}
            disabled={!keySet}
            className="w-full py-2 bg-slate-800 text-white rounded-lg text-sm font-semibold hover:bg-slate-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Run Pipeline Now
          </button>
          {!keySet && (
            <p className="text-xs text-slate-400 mt-1 text-center">Save your API key first</p>
          )}
        </div>
      </Card>

      <Card title="Job Preferences">
        <Field
          label="School / University"
          placeholder="Temple University"
          value={school}
          onChange={e => setSchool(e.target.value)}
          hint="Used in outreach message personalization"
        />
        <Field
          label="Target Locations (comma separated)"
          placeholder="Philadelphia, Remote"
          value={locations}
          onChange={e => setLocations(e.target.value)}
        />
        <Field
          label="Role Keywords (comma separated)"
          placeholder="software engineering, backend, AI"
          value={keywords}
          onChange={e => setKeywords(e.target.value)}
        />
        <Field
          label="Skills (comma separated)"
          placeholder="Python, React, FastAPI"
          value={skills}
          onChange={e => setSkills(e.target.value)}
        />
        <div className="border-t border-slate-100 pt-2 space-y-0">
          <Toggle label="Enable Cold Outreach"       value={cold}   onChange={setCold} />
          <Toggle label="JobSpy (LinkedIn / Indeed)" value={jobspy} onChange={setJobspy} />
        </div>
      </Card>

      <Card title="Color Key">
        {[
          { color: 'bg-green-100  border-green-200',  label: 'Green',  desc: 'Posted < 6h — apply immediately' },
          { color: 'bg-blue-100   border-blue-200',   label: 'Blue',   desc: 'Posted < 24h — apply today' },
          { color: 'bg-yellow-100 border-yellow-200', label: 'Yellow', desc: 'Posted < 48h — apply this week' },
          { color: 'bg-white      border-slate-200',  label: 'White',  desc: 'Posted > 48h' },
        ].map(r => (
          <div key={r.label} className={`flex items-center gap-3 px-3 py-2 rounded-lg border ${r.color}`}>
            <span className="text-xs font-semibold text-slate-700 w-12">{r.label}</span>
            <span className="text-xs text-slate-500">{r.desc}</span>
          </div>
        ))}
      </Card>

      <Card title="How it works">
        <ol className="space-y-2 text-xs text-slate-600 list-decimal list-inside">
          <li>Enter your Anthropic API key above and click <strong>Save Settings</strong>.</li>
          <li>Click <strong>Run Pipeline Now</strong> (or the button in the sidebar).</li>
          <li>The pipeline scrapes Greenhouse, Lever, LinkedIn, and Wellfound for intern postings.</li>
          <li>Claude researches contacts at each company and drafts outreach messages.</li>
          <li>Results appear in Job Leads, Outreach, and Cold Outreach tabs (3-5 minutes).</li>
        </ol>
        <p className="text-xs text-slate-400 pt-2">
          Your API key is sent directly to the backend and discarded after each run — it is never stored on the server.
        </p>
      </Card>
    </div>
  )
}

function CheckIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 00-1.414 0L8 12.586 4.707 9.293a1 1 0 00-1.414 1.414l4 4a1 1 0 001.414 0l8-8a1 1 0 000-1.414z" clipRule="evenodd" />
    </svg>
  )
}
