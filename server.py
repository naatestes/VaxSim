"""Minimal FastAPI backend for the In-Silico Cancer Vaccine Designer app.

Serves the React frontend and the pipeline's data files, and streams a live
pipeline run as Server-Sent Events.

Run:
    uvicorn server:app --port 8000
    # then open http://localhost:8000

Endpoints:
    GET  /                  -> the React app (index.html)
    GET  /app.jsx           -> the React source (transpiled in-browser by Babel)
    GET  /data/candidates   -> candidate_neoantigens.csv as JSON array
    GET  /data/references    -> reference_points.csv as JSON array (for the PCA plot)
    GET  /data/construct     -> vaccine_design.txt as raw text
    GET  /data/status        -> { has_results, last_run }
    POST /pipeline/run       -> SSE stream of the pipeline's stdout, line by line
"""

from __future__ import annotations

import asyncio
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CANDIDATES_CSV = DATA / "candidate_neoantigens.csv"
REFERENCES_CSV = DATA / "reference_points.csv"
CONSTRUCT_TXT = DATA / "vaccine_design.txt"

app = FastAPI(title="In-Silico Cancer Vaccine Designer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # localhost-only tool; no auth, no sensitive data
    allow_methods=["*"],
    allow_headers=["*"],
)

_NUMERIC = {"binding", "similarity", "composite", "pca_x", "pca_y", "mut_pos_in_peptide"}


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            for k in list(row):
                if k in _NUMERIC and row[k] not in (None, ""):
                    try:
                        row[k] = float(row[k])
                    except ValueError:
                        pass
            out.append(row)
    return out


# ---- frontend ----------------------------------------------------------------
@app.get("/")
def index():
    return FileResponse(ROOT / "index.html")


@app.get("/app.jsx")
def appjsx():
    return FileResponse(ROOT / "app.jsx", media_type="text/babel")


# ---- data --------------------------------------------------------------------
@app.get("/data/candidates")
def candidates():
    return JSONResponse(_read_csv(CANDIDATES_CSV))


@app.get("/data/references")
def references():
    return JSONResponse(_read_csv(REFERENCES_CSV))


@app.get("/data/construct")
def construct():
    if not CONSTRUCT_TXT.exists():
        return PlainTextResponse("", status_code=200)
    return PlainTextResponse(CONSTRUCT_TXT.read_text())


@app.get("/data/status")
def status():
    if CANDIDATES_CSV.exists():
        ts = datetime.fromtimestamp(CANDIDATES_CSV.stat().st_mtime, tz=timezone.utc)
        return {"has_results": True, "last_run": ts.isoformat()}
    return {"has_results": False, "last_run": None}


# ---- live run (SSE) ----------------------------------------------------------
@app.post("/pipeline/run")
async def run_pipeline():
    async def event_stream():
        env = {**os.environ, "VAXSIM_DEMO": "1", "PYTHONUNBUFFERED": "1"}
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(ROOT / "scripts" / "run_pipeline.py"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(ROOT),
            env=env,
        )
        try:
            while True:
                raw = await proc.stdout.readline()
                if not raw:
                    break
                line = raw.decode(errors="replace").rstrip("\n")
                yield f"data: {line}\n\n"
        finally:
            await proc.wait()
        yield f"data: STAGE:done:{proc.returncode}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )
