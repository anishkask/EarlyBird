import { useState } from 'react'
import Badge from '../components/Badge'

const CONTACTS = [
  {
    initials: 'CW', color: 'bg-blue-100 text-blue-600',
    name: 'Caitlin Wright', title: 'Recruiter', company: 'Airbnb',
    email: 'caitlin.wright@airbnb.com', domain: 'airbnb.com',
    apollo: 'https://app.apollo.io/#/people?q_organization_domains[]=airbnb.com',
    linkedin: '#', status: 'new',
    role: 'ML Engineering Intern 2026', posted: '2h ago',
    linkedinMsg: 'Hi Caitlin — I came across your profile while researching Airbnb. I\'m a junior CS student at Drexel applying for the ML Engineering Intern role and would love to connect and learn more about the team.',
    emailSubject: 'Drexel CS Student — ML Engineering Intern @ Airbnb',
    emailBody: `Hi Caitlin,\n\nI came across the ML Engineering Intern posting at Airbnb and wanted to reach out directly. I'm a junior CS student at Drexel University with experience in RAG pipelines, LLM fine-tuning, and backend development in Python.\n\nI'd love to learn more about the team and the internship program. Would you have 15 minutes for a quick chat?\n\nBest,\nAnishka`,
  },
  {
    initials: 'SP', color: 'bg-purple-100 text-purple-600',
    name: 'Shivani Patel', title: 'Campus Recruiter', company: 'Notion',
    email: 's.patel@notion.so', domain: 'notion.so',
    apollo: 'https://app.apollo.io/#/people?q_organization_domains[]=notion.so',
    linkedin: '#', status: 'draft',
    role: 'Backend Engineer Intern', posted: '5h ago',
    linkedinMsg: 'Hi Shivani — I noticed you handle university recruiting at Notion. I\'m a Drexel CS junior interested in the Backend Intern role and would love to connect!',
    emailSubject: 'Drexel CS Student — Backend Engineer Intern @ Notion',
    emailBody: `Hi Shivani,\n\nI came across the Backend Engineer Intern posting at Notion and wanted to reach out. I'm a junior at Drexel with Python and distributed systems experience.\n\nWould love to connect!\n\nBest,\nAnishka`,
  },
  {
    initials: 'MK', color: 'bg-green-100 text-green-600',
    name: 'Maya Kim', title: 'Univ. Recruiting', company: 'Vercel',
    email: 'm.kim@vercel.com', domain: 'vercel.com',
    apollo: 'https://app.apollo.io/#/people?q_organization_domains[]=vercel.com',
    linkedin: '#', status: 'sent',
    role: 'Fullstack Intern 2026', posted: '36h ago',
    linkedinMsg: 'Hi Maya — I\'m a Drexel CS student interested in the Fullstack Intern role at Vercel. Would love to connect!',
    emailSubject: 'Drexel CS Student — Fullstack Intern @ Vercel',
    emailBody: `Hi Maya,\n\nI'm a junior CS student at Drexel interested in the Fullstack Intern role. Would love to chat!\n\nBest,\nAnishka`,
  },
]

const STATUS_BADGE = { new: 'green', draft: 'blue', sent: 'pink' }
const STATUS_LABEL = { new: 'New',   draft: 'Draft', sent: 'Sent' }

export default function Outreach() {
  const [selected, setSelected] = useState(0)
  const c = CONTACTS[selected]

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Contact list */}
      <div className="col-span-1 space-y-2">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Contacts ({CONTACTS.length})</p>
        {CONTACTS.map((contact, i) => (
          <button
            key={contact.name}
            onClick={() => setSelected(i)}
            className={`w-full text-left p-4 rounded-xl border transition-all ${
              selected === i
                ? 'border-jay-blue bg-blue-50 shadow-sm'
                : 'border-slate-100 bg-white hover:border-slate-200'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 ${contact.color}`}>
                {contact.initials}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm text-slate-800 truncate">{contact.name}</p>
                <p className="text-xs text-slate-400 truncate">{contact.title} · {contact.company}</p>
              </div>
              <Badge color={STATUS_BADGE[contact.status]}>{STATUS_LABEL[contact.status]}</Badge>
            </div>
          </button>
        ))}
      </div>

      {/* Detail panel */}
      <div className="col-span-2 bg-white rounded-xl shadow-sm border border-slate-100 p-5 flex flex-col gap-4">
        {/* Contact header */}
        <div className="flex items-center gap-4 pb-4 border-b border-slate-100">
          <div className={`w-14 h-14 rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0 ${c.color}`}>
            {c.initials}
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="font-bold text-slate-800 text-lg">{c.name}</h2>
            <p className="text-slate-400 text-sm">{c.title} at {c.company} · Found via web search</p>
            <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
              <a href={c.linkedin} className="text-xs text-jay-blue hover:underline">LinkedIn</a>
              <span className="text-slate-300 text-xs">·</span>
              <span className="text-xs text-slate-400">{c.email}</span>
              <span className="text-slate-300 text-xs">·</span>
              <a href={c.apollo} target="_blank" rel="noreferrer" className="text-xs text-purple-500 hover:underline">Apollo</a>
            </div>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="text-xs text-slate-400">Re: {c.role}</p>
            <p className="text-xs text-green-600 font-medium mt-0.5">Posted {c.posted}</p>
          </div>
        </div>

        {/* LinkedIn message */}
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            LinkedIn Message <span className="font-normal text-slate-400 normal-case">(280 chars max)</span>
          </p>
          <div className="bg-slate-50 rounded-lg p-3 text-sm text-slate-700 leading-relaxed border border-slate-100">
            {c.linkedinMsg}
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
              <p className="text-xs text-slate-500">To: <span className="text-slate-700">{c.email}</span></p>
              <p className="text-xs text-slate-500">Subject: <span className="text-slate-700">{c.emailSubject}</span></p>
            </div>
            <pre className="p-3 text-sm text-slate-700 leading-relaxed whitespace-pre-wrap font-sans overflow-y-auto max-h-36">
              {c.emailBody}
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
