export default function Header({ title, sub }) {
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex-shrink-0">
      <h1 className="text-slate-800 font-bold text-lg leading-tight">{title}</h1>
      <p className="text-slate-400 text-xs mt-0.5">{sub}</p>
    </header>
  )
}
