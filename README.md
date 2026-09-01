# Rana Fluid Dynamic Model

This repository preserves two snapshots of an aqueous humor outflow modeling project:

- `m-johnson2-aqueous-outflow-8fb729748300_Original/`: original project snapshot
- `m-johnson2-aqueous-outflow-8fb729748300_Modified/`: modified snapshot with additional comparison data and presentation assets

The project models the human aqueous humor outflow system and includes:

- an offline numerical model written in Python
- a Flask backend API for solving the model
- an Angular frontend for interactive simulation

## Repository Layout

### Main snapshots

- `m-johnson2-aqueous-outflow-8fb729748300_Original/`
- `m-johnson2-aqueous-outflow-8fb729748300_Modified/`

### Key directories inside the modified snapshot

- `offline/`: core numerical model, solver, plotting, and analysis scripts
- `backend/aqbackend/`: Flask application and model-serving logic
- `frontend/`: Angular 6 web UI
- `aq-ui-dist/`: built deployment artifacts
- `ComparisonData/`: comparison datasets added in the modified version

### Key files inside the modified snapshot

- `backend/requirements.txt`: backend-specific Python requirements
- `backend/setup.py`: backend package definition
- `frontend/package.json`: frontend dependencies and scripts
- `bootstrap.sh`: starts backend and frontend for local development in Unix-like environments
- `build.sh`: builds backend wheel and frontend production bundle
- `update_server_backend.sh`: deployment helper for the backend

## Environment Notes

This is an older stack and appears to target:

- Python 3.6 or 3.7 era tooling
- Flask 1.0.x
- Angular CLI 6.x
- Node/npm versions compatible with Angular 6

The root-level `requirements.txt` in this repository is a convenience file aggregated from the backend and offline model dependencies. The original backend also keeps its own `backend/requirements.txt` and `Pipfile`.

## Python Setup

From the repository root:

```bash
python -m venv .venv
pip install -r requirements.txt
```

PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux activation:

```bash
source .venv/bin/activate
```

If you want to work directly with the packaged backend, you can also install from:

```bash
cd m-johnson2-aqueous-outflow-8fb729748300_Modified/backend
pip install -r requirements.txt
```

## Frontend Setup

From the modified snapshot:

```bash
cd m-johnson2-aqueous-outflow-8fb729748300_Modified/frontend
npm install
npm start
```

## Running The Project Locally

### Backend

The Flask app lives in:

`m-johnson2-aqueous-outflow-8fb729748300_Modified/backend/aqbackend`

A typical local run flow is:

```powershell
cd m-johnson2-aqueous-outflow-8fb729748300_Modified/backend
$env:FLASK_APP="aqbackend"
flask run -h localhost -p 5000
```

On Unix-like systems, the existing `bootstrap.sh` script shows the intended development workflow: backend on port `5000` and frontend on port `8000`.

### Frontend

```bash
cd m-johnson2-aqueous-outflow-8fb729748300_Modified/frontend
npm start
```

Note: `frontend/src/app/env.ts` currently points to the deployed API endpoint, not `localhost`. For full local end-to-end development, update that API URL to your local backend before launching the frontend.

## Core Model Files

The main numerical model logic is concentrated in:

- `offline/solver.py`
- `offline/outputs.py`
- `offline/gauss_seidel.py`

Equivalent packaged backend copies also exist in:

- `backend/aqbackend/solver.py`
- `backend/aqbackend/outputs.py`
- `backend/aqbackend/gauss_seidel.py`

The backend exposes a `/solve` endpoint that accepts simulation conditions and returns model results as JSON.

## Data And Assets

This repository includes several data and reference assets used by the model and UI, such as:

- CSV correlation tables
- injection/separation datasets
- JSON correlation files
- spreadsheets and presentation materials in the modified snapshot

Because some generated directories and cached files are also present in the project tree, the root `.gitignore` is configured to ignore common Python, Angular, and build artifacts going forward.

## Recommended Workflow

If you are using this repository as the main development base, prefer working from:

`m-johnson2-aqueous-outflow-8fb729748300_Modified/`

Use the original snapshot as a historical baseline for comparison.

## Deploying the Local Web Calculator

The root-level `local_web_calculator.py` can run locally or as a public
container service. When the `PORT` environment variable is present, it binds
to `0.0.0.0`, uses that port, and does not try to open a desktop browser. The
service also exposes `GET /healthz` for deployment health checks.

### Local deployment-mode check

```powershell
$env:PORT="8080"
python local_web_calculator.py
```

Then open `http://127.0.0.1:8080/` and verify that
`http://127.0.0.1:8080/healthz` returns `{"status":"ok"}`.

### Container build

```bash
docker build -t aqueous-outflow-calculator .
docker run --rm -p 8080:8080 aqueous-outflow-calculator
```

### Google Cloud Run

After selecting a Google Cloud project and enabling billing, deploy from the
repository root:

```bash
gcloud run deploy aqueous-outflow-calculator \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

Cloud Run prints a public HTTPS service URL after deployment. That URL can be
added to Google Sites as a full-page embed or navigation link. Deployment is
intentionally not automated by this repository because it requires choosing
the owning Google Cloud project, billing account, region, and public-access
policy.
