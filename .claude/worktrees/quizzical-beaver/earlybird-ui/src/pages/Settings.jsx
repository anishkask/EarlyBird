import { useState } from 'react'

function Field({ label, ...props }) {
  return (
    <div>
      <label className="text-xs text-slate-500 font-medium block mb-1">{label}</label>
      <input
        className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-jay-blue bg-white"
        {...props}
      />
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

export default function Settings() {
  const [cold, setCold] = useState(true)
  const [emails, setEmails] = useState(false)
  const [jobspy, setJobspy] = useState(true)

  return (
    <div className="grid grid-cols-2 gap-4 max-w-2xl">
      <Card title="Your Profile">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Your Name"  defaultValue="Anishka Kakade" />
          <Field label="Your Email" defaultValue="anishka@drexel.edu" type="email" />
        </div>
        <Field label="School" defaultValue="Drexel University" />
        <Field label="LinkedIn URL" defaultValue="https://linkedin.com/in/anishkak" />
        <div>
          <label className="text-xs text-slate-500 font-medium block mb-1">Background</label>
          <textarea
            defaultValue="CS junior at Drexel, experience in RAG/LLMs, Python, backend engineering."
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-jay-blue bg-white h-20 resize-none"
          />
        </div>
        <button className="w-full py-2 bg-jay-blue text-white rounded-lg text-sm font-semibold hover:bg-jay-crest transition-colors">
          Save Profile
        </button>
      </Card>

      <Card title="Pipeline Settings">
        <Field label="Hours Window" defaultValue="72" type="number" />
        <Field label="Max Jobs for Outreach" defaultValue="35" type="number" />
        <Field label="Cold Outreach Limit" defaultValue="5" type="number" />
        <div className="border-t border-slate-100 pt-2 space-y-0">
          <Toggle label="Enable Cold Outreach"  value={cold}   onChange={setCold} />
          <Toggle label="Auto-send Emails"       value={emails} onChange={setEmails} />
          <Toggle label="JobSpy (LinkedIn/Indeed)" value={jobspy} onChange={setJobspy} />
        </div>
      </Card>

      <Card title="API Keys">
        <div>
          <label className="text-xs text-slate-500 font-medium block mb-1">Anthropic API Key</label>
          <div className="flex gap-2 items-center">
            <input
              type="password"
              defaultValue="sk-ant-api03-••••••••"
              className="flex-1 border border-green-300 bg-green-50 rounded-lg px-3 py-2 text-sm outline-none"
            />
            <CheckIcon className="w-5 h-5 text-green-500 flex-shrink-0" />
          </div>
        </div>
        <div>
          <label className="text-xs text-slate-500 font-medium block mb-1">Gmail OAuth</label>
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
            <span className="text-xs text-slate-400 flex-1">credentials.json not found</span>
            <button className="text-xs text-jay-blue hover:underline flex-shrink-0">Connect</button>
          </div>
        </div>
      </Card>

      <Card title="Color Key">
        {[
          { color: 'bg-green-100 border-green-200',  label: 'Green',  desc: 'Posted < 6h — apply immediately' },
          { color: 'bg-blue-100  border-blue-200',   label: 'Blue',   desc: 'Posted < 24h — apply today' },
          { color: 'bg-yellow-100 border-yellow-200',label: 'Yellow', desc: 'Posted < 48h — apply this week' },
          { color: 'bg-white     border-slate-200',  label: 'White',  desc: 'Posted > 48h' },
        ].map(r => (
          <div key={r.label} className={`flex items-center gap-3 px-3 py-2 rounded-lg border ${r.color}`}>
            <span className="text-xs font-semibold text-slate-700 w-12">{r.label}</span>
            <span className="text-xs text-slate-500">{r.desc}</span>
          </div>
        ))}
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
