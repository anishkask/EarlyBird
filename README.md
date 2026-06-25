# EarlyBird

> Apply before everyone else does.

EarlyBird is a job search automation tool for students and early-career engineers who want to apply to roles within hours of posting, before listings hit mass job boards and inboxes flood with applicants.

It polls company ATS systems (Greenhouse and Lever), runs live web searches for recruiters and founders, drafts personalized outreach messages, and presents everything in a React dashboard backed by a FastAPI server. It also runs as a standalone CLI that writes a color-coded Excel tracker.

## Architecture

EarlyBird has three parts:

1. Pipeline (`job_pipeline_full.py`, `cold_outreach.py`): the core scraping, contact research, and outreach logic. Runs from the CLI and writes Excel, or is called by the API.
2. Backend (`api.py`): a FastAPI server that runs the pipeline in a background thread and returns results as JSON. Each visitor supplies their own Anthropic API key per request.
3. Frontend (`earlybird-ui/`): a React + Vite + Tailwind dashboard. Users enter their key, run the pipeline, and view jobs and contacts in the browser.

Live site: [earlybird-ashen.vercel.app](https://earlybird-ashen.vercel.app)

## Features

- Scrapes Greenhouse, Lever, LinkedIn, Indeed, and Wellfound within hours of posting
- Dynamic ATS discovery: finds and verifies company job boards in real time instead of relying on a fixed company list
- Filters by US location and remote, removing international noise
- Deduplicates across sources so the same role never appears twice
- Uses the Claude API with live web search to find real recruiters and founders by name
- Drafts a LinkedIn message per contact that you review and send manually
- Cold outreach: researches founders and CEOs at VC portfolio companies, even those with no open roles
- Apollo lookup links and company domain columns for email pattern discovery
- CLI still generates a color-coded Excel file: green for posted under 6h, blue for under 24h, yellow for under 48h

## Using the live site

1. Open [earlybird-ashen.vercel.app](https://earlybird-ashen.vercel.app)
2. Go to Settings and enter your Anthropic API key. The key is held in memory for the session only. It is never written to disk or stored on the server.
3. Optionally set your school, target locations, role keywords, and skills, then click Save Settings.
4. Click Run Pipeline. The run starts in the background and the page polls for status every 5 seconds.
5. After a few minutes, results appear in the Job Leads, Outreach, and Cold Outreach tabs.

A run takes roughly 3 to 5 minutes depending on how many companies have fresh postings.

## Dynamic ATS discovery

Instead of a hardcoded company list, `build_dynamic_watchlist()` builds the watchlist on every run:

1. Reads `data/cold_outreach_cache.json`, which accumulates companies discovered by VC portfolio scraping.
2. For each company, constructs candidate slugs and checks live Greenhouse and Lever endpoints with a short timeout.
3. Keeps companies whose boards return an active, non-empty jobs list.
4. Caches verified slugs in `watchlist_cache.json` and reuses the cache for a week before re-verifying.
5. Also pulls additional companies from real-time sources such as YC Work at a Startup and Wellfound.

The watchlist grows as cold outreach discovers more companies, and shrinks as companies stop posting.

## Security

The site is designed to be used by any visitor with their own API key, so it takes the following precautions:

- API keys are accepted per request, used only for that run, and never logged, written to disk, or stored in the run record.
- Pipeline results contain personal contact data, so each run is keyed by a high-entropy, unguessable token. Unknown or expired tokens return 404, which closes insecure-direct-object-reference access.
- Runs auto-expire after 30 minutes and the in-memory store is size-capped, so personal data does not linger.
- Per-IP rate limiting and a concurrency cap bound abuse and resource exhaustion.
- Strict input validation on every field. Raw exceptions are logged on the server and never returned to clients.
- CORS is restricted to the deployed frontend origin. Interactive API docs are disabled.
- The frontend sends a Content-Security-Policy, HSTS, X-Frame-Options, and related headers. API key inputs disable browser autofill and storage.

## Local development

### Backend

```bash
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

The API is then available at `http://localhost:8000`. Check `http://localhost:8000/health`.

### Frontend

```bash
cd earlybird-ui
npm install
npm run dev
```

Set `VITE_API_URL` so the frontend knows where the backend is. Create `earlybird-ui/.env.local`:

```
VITE_API_URL=http://localhost:8000
```

If `VITE_API_URL` is not set, the frontend defaults to `http://localhost:8000`.

## CLI usage

The CLI behaves exactly as before and still writes Excel locally.

```bash
# Standard run, last 72 hours
python job_pipeline_full.py

# Fresh only
python job_pipeline_full.py --hours 24

# Scrape only, skip all Claude API calls
python job_pipeline_full.py --scrape-only
```

Configure the CLI through `.env`:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...
YOUR_NAME=Your Name
YOUR_EMAIL=you@email.com
YOUR_SCHOOL=Your University
YOUR_LINKEDIN=https://linkedin.com/in/yourhandle
MY_BACKGROUND=Brief summary of your skills and experience
```

## API endpoints

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET | `/health` | Liveness check. Returns `{"status":"ok"}` |
| POST | `/run-pipeline` | Starts a run. Body includes `anthropic_api_key`, `hours`, `cold_outreach`, `cold_outreach_limit`. Returns `run_id` |
| GET | `/status/{run_id}` | Returns the run status: queued, running, complete, or error |
| GET | `/results/{run_id}` | Returns the full results JSON once the run is complete |
| POST | `/settings` | Validates preferences for the session. Nothing is persisted |

## Deployment

The frontend is hosted on Vercel and the backend on Render. Both deploy from the `main` branch.

### Backend (Render)

The backend is defined in `render.yaml`. To create the service the first time:

1. On Render, choose New, then Web Service, and connect this repository.
2. Branch: `main`. Build command: `pip install -r requirements.txt`. Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`.
3. Choose the free instance type and create the service.
4. Copy the resulting URL, for example `https://earlybird-api.onrender.com`.

### Frontend (Vercel)

1. The Vercel project root directory is `earlybird-ui`.
2. Add an environment variable `VITE_API_URL` set to the Render backend URL.
3. Vercel builds with `npm run build` and serves the `dist` output.

## Redeploying

### Redeploy the frontend

Vercel rebuilds automatically on every push to `main`. To trigger a deploy manually instead:

- From the dashboard: open the Vercel project, go to Deployments, open the most recent deployment menu, and choose Redeploy.
- From the CLI: `cd earlybird-ui && npx vercel --prod`.

If you change `VITE_API_URL`, redeploy afterward so the new value is baked into the build.

### Redeploy the backend

`render.yaml` sets `autoDeploy: false`, so pushing to `main` does not deploy on its own. To deploy the latest commit:

- From the dashboard: open the `earlybird-api` service, choose Manual Deploy, then Deploy latest commit.
- To deploy on every push instead, set `autoDeploy: true` in `render.yaml` or enable auto-deploy in the service settings.

After a backend redeploy, confirm it is healthy by opening `https://YOUR-RENDER-URL/health`.

## Stack

Pipeline and backend:

- Python 3.10 or newer
- FastAPI and Uvicorn
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) with the `web_search_20250305` tool
- [JobSpy](https://github.com/cullenwatson/JobSpy) for LinkedIn and Indeed
- openpyxl, BeautifulSoup, requests, python-dotenv

Frontend:

- React and Vite
- Tailwind CSS v3
- Hosted on Vercel

## Notes

- LinkedIn and Indeed scraping via JobSpy may conflict with their terms of service. Run at most once per day.
- Never commit `.env`, `token.json`, `credentials.json`, or `*.xlsx` files. All are listed in `.gitignore`.
- The Render free tier sleeps after a period of inactivity. The first request after it sleeps takes around 30 seconds to wake the service.

## Roadmap

- Resume-to-job matching using embeddings
- Daily digest summarizing each morning's run
- Handshake integration for student-exclusive postings

## License

MIT
