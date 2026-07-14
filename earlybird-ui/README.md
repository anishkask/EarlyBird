# EarlyBird UI

React + Vite + Tailwind dashboard for the EarlyBird pipeline. See the [root README](../README.md) for the full project.

```bash
npm install
npm run dev        # dev server on :5173, expects the API on :8000
npm run build      # production build to dist/
```

Set `VITE_API_URL` in `.env.local` to point at a non-default backend.

Structure: `src/pages/` holds the dashboard views (Jobs, Outreach, Cold Outreach, Settings), `src/components/` the shared pieces (header, sidebar, run-progress modal). Security headers for the Vercel deployment live in `vercel.json`.
