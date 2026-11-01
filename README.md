# Hospivance AI — AI-Powered Hospital Bottleneck Prediction System

**See the Hospital Bottleneck Before It Happens.**

Hospivance AI is a full-stack hospital operations command center and predictive analytics platform that forecasts patient admission surges, monitors real-time bed saturation across specialized clinical units, detects department overcrowding risks, and generates AI-backed resource allocation protocols.

> **Synthetic Data & Clinical Disclaimer:**
>
> This repository uses **100% synthetic, non-PHI department-day hospital telemetry** (4,380 records across 730 days) generated for operational capacity modeling and research demonstrations. No real patient names, Medical Record Numbers (MRNs), or Protected Health Information (PHI) are stored or processed. All forecasts and recommendations are operational planning signals and must not be used for clinical diagnosis or medical treatment decisions.

## Key Features

* **Multi-Horizon Patient Surge Forecasting**: Predicts daily patient admissions across **24-hour (next day)**, **3-day**, and **7-day** horizons with 95% confidence intervals ($\pm 1.96 \times \text{RMSE}$).

* **Leakage-Free Machine Learning Pipeline**: Trained using a **Random Forest Regressor** on a strict chronological train/test split (`80%` historical training, `20%` future holdout) with lag features (`lag_1`, `lag_2`, `lag_3`, `lag_7`), rolling 7-day statistics, seasonal respiratory intensity, temperature, and calendar indicators.

* **Real-Time Bed Availability Matrix**: Monitors **395 total beds** across 6 hospital units (`Emergency Room`, `Intensive Care Unit (ICU)`, `General Ward`, `Pediatrics`, `Cardiology`, and `Surgery`), tracking occupied beds, sanitizing/turnover beds, admission-ready census, 14-day occupancy curves, and exact discharge targets needed to return below the 85% safety threshold.

* **Department Overcrowding Detection**: Analyzes 14-day, 30-day, and 60-day department throughput velocities, average ER door-to-provider wait times, ambulance diversions, and net patient backlog flow.

* **Automated Risk Categorization & Alerts**: Classifies operational saturation into **LOW (`< 75%`)**, **MODERATE (`75% – 89%`)**, and **HIGH (`>= 90%`)** risk bands, complete with one-click charge nurse acknowledgment and an interactive **Emergency Surge Drill Simulator**.

* **AI Resource Allocation Recommendations**: Integrates with **Google Gemini API** (`gemini-2.0-flash`) and **OpenAI API** (`gpt-4o-mini`) to generate executive operational briefings and prioritized clinical protocols (ICU step-down reviews, elective surgical buffering, float pool nurse deployment, and morning discharge lounge acceleration), backed by a deterministic **Clinical Heuristic Engine** when no API key is configured.

* **Simulated Live WebSocket Telemetry**: Streams real-time hospital bed census fluctuations over `/ws/live` with a live status indicator in the top navigation bar.

* **HL7 FHIR R4 & Hackathon Organizer Hooks**: Exports standard HL7 FHIR R4 `CapabilityStatement` and `Encounter` bundles (`/api/fhir/Bundle/encounters`) and includes a plug-and-play external REST API synchronization module (`/api/organizer/*`).

## Tech Stack

| Layer | Technologies | 
| ----- | ----- | 
| **Frontend** | React 18, Vite 5, Custom Responsive SVG Data Visualizations, Healthcare Design System (Navy `#0f172a`, White `#ffffff`, Teal `#0d9488`) | 
| **Backend API** | Python 3.11+, FastAPI, Uvicorn, Pydantic, WebSockets | 
| **Machine Learning** | Scikit-learn (`RandomForestRegressor` + Pure-Python Ensemble Fallback), Pandas, NumPy, Joblib | 
| **Database** | PostgreSQL 16 (`docker-compose.yml`) with automatic zero-config fallback to SQLite (`data/hospivance.db`) | 
| **Generative AI** | Google Gemini API (`google-generativeai`), OpenAI API (`openai`), Clinical Heuristic Fallback Engine v2.4 | 
| **Interoperability** | HL7 FHIR R4 (`Encounter` & `CapabilityStatement`), REST JSON Report Exporter | 

## Machine Learning Evaluation Scorecard

The forecasting pipeline is evaluated strictly on out-of-time chronological holdout data (`870` department-day records from `2026-06-09` to `2026-10-31`) after training on `3,468` historical department-day records (`2024-11-08` to `2026-06-08`):

| Metric | Holdout Score | Description | 
| ----- | ----- | ----- | 
| **Algorithm** | `RandomForestRegressor` | 100 trees, max depth 12, chronological lag & rolling window pipeline | 
| **Validation Strategy** | Chronological Split | Strict temporal cutoff (`2026-06-09`) — zero future lookahead leakage | 
| $R^2$ **Score** | **0.9063** | 90.63% of variance explained on unseen future holdout days | 
| **Mean Absolute Error (MAE)** | **5.485 patients** | Average daily admission prediction error per department | 
| **Root Mean Squared Error (RMSE)** | **7.510 patients** | Used to compute 95% confidence bounds ($\pm 1.96 \times \text{RMSE} / 2$) | 
| **MAPE** | **30.29%** | Mean Absolute Percentage Error across all 6 clinical units | 

