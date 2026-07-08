# EarlyBird

> Apply before everyone else does.

EarlyBird is a job search automation tool for engineers who want to see fresh paid roles within hours of posting, before listings hit mass job boards and inboxes flood with applicants. It targets full-time, contract, and contract-to-hire roles in the AI/ML and full-stack space.

It polls company ATS systems (Greenhouse, Lever, Ashby) for a config-driven watchlist plus the RemoteOK board, ranks roles by freshness and profile match, drafts a short outreach message for the top results using the Claude API with live web search, and writes a color-coded Excel tracker. It also runs behind a FastAPI server with a React dashboard.

## Architecture

EarlyBird has three parts:

1. Pipeline (`job_pipeline_full.py`, `cold_outreach.py`): the core scraping, contact research, and outreach logic. Runs from the CLI and writes Excel, or is called by the API.
2. Backend (`api.py`): a FastAPI server that runs the pipeline in a background thread and returns results as JSON. Each visitor supplies their own Anthropic API key per request.
3. Frontend (`earlybird-ui/`): a React + Vite + Tailwind dashboard. Users enter their key, run the pipeline, and view jobs and contacts in the browser.

Live site: [earlybird-ashen.vercel.app](https://earlybird-ashen.vercel.app)

## Features

- Pulls from stable, terms-respecting endpoints only: Greenhouse, Lever, and Ashby ATS JSON APIs, plus the RemoteOK JSON board
- Targets paid roles (full-time, contract, contract-to-hire) and filters internships out by default
- Detects and deprioritizes roles that require a conferred degree, without ever filtering on visa sponsorship
- Ranks every role by freshness, profile keyword match, and paid role type, then dedupes across sources
- Flags urgency: roles under 1 hour old are highlighted red, under 6 hours green
- For the top ranked roles, researches a likely outreach contact with the Claude API (live web search) and drafts a short tailored message
- Sources, target companies, keywords, and filters are all controlled from a single `config.py`
- Fast `--fresh` mode for frequent polling so you see new roles first
- Color-coded Excel tracker with apply links, posting age, rank, and role type
- LinkedIn and Indeed scraping is removed from the default run (anti-bot fragility and terms conflicts); it remains behind a config flag, off by default

## Using the live site

1. Open [earlybird-ashen.vercel.app](https://earlybird-ashen.vercel.app)
2. Go to Settings and enter your Anthropic API key. The key is held in memory for the session only. It is never written to disk or stored on the server.
3. Optionally set your school, target locations, role keywords, and skills, then click Save Settings.
4. Click Run Pipeline. The run starts in the background and the page polls for status every 5 seconds.
5. After a few minutes, results appear in the Job Leads, Outreach, and Cold Outreach tabs.

A run takes roughly 3 to 5 minutes depending on how many companies have fresh postings.

## Configuration

Everything you tune lives in `config.py`, so you never edit core logic. Nothing personal or secret belongs here (see note below).

Relevance and sources:
- `PROFILE_KEYWORDS`: keywords that define relevance and drive ranking (high, core, and adjacent tiers).
- `SOURCES`: turn each source on or off. Greenhouse, Lever, Ashby, and RemoteOK are on by default; Wellfound and JobSpy (LinkedIn/Indeed) are off.
- `WATCHLIST`: target companies as `{name, ats_type, slug}` (Greenhouse/Lever). Slugs that no longer resolve are skipped gracefully.
- `ASHBY_COMPANIES`: Ashby board slugs (Ashby skews to startups).

Role and seniority filters (tune to your own level):
- `SENIORITY_EXCLUDE`: title terms to drop (default excludes staff/principal/lead/senior/manager/director and similar).
- `MAX_YEARS`: drop roles whose description requires at least this many years of experience.
- `ENTRY_MID_SIGNALS`: title terms that mark an entry/mid role, used for a ranking bonus.
- `FUNCTION_EXCLUDE`: off-target functions to drop (default excludes security, IT, SRE, hardware, data science, sales/solutions engineering, and similar).
- `INCLUDE_INTERNSHIPS`, `DEGREE_REQUIREMENT_MODE`, `REMOTE_OK`.

Company targeting:
- `EXCLUDE_COMPANIES`: companies to drop entirely (matched as a lowercase substring of the company name).
- `LARGE_BOARD_THRESHOLD` / `SMALL_BOARD_THRESHOLD`: a company-size proxy based on how many roles its ATS board lists. Small boards get a ranking bonus, large boards a penalty.

Run tuning:
- `DEFAULT_HOURS`, `FRESH_HOURS`, `OUTREACH_TOP_N`.

Ranking is attainability-aware: it rewards entry/mid level, smaller companies, stack-keyword match, and freshness, and penalizes high seniority and large or excluded companies.

Secrets and personal identity stay in `.env` and never go in `config.py`. Your name, background, and API keys are read from environment variables at runtime, so nothing identifying is committed to the repo.

### Watchlist and discovery

The watchlist is `config.WATCHLIST` plus any companies confirmed by discovery. On a full run, EarlyBird verifies company names from the cold-outreach cache against live Greenhouse and Lever endpoints and stores the confirmed ones in `watchlist_cache.json` for future runs. Loading the watchlist never makes network calls, so runs start instantly.

Note on stable endpoints: ai-jobs.net exposes no stable public feed, so it is intentionally not integrated. RemoteOK covers AI-board listings through its documented JSON API instead.

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

The CLI writes a color-coded Excel tracker locally.

```bash
# Standard run (config.DEFAULT_HOURS lookback), with outreach drafting
python job_pipeline_full.py

# Fast poll: short window (config.FRESH_HOURS), scrape and Excel only, no Claude calls
python job_pipeline_full.py --fresh

# Custom lookback window
python job_pipeline_full.py --hours 24

# Scrape and write Excel only, skip all Claude API calls
python job_pipeline_full.py --scrape-only
```

Run modes at a glance:

| Mode | Sources | Outreach drafting | Speed |
| ---- | ------- | ----------------- | ----- |
| `--fresh` | ATS + RemoteOK | no | fastest, for frequent polling |
| `--scrape-only` | ATS + RemoteOK | no | fast, no API key needed |
| standard | ATS + RemoteOK | yes (top `OUTREACH_TOP_N`) | slower, needs a funded key |

Secrets and identity go in `.env`:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...
YOUR_NAME=Your Name
YOUR_EMAIL=you@email.com
YOUR_LINKEDIN=https://linkedin.com/in/yourhandle
MY_BACKGROUND=Brief summary of your skills and experience
```

Outreach is draft-only. EarlyBird never sends email on your behalf.

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
- openpyxl, BeautifulSoup, requests, python-dotenv
- [JobSpy](https://github.com/cullenwatson/JobSpy) is an optional, disabled-by-default source for LinkedIn and Indeed

Frontend:

- React and Vite
- Tailwind CSS v3
- Hosted on Vercel

## Scheduling

For speed-to-first-sight, poll frequently with the fast `--fresh` mode. It needs no API key and skips outreach.

Windows (Task Scheduler), `run_earlybird.bat`:

```bat
@echo off
cd C:\path\to\EarlyBird
python job_pipeline_full.py --fresh >> logs\pipeline_log.txt 2>&1
```

Add a trigger that runs it every few hours. Run the standard mode (with outreach) once a day.

Mac / Linux (cron):

```bash
crontab -e
# Fast poll every 2 hours:
0 */2 * * * cd /path/to/EarlyBird && python job_pipeline_full.py --fresh >> logs/pipeline_log.txt 2>&1
# Full run with outreach each morning at 8:
0 8 * * * cd /path/to/EarlyBird && python job_pipeline_full.py >> logs/pipeline_log.txt 2>&1
```

## Notes

- LinkedIn and Indeed scraping (JobSpy) is off by default because it breaks on anti-bot measures and conflicts with those sites' terms. Enabling it in `config.py` is at your own discretion.
- Never commit `.env`, `token.json`, `credentials.json`, or `*.xlsx` files. All are listed in `.gitignore`.
- The Render free tier sleeps after a period of inactivity. The first request after it sleeps takes around 30 seconds to wake the service.

## Roadmap

- Resume-to-job matching using embeddings
- Daily digest summarizing each morning's run
- Wider default watchlist and Ashby coverage

## License

MIT
