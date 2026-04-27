const variants = {
  green:  'bg-green-100 text-green-700',
  blue:   'bg-blue-100  text-blue-700',
  yellow: 'bg-yellow-100 text-yellow-700',
  gray:   'bg-slate-100 text-slate-500',
  pink:   'bg-pink-100  text-pink-700',
}

export default function Badge({ color = 'gray', children }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${variants[color]}`}>
      {children}
    </span>
  )
}