## Repository Structure

```
Hospivance_AI/
├── .env.example                      # Root environment variable template
├── .gitignore                        # Git ignore rules
├── docker-compose.yml                # Optional PostgreSQL 16 container setup
├── HACKATHON_INTEGRATION.md          # Guide for plugging in external organizer APIs
├── README.md                         # Project documentation
├── data/
│   ├── hospital_daily.csv            # 730-day synthetic hospital dataset (4,380 rows)
│   └── hospivance.db                 # Auto-generated SQLite database
├── backend/
│   ├── .env.example                  # Backend environment template
│   ├── requirements.txt              # Python dependencies
│   ├── app/
│   │   ├── main.py                   # FastAPI entry point, CORS, lifecycle, WebSocket /ws/live
│   │   ├── config.py                 # Environment configuration loader
│   │   ├── database/
│   │   │   ├── session.py            # PostgreSQL / SQLite dual session manager
│   │   │   ├── models.py             # Department, AdmissionRecord, Alert, Encounter models
│   │   │   ├── seed.py               # Automated database seeder on first boot
│   │   │   └── sqlite_adapter.py     # Zero-dependency SQLite query adapter
│   │   ├── routes/
│   │   │   ├── dashboard.py          # GET /api/dashboard
│   │   │   ├── beds.py               # GET /api/beds
│   │   │   ├── departments.py        # GET /api/departments
│   │   │   ├── predict.py            # POST /api/predict (1, 3, or 7-day horizons)
│   │   │   ├── alerts.py             # GET /api/alerts, POST /ack, POST /simulate
│   │   │   ├── analytics.py          # GET /api/analytics, POST /retrain
│   │   │   ├── recommendations.py    # POST /api/recommendations
│   │   │   ├── reports.py            # GET /api/reports/export
│   │   │   ├── fhir.py               # GET /api/fhir/metadata, GET /api/fhir/Bundle/encounters
│   │   │   └── organizer.py          # GET /api/organizer/status, POST /test, POST /sync
│   │   └── services/
│   │       ├── forecast_service.py   # Multi-horizon ML forecast orchestration
│   │       ├── alert_service.py      # Risk threshold evaluation & alert lifecycle
│   │       ├── llm_service.py        # Gemini / OpenAI / Clinical Heuristic engine
│   │       ├── fhir_service.py       # HL7 FHIR R4 resource serializer
│   │       └── organizer_sync.py     # External REST API connector
│   └── ml/
│       ├── generate_data.py          # 730-day synthetic hospital data generator
│       ├── features.py               # Lag, rolling window, and one-hot feature builder
│       ├── models.py                 # Ensemble regression fallback
│       ├── train.py                  # Chronological training & evaluation script
│       ├── inference.py              # Multi-horizon admission & occupancy predictor
│       └── artifacts/
│           ├── model.joblib          # Serialized trained model & feature metadata
│           └── metrics.json          # Holdout evaluation scorecard
├── frontend/
│   ├── .env.example                  # Frontend environment template
│   ├── package.json                  # Node dependencies & Vite scripts
│   ├── vite.config.js                # Vite server & /api + /ws proxy config
│   ├── index.html                    # Application HTML shell
│   └── src/
│       ├── main.jsx                  # React entry point
│       ├── App.jsx                   # Application shell & view router
│       ├── index.css                 # Navy, White, and Teal healthcare styling
│       ├── api/
│       │   └── client.js             # Fetch wrapper for all REST & WebSocket endpoints
│       ├── components/
│       │   ├── Sidebar.jsx           # Left navigation bar
│       │   ├── Navbar.jsx            # Header with live WebSocket telemetry pill
│       │   ├── StatCard.jsx          # KPI metric card
│       │   ├── RiskBadge.jsx         # LOW, MODERATE, HIGH status pill
│       │   ├── LiveStatusBadge.jsx   # Real-time WebSocket stream consumer
│       │   └── Charts.jsx            # Responsive SVG trend line, bar, and gauge charts
│       └── pages/
│           ├── DashboardOverview.jsx # Executive Command Center
│           ├── PredictionsPage.jsx   # 24h, 3d, and 7d surge forecasting
│           ├── BedMonitoringPage.jsx # Bed census matrix & 14d occupancy curves
│           ├── DepartmentOvercrowdingPage.jsx # 30d overcrowding & net flow analysis
│           ├── AlertsPage.jsx        # Bottleneck alerts & surge drill trigger
│           ├── RecommendationsPage.jsx # AI resource allocation briefings
│           ├── AnalyticsPage.jsx     # 90d seasonality & ML model scorecard
│           └── SettingsReportsPage.jsx # FHIR export, JSON report, & organizer sync
└── tests/
    └── test_backend.py               # End-to-end automated test suite (16 endpoints)

```

## Quick Start & Installation

### Prerequisites

* **Python 3.11 or 3.12** ([Download Python](https://www.python.org/downloads/))

* **Node.js 18+** and **npm** ([Download Node.js](https://nodejs.org/))

* **Docker Desktop** *(Optional — only needed if you prefer PostgreSQL over the automatic SQLite database)*

### 1. Clone the Repository

```
git clone https://github.com/your-username/hospivance-ai.git
cd hospivance-ai

```

### 2. Configure Environment Variables

**Windows (PowerShell):**

```
Copy-Item .env.example .env
Copy-Item .env.example backend\.env
Copy-Item frontend\.env.example frontend\.env

```

**macOS / Linux:**

```
cp .env.example .env
cp .env.example backend/.env
cp frontend/.env.example frontend/.env

```

*(Optional)* To enable live **Google Gemini** or **OpenAI** explanations, add your key to `backend/.env`:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

```

If left blank, Hospivance AI automatically uses its built-in **Clinical Operations Heuristic Engine**.

### 3. Start the Backend Server (Terminal 1)

**Windows (PowerShell):**

```
cd backend
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```

**macOS / Linux:**

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

```

On first boot, the backend automatically:

1. Generates `data/hospital_daily.csv` (4,380 records across 6 departments) if missing.

2. Initializes the database schema (`PostgreSQL` or `data/hospivance.db` via `SQLite`) and seeds departments, alerts, and synthetic FHIR encounters.

3. Trains and evaluates the Random Forest model (`backend/ml/artifacts/model.joblib`) if not already present.

* **Backend API Base URL**: `http://127.0.0.1:8000`

* **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`

* **Health Check**: `http://127.0.0.1:8000/health`

### 4. Start the React Frontend (Terminal 2)

Open a second terminal window from the project root:

```
cd frontend
npm install
npm run dev

```

* **Dashboard URL**: `http://localhost:5173`

## Running Tests & Retraining the ML Model

To run the automated end-to-end backend test suite verifying all 16 endpoints:

```
python tests/test_backend.py

```

To explicitly regenerate the synthetic dataset and retrain the machine learning model from the command line:

```
cd backend
python -m ml.generate_data
python -m ml.train

```

## REST API Reference

| Method | Endpoint | Description | 
| ----- | ----- | ----- | 
| `GET` | `/health` | Service liveness, active database engine, ML readiness, and LLM flags | 
| `GET` | `/api/dashboard` | Hospital KPIs, 7-day admission trend + 24h forecast, and department risk grid | 
| `GET` | `/api/beds` | Department bed availability matrix, sanitizing counts, and 14-day occupancy curves | 
| `GET` | `/api/departments` | 14/30/60-day department time series, wait times, diversions, and net flow | 
| `POST` | `/api/predict` | Multi-horizon admission & occupancy predictions (`horizon_days`: `1`, `3`, or `7`) | 
| `GET` | `/api/alerts` | List active and resolved overcrowding alerts (`?risk_level=HIGH|MODERATE|LOW`) | 
| `POST` | `/api/alerts/{id}/ack` | Acknowledge an operational bottleneck alert | 
| `POST` | `/api/alerts/simulate` | Trigger a simulated emergency surge drill alert | 
| `GET` | `/api/analytics` | 90-day day-of-week seasonality, department volumes, and ML evaluation scorecard | 
| `POST` | `/api/analytics/retrain` | Retrain the Random Forest pipeline on the chronological dataset | 
| `POST` | `/api/recommendations` | Generate AI resource allocation briefing and prioritized protocols | 
| `GET` | `/api/reports/export` | Download a comprehensive JSON hospital operations report | 
| `GET` | `/api/fhir/metadata` | HL7 FHIR R4 `CapabilityStatement` | 
| `GET` | `/api/fhir/Bundle/encounters` | HL7 FHIR R4 `Bundle` of synthetic inpatient and ER `Encounter` resources | 
| `GET` | `/api/organizer/status` | Check external hackathon organizer API configuration | 
| `POST` | `/api/organizer/test` | Test connectivity to the configured organizer REST API | 
| `POST` | `/api/organizer/sync` | Synchronize external organizer hospital feeds | 
| `WS` | `/ws/live` | Real-time simulated occupancy WebSocket stream | 

## Risk Band Thresholds

| Occupancy Rate | Risk Level | Operational Protocol | 
| ----- | ----- | ----- | 
| **< 75%** | `LOW` | Normal clinical flow; standard admission and discharge operations. | 
| **75% – 89%** | `MODERATE` | Elevated utilization; prioritize morning discharge orders and prepare float pool nurses. | 
| **>= 90%** | `HIGH` | Critical bottleneck risk; initiate ICU step-down audits, buffer elective post-op ICU surgeries, and deploy fast-track ER triage staffing. | 

## Security & Privacy Architecture

* **Server-Side Secret Isolation**: All API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ORGANIZER_API_KEY`) reside strictly in `backend/.env` and are never exposed to browser `VITE_*` variables.

* **Zero PHI Footprint**: All database records and FHIR bundles carry `"is_synthetic": true` metadata flags.

## License

Released under the MIT License for educational, hackathon, and healthcare operations research purposes.
