export default function BluejayLogo({ size = 36 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="EarlyBird logo"
    >
      {/* Body */}
      <ellipse cx="32" cy="38" rx="16" ry="13" fill="#1D6FA4" />

      {/* Wing highlight */}
      <ellipse cx="32" cy="38" rx="10" ry="8" fill="#4BA3D3" opacity="0.5" />

      {/* Wing feather tips (darker band) */}
      <path
        d="M18 44 Q24 50 32 51 Q40 50 46 44"
        stroke="#0B4F78"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
      />

      {/* Head */}
      <circle cx="32" cy="24" r="10" fill="#1D6FA4" />

      {/* Crest (three feathers pointing up-right) */}
      <path d="M36 16 Q40 8 44 5" stroke="#0B4F78" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <path d="M33 14 Q36 6 38 2"  stroke="#0B4F78" strokeWidth="2"   strokeLinecap="round" fill="none" />
      <path d="M30 14 Q31 7 30 3"  stroke="#1D6FA4" strokeWidth="1.5" strokeLinecap="round" fill="none" />

      {/* White cheek patch */}
      <ellipse cx="29" cy="26" rx="5" ry="4" fill="white" opacity="0.85" />

      {/* Black necklace band */}
      <path
        d="M22 28 Q27 32 32 32 Q37 32 42 28"
        stroke="#0D1B2A"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
      />

      {/* Eye */}
      <circle cx="34" cy="22" r="2.2" fill="#0D1B2A" />
      <circle cx="34.7" cy="21.3" r="0.7" fill="white" />

      {/* Beak */}
      <path d="M40 24 L46 26 L40 27 Z" fill="#CBD5A0" />

      {/* Tail */}
      <path d="M16 42 Q10 50 12 56" stroke="#0B4F78" strokeWidth="3" strokeLinecap="round" fill="none" />
      <path d="M18 44 Q13 52 16 58" stroke="#1D6FA4" strokeWidth="2" strokeLinecap="round" fill="none" />
      <path d="M20 45 Q17 53 20 59" stroke="#4BA3D3" strokeWidth="1.5" strokeLinecap="round" fill="none" />

      {/* Feet / perch line */}
      <path d="M26 51 L26 57 M26 57 L22 60 M26 57 L30 60" stroke="#0B4F78" strokeWidth="1.5" strokeLinecap="round" fill="none" />
      <path d="M36 51 L36 57 M36 57 L32 60 M36 57 L40 60" stroke="#0B4F78" strokeWidth="1.5" strokeLinecap="round" fill="none" />
    </svg>
  )
}
