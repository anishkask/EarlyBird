import { useState } from 'react'
import Badge from '../components/Badge'

const STATUS_BADGE = { new: 'green', draft: 'blue', sent: 'pink' }
const STATUS_LABEL = { new: 'New',   draft: 'Draft', sent: 'Sent' }

function initialsFrom(name) {
  return name
    .split(' ')
    .filter(Boolean)
    .map(part => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

export default function Outreach({ pipeline }) {
  const [selected, setSelected] = useState(0)

  const contacts = pipeline?.outreach || []
  // Clamp at render time; keeps the index valid when a new run shrinks the list.
  const active = selected < contacts.length ? selected : 0

  if (!pipeline) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
        <h2 className="text-lg font-semibold text-slate-800">No outreach data yet</h2>
        <p className="text-sm text-slate-500 mt-2">Go to <strong>Settings</strong>, enter your Anthropic API key, then click <strong>Run Pipeline</strong>.</p>
      </div>
    )
  }
  const contact = contacts[active] || {}

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Contact list */}
      <div className="col-span-1 space-y-2">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Contacts ({contacts.length})</p>
        {contacts.map((contactItem, i) => {
          const name = contactItem.contactName || contactItem.name || 'Recruiter'
          const title = contactItem.contactTitle || contactItem.title || 'Contact'
          const company = contactItem.company || 'Company'
          const initials = contactItem.initials || initialsFrom(name)
          const status = contactItem.emailSent ? 'sent' : 'new'

          return (
            <button
              key={`${name}-${i}`}
              onClick={() => setSelected(i)}
              className={`w-full text-left p-4 rounded-xl border transition-all ${
                active === i
                  ? 'border-jay-blue bg-blue-50 shadow-sm'
                  : 'border-slate-100 bg-white hover:border-slate-200'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 ${contactItem.color || 'bg-slate-100 text-slate-700'}`}>
                  {initials}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm text-slate-800 truncate">{name}</p>
                  <p className="text-xs text-slate-400 truncate">{title} · {company}</p>
                </div>
                <Badge color={STATUS_BADGE[status] || 'gray'}>{STATUS_LABEL[status] || 'Draft'}</Badge>
              </div>
            </button>
          )
        })}
      </div>

      {/* Detail panel */}
      <div className="col-span-2 bg-white rounded-xl shadow-sm border border-slate-100 p-5 flex flex-col gap-4">
        {/* Contact header */}
        <div className="flex items-center gap-4 pb-4 border-b border-slate-100">
          <div className={`w-14 h-14 rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0 ${contact.color || 'bg-slate-100 text-slate-700'}`}>
            {contact.initials || initialsFrom(contact.contactName || contact.name || '')}
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="font-bold text-slate-800 text-lg">{contact.contactName || contact.name || 'Recruiter'}</h2>
            <p className="text-slate-400 text-sm">{contact.contactTitle || contact.title || 'Contact'} at {contact.company}</p>
            <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
              <a href={contact.linkedinUrl || '#'} className="text-xs text-jay-blue hover:underline">LinkedIn</a>
              <span className="text-slate-300 text-xs">·</span>
              <span className="text-xs text-slate-400">{contact.email}</span>
              <span className="text-slate-300 text-xs">·</span>
              <a href={contact.apolloLookup || '#'} target="_blank" rel="noreferrer" className="text-xs text-purple-500 hover:underline">Apollo</a>
            </div>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="text-xs text-slate-400">Re: {contact.role}</p>
            <p className="text-xs text-green-600 font-medium mt-0.5">Posted {contact.posted || contact.posted || 'N/A'}</p>
          </div>
        </div>

        {/* LinkedIn message */}
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            LinkedIn Message <span className="font-normal text-slate-400 normal-case">(280 chars max)</span>
          </p>
          <div className="bg-slate-50 rounded-lg p-3 text-sm text-slate-700 leading-relaxed border border-slate-100">
            {contact.linkedinMsg || 'No LinkedIn message available for this contact.'}
          </div>
          <div className="flex justify-end mt-2">
            <button className="text-xs bg-jay-blue text-white px-4 py-1.5 rounded-lg font-medium hover:bg-jay-crest transition-colors">
              Copy Message
            </button>
          </div>
        </div>

        {/* Email draft */}
        <div className="flex-1">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Email Draft</p>
          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <div className="bg-slate-50 px-3 py-2 border-b border-slate-200 space-y-0.5">
              <p className="text-xs text-slate-500">To: <span className="text-slate-700">{contact.email || 'No email found'}</span></p>
              <p className="text-xs text-slate-500">Subject: <span className="text-slate-700">{contact.emailSubject || 'No subject available'}</span></p>
            </div>
            <pre className="p-3 text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-sans overflow-y-auto max-h-36">
              {contact.emailBody || 'No email draft available for this contact.'}
            </pre>
          </div>
          <div className="flex justify-end gap-2 mt-2">
            <button className="text-xs border border-slate-200 text-slate-600 px-4 py-1.5 rounded-lg hover:bg-slate-50 transition-colors">
              Edit
            </button>
            <button className="text-xs bg-green-500 text-white px-4 py-1.5 rounded-lg font-medium hover:bg-green-600 transition-colors">
              Send Email
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
