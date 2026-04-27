import { useState } from 'react'

export default function RunModal({ onClose }) {
  const [hours, setHours] = useState(72)
  const [coldOutreach, setColdOutreach] = useState(true)
  const [sendEmails, setSendEmails] = useState(false)

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-xl p-6 w-96">
        <h2 className="font-bold text-slate-800 text-lg mb-1">Run Pipeline</h2>
        <p className="text-slate-400 text-sm mb-5">Configure and launch a new scrape run</p>

        <div className="space-y-4 mb-6">
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
          <Toggle label="Send Emails Automatically" value={sendEmails} onChange={setSendEmails} />
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 border border-slate-200 rounded-lg py-2 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-jay-blue text-white rounded-lg py-2 text-sm font-semibold hover:bg-jay-crest transition-colors"
          >
            Run Now
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
        <span
          className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${value ? 'right-0.5' : 'left-0.5'}`}
        />
      </button>
    </div>
  )
}
