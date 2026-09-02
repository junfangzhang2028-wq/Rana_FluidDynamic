# Aqueous Outflow Web Calculator — Python Review Package

This package contains the minimum source files needed to review and run the
browser-based aqueous outflow calculator. It intentionally excludes the paper
figures, presentation files, historical Angular frontend, and batch-analysis
outputs.

## Architecture

The calculator is a small Python HTTP service:

1. `local_web_calculator.py` serves the standalone HTML/CSS/JavaScript user
   interface.
2. The browser sends simulation inputs to `POST /api/solve`.
3. Python calls the numerical model in the `offline` package.
4. Results are returned as JSON and plotted by the browser.

The current implementation therefore needs a Python runtime. Unlike the
existing VisOCT Acquisition Time Estimator, its calculation is not a short
JavaScript formula that can simply be pasted into a Google Sites custom embed.

## Included files

- `local_web_calculator.py` — standalone interface and API endpoint
- `m-johnson2-aqueous-outflow-8fb729748300_Modified/offline/solver.py` — core
  numerical solver
- `m-johnson2-aqueous-outflow-8fb729748300_Modified/offline/gauss_seidel.py` —
  iterative linear solver
- `m-johnson2-aqueous-outflow-8fb729748300_Modified/offline/outputs_trial.py` —
  model input/output wrappers used by the web API
- `requirements.deploy.txt` — Python dependencies for the web service
- `Dockerfile` — container configuration suitable for Cloud Run or another
  container host

## Run locally

Python 3.12 is recommended.

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.deploy.txt
python local_web_calculator.py 4300
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.deploy.txt
python local_web_calculator.py 4300
```

Then open `http://127.0.0.1:4300/`.

## Hosting options

The smallest-change option is to host the existing Python service on Cloud
Run, another container platform, or a company-managed Python server. Once it
has a public HTTPS URL, Google Sites can include it as a full-page embed.

It is also technically possible to eliminate the server by porting the solver
to JavaScript or WebAssembly. That would require translating and validating
the NumPy/SciPy-dependent numerical implementation and checking its results
against the Python reference model.

## Deployment behavior

When the `PORT` environment variable is set, `local_web_calculator.py` listens
on `0.0.0.0:$PORT`, does not open a desktop browser, and exposes `GET /healthz`.
Those behaviors are intended for Cloud Run and similar managed services.
