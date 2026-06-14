# Interactive App — In-Silico Cancer Vaccine Designer

A live ETL runner + data explorer for the vaccine-design pipeline. A FastAPI backend
serves a single-file React app, exposes the pipeline's output files, and streams a live
pipeline run as Server-Sent Events.

## Run it

```bash
# from the project root, with the project venv active
source .venv/bin/activate
pip install fastapi uvicorn            # one-time (also in requirements.txt)

uvicorn server:app --port 8000
# open http://localhost:8000
```

The server serves the frontend itself, so everything is one origin — just open the URL.

## How it works

- **Explorer mode (default):** on load, the app reads the existing output files
  (`data/candidate_neoantigens.csv`, `data/reference_points.csv`, `data/vaccine_design.txt`)
  via the data endpoints and visualizes them across the six pipeline stages.
- **Run mode:** click **Run Pipeline**. The backend shells out to
  `scripts/run_pipeline.py` and streams its stdout line-by-line over SSE. The app parses
  the structured `STAGE:` events to drive the live stepper, then reloads Explorer mode with
  the fresh results. (The run sets `VAXSIM_DEMO=1` so it's slow enough to watch.)

If the backend is unreachable, the app loads in a graceful empty state ("No data yet —
click Run Pipeline").

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/` | the React app (`index.html`) |
| GET | `/app.jsx` | React source (transpiled in-browser by Babel) |
| GET | `/data/candidates` | `candidate_neoantigens.csv` as JSON |
| GET | `/data/references` | `reference_points.csv` as JSON (PCA scatter) |
| GET | `/data/construct` | `vaccine_design.txt` as raw text |
| GET | `/data/status` | `{ has_results, last_run }` |
| POST | `/pipeline/run` | SSE stream of pipeline stdout |

> Note vs. the original brief: a fifth endpoint, `GET /data/references`, was added so the
> Stage-5 embedding scatter can place the 32 reference epitopes in the **same PCA space** as
> the candidates (PCA is fit on the reference epitopes; candidates are projected onto it).
> This keeps the plot correct across re-runs instead of relying on a brittle hardcoded lookup.

## Notes

- **Offline-capable.** React and Babel are vendored under `vendor/` and served same-origin,
  and the layout uses hand-written CSS (no Tailwind CDN) — so the app loads with no internet.
  The only external request is Google Fonts (`@import`); if it's blocked, the app falls back to
  system serif/mono fonts and still works. Good insurance for flaky conference wifi.
- No database, no auth, no external **data/API** calls — all data is the pipeline's own output.
- A failed/partial run is shown as an error (the active stage turns red); only a clean run
  marks all six stages complete. Closing the tab mid-run terminates the pipeline subprocess.
- The `STAGE:` print convention emitted by `scripts/run_pipeline.py` is documented at the top
  of that file.
