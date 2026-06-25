#!/usr/bin/env python3
"""
FastAPI backend server for EarlyBird.
Runs pipeline jobs in background threads and returns results as JSON.
API keys are never logged, stored to disk, or retained after a run finishes.
"""
import uuid
import threading
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="EarlyBird API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://earlybird-ashen.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory run store — never persisted to disk
# run_id -> {status, results, error, timestamp}
_runs: dict = {}


class PipelineRequest(BaseModel):
    anthropic_api_key: str
    hours: int = 72
    cold_outreach: bool = True
    cold_outreach_limit: int = 10
    target_locations: List[str] = []
    role_keywords: List[str] = []
    skills: List[str] = []


class SettingsRequest(BaseModel):
    anthropic_api_key: str = ""
    target_locations: List[str] = []
    role_keywords: List[str] = []
    skills: List[str] = []
    school: str = ""


def _background_run(
    run_id: str,
    api_key: str,
    hours: int,
    cold_outreach: bool,
    cold_outreach_limit: int,
):
    """Execute pipeline in a background thread. Discards api_key on completion."""
    _runs[run_id]["status"] = "running"
    try:
        from job_pipeline_full import run_pipeline_api
        results = run_pipeline_api(
            api_key=api_key,
            hours=hours,
            cold_outreach_enabled=cold_outreach,
            cold_outreach_limit=cold_outreach_limit,
        )
        _runs[run_id]["status"] = "complete"
        _runs[run_id]["results"] = results
    except Exception as e:
        _runs[run_id]["status"] = "error"
        _runs[run_id]["error"] = str(e)
    finally:
        api_key = None  # ensure key does not linger


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/run-pipeline")
async def run_pipeline(req: PipelineRequest):
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().isoformat() + "Z"
    _runs[run_id] = {
        "status": "queued",
        "timestamp": timestamp,
        "results": None,
        "error": None,
    }

    api_key = req.anthropic_api_key

    t = threading.Thread(
        target=_background_run,
        args=(run_id, api_key, req.hours, req.cold_outreach, req.cold_outreach_limit),
        daemon=True,
    )
    t.start()

    return {"run_id": run_id, "status": "queued", "timestamp": timestamp}


@app.get("/status/{run_id}")
async def get_status(run_id: str):
    if run_id not in _runs:
        return {"run_id": run_id, "status": "not_found"}
    run = _runs[run_id]
    return {
        "run_id": run_id,
        "status": run["status"],
        "error": run.get("error"),
        "timestamp": run.get("timestamp"),
    }


@app.get("/results/{run_id}")
async def get_results(run_id: str):
    if run_id not in _runs:
        return {"error": "Run not found", "status": "not_found"}
    run = _runs[run_id]
    if run["status"] != "complete":
        return {"error": f"Run is {run['status']}", "status": run["status"]}
    return run["results"]


@app.post("/settings")
async def save_settings(req: SettingsRequest):
    # Session-only — nothing persisted to disk
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
