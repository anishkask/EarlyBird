#!/usr/bin/env python3
"""
FastAPI backend server for EarlyBird.

Security model (no user accounts by design — every visitor uses their own key):
- The Anthropic API key is accepted per request, used only for that pipeline
  run, and never logged, written to disk, or stored in the run record.
- Pipeline results contain personal contact data, so each run is keyed by a
  high-entropy unguessable token (run_id). Knowing the token is the only way
  to read a run, which closes insecure-direct-object-reference access.
- Runs auto-expire after RESULT_TTL_SECONDS and the store is size-capped, so
  personal data never lingers in memory.
- Per-IP rate limiting and a concurrency cap bound abuse and resource
  exhaustion. Raw exceptions are logged server-side but never returned to
  clients.
"""
import os
import time
import secrets
import logging
import threading
from collections import deque
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Logging — never logs request bodies, so the API key is never written out.
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("earlybird.api")

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------
RESULT_TTL_SECONDS = 1800          # purge a run 30 min after it was created
MAX_RUNS_RETAINED = 100            # hard cap on stored runs (evict oldest)
MAX_CONCURRENT_RUNS = 3            # background pipeline threads at once
RATE_LIMIT_MAX = 5                 # runs allowed per IP ...
RATE_LIMIT_WINDOW = 900            # ... per this many seconds (15 min)

# Allowed browser origins (CORS). Override via env for self-hosting.
_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "https://earlybird-ashen.vercel.app,http://localhost:5173,http://localhost:3000",
    ).split(",")
    if o.strip()
]

# Allowed Host headers. Render injects its own host; "*" is acceptable only
# because we do not rely on the Host header for any security decision.
_ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]

app = FastAPI(title="EarlyBird API", docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=_ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=False,           # no cookies/auth — keep credentials off
    allow_methods=["GET", "POST"],     # only what we serve
    allow_headers=["Content-Type"],
    max_age=600,
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Attach defensive headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# ---------------------------------------------------------------------------
# In-memory state — never persisted to disk. Guarded by a lock because both
# request handlers and background threads mutate it.
# ---------------------------------------------------------------------------
_runs: dict = {}                   # run_id -> {status, results, error, created_at, timestamp}
_rate_buckets: dict = {}           # client_ip -> deque[timestamps]
_lock = threading.Lock()


def _now() -> float:
    return time.time()


def _purge_expired_locked():
    """Remove expired runs and enforce the size cap. Caller holds _lock."""
    cutoff = _now() - RESULT_TTL_SECONDS
    for rid in [rid for rid, r in _runs.items() if r.get("created_at", 0) < cutoff]:
        _runs.pop(rid, None)
    if len(_runs) > MAX_RUNS_RETAINED:
        # Evict oldest by created_at until under cap
        for rid, _ in sorted(_runs.items(), key=lambda kv: kv[1].get("created_at", 0))[
            : len(_runs) - MAX_RUNS_RETAINED
        ]:
            _runs.pop(rid, None)


def _active_run_count_locked() -> int:
    return sum(1 for r in _runs.values() if r.get("status") in ("queued", "running"))


def _client_ip(request: Request) -> str:
    """Best-effort client IP. Behind Render's proxy the real IP is the first
    entry of X-Forwarded-For; fall back to the socket peer."""
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _rate_limited_locked(ip: str) -> bool:
    """Sliding-window rate limit per IP. Caller holds _lock."""
    window_start = _now() - RATE_LIMIT_WINDOW
    bucket = _rate_buckets.setdefault(ip, deque())
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_MAX:
        return True
    bucket.append(_now())
    return False


# ---------------------------------------------------------------------------
# Request models with strict validation
# ---------------------------------------------------------------------------
class PipelineRequest(BaseModel):
    """Body of POST /run-pipeline. The API key is used for the run only."""
    anthropic_api_key: str = Field(..., min_length=20, max_length=200)
    hours: int = Field(72, ge=1, le=168)
    cold_outreach: bool = True
    cold_outreach_limit: int = Field(10, ge=1, le=25)
    target_locations: List[str] = Field(default_factory=list, max_length=25)
    role_keywords: List[str] = Field(default_factory=list, max_length=25)
    skills: List[str] = Field(default_factory=list, max_length=50)

    @field_validator("anthropic_api_key")
    @classmethod
    def _key_shape(cls, v: str) -> str:
        v = v.strip()
        # Reject obvious junk early; real validation happens at Anthropic.
        if not v.startswith("sk-ant-"):
            raise ValueError("invalid API key format")
        return v

    @field_validator("target_locations", "role_keywords", "skills")
    @classmethod
    def _bound_strings(cls, v: List[str]) -> List[str]:
        return [str(s)[:100] for s in v if s and str(s).strip()][:50]


class SettingsRequest(BaseModel):
    """Body of POST /settings. Validated but never persisted server-side."""
    anthropic_api_key: str = Field("", max_length=200)
    target_locations: List[str] = Field(default_factory=list, max_length=25)
    role_keywords: List[str] = Field(default_factory=list, max_length=25)
    skills: List[str] = Field(default_factory=list, max_length=50)
    school: str = Field("", max_length=200)


# ---------------------------------------------------------------------------
# Background pipeline execution
# ---------------------------------------------------------------------------
def _background_run(run_id: str, api_key: str, hours: int, cold_outreach: bool, cold_outreach_limit: int,
                    target_locations: List[str], role_keywords: List[str], skills: List[str]):
    """Run the pipeline in a worker thread. The api_key lives only in this
    frame for the duration of the run and is never stored in _runs."""
    with _lock:
        if run_id in _runs:
            _runs[run_id]["status"] = "running"
    try:
        from job_pipeline_full import run_pipeline_api
        results = run_pipeline_api(
            api_key=api_key,
            hours=hours,
            cold_outreach_enabled=cold_outreach,
            cold_outreach_limit=cold_outreach_limit,
            target_locations=target_locations,
            role_keywords=role_keywords,
            skills=skills,
        )
        with _lock:
            if run_id in _runs:
                _runs[run_id]["status"] = "complete"
                _runs[run_id]["results"] = results
    except Exception:
        # Log full detail server-side; expose only a generic message.
        logger.exception("Pipeline run %s failed", run_id)
        with _lock:
            if run_id in _runs:
                _runs[run_id]["status"] = "error"
                _runs[run_id]["error"] = "Pipeline run failed. Check your API key and try again."
    finally:
        api_key = None  # do not let the key linger in this frame


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    """Liveness probe used by the frontend and the hosting platform."""
    return {"status": "ok"}


@app.post("/run-pipeline")
async def run_pipeline(req: PipelineRequest, request: Request):
    """Start a pipeline run in a background thread and return its run_id.
    Enforces per-IP rate limiting and a global concurrency cap first."""
    ip = _client_ip(request)
    with _lock:
        _purge_expired_locked()
        if _rate_limited_locked(ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        if _active_run_count_locked() >= MAX_CONCURRENT_RUNS:
            raise HTTPException(status_code=429, detail="Server busy. Try again in a few minutes.")

        run_id = secrets.token_urlsafe(24)   # unguessable; the only handle to this run
        timestamp = datetime.now(timezone.utc).isoformat()
        _runs[run_id] = {
            "status": "queued",
            "results": None,
            "error": None,
            "created_at": _now(),
            "timestamp": timestamp,
        }

    # Start the worker outside the lock. The key is passed by value only.
    threading.Thread(
        target=_background_run,
        args=(run_id, req.anthropic_api_key, req.hours, req.cold_outreach, req.cold_outreach_limit,
              req.target_locations, req.role_keywords, req.skills),
        daemon=True,
    ).start()

    return {"run_id": run_id, "status": "queued", "timestamp": timestamp}


@app.get("/status/{run_id}")
async def get_status(run_id: str):
    """Report a run's lifecycle state: queued, running, complete, or error."""
    with _lock:
        _purge_expired_locked()
        run = _runs.get(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found or expired.")
        return {
            "run_id": run_id,
            "status": run["status"],
            "error": run.get("error"),
            "timestamp": run.get("timestamp"),
        }


@app.get("/results/{run_id}")
async def get_results(run_id: str):
    """Return a completed run's full results; 409 while still in progress."""
    with _lock:
        _purge_expired_locked()
        run = _runs.get(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found or expired.")
        if run["status"] != "complete":
            return JSONResponse(
                status_code=409,
                content={"error": f"Run is {run['status']}", "status": run["status"]},
            )
        return run["results"]


@app.post("/settings")
async def save_settings(req: SettingsRequest):
    """Validate settings for the session. Deliberately a no-op server-side:
    preferences live in the browser and are sent with each run request."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
