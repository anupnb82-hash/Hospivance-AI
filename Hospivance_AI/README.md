# Hospivance AI – AI-Powered Hospital Bottleneck Prediction System

**See the Bottleneck Before It Happens.**

Hospivance AI is an intelligent hospital operations dashboard and clinical decision support system that forecasts patient admissions, bed occupancy kinetics, and department-level overcrowding risk using machine learning (Random Forest regression) trained on chronological historical hospital data.

> ⚠️ **Synthetic Data & Clinical Notice**:
> This project uses **100% synthetic, non-PHI demonstration data**. It is engineered for healthcare capacity management, surge planning, and hospital resource optimization. It does **not** make clinical diagnoses or treatment decisions and must not be used as a medical device.

---

## Completed Features

1. **AI-Based Patient Admission Forecasting**: Machine learning pipeline trained on historical synthetic hospital data using strict chronological splitting (no data leakage).
2. **Multi-Horizon Predictions**: Interactive forecasting for **24 hours (next day)**, **3 days**, and **7 days** with 95% confidence intervals ($\pm 1.96 \times \text{RMSE}$).
3. **Hospital Bed Availability Monitoring**: Real-time matrix of total beds (395 across 6 units), occupied, available, sanitizing/turnover, and admission-ready census with 14-day historical curves.
4. **Department-Wise Overcrowding Analysis**: In-depth 30-day series tracking admission vs. discharge velocity, net backlog flow, average wait times, and ambulance diversions.
5. **Low, Moderate, and High Risk Alerts**: Automated threshold detection (`LOW <75%`, `MODERATE 75–89%`, `HIGH ≥90%`) with one-click charge nurse acknowledgment and emergency surge drill simulation.
6. **AI-Generated Resource Allocation Recommendations**: Actionable operational interventions covering Float Pool Staffing, ICU Step-Down reviews, Elective Surgery Buffering, and Morning Discharge Acceleration. Powered by Google Gemini API / OpenAI API with a clinical decision support heuristic fallback.
7. **Historical Admission Analytics & ML Scorecard**: 90-day seasonal trends, day-of-week surge patterns, holdout validation metrics (MAE, RMSE, R², MAPE), and feature importance ranking.
8. **Interactive Healthcare Dashboard**: Built with React.js, Vite, and custom responsive SVG data visualizations in a clean navy blue (`#0f172a`), white (`#ffffff`), and teal (`#0d9488`) healthcare design system.
9. **Functional Frontend-Backend Integration**: Robust REST API client with environment-driven proxy configuration.
10. **Working REST Endpoints**: 16 fully functional endpoints covering KPIs, predictions, bed tracking, alerts, analytics, reports, FHIR, and organizer hooks.
11. **Database Integration**: Multi-backend support featuring automatic PostgreSQL connectivity (`docker compose`) with seamless automatic SQLite fallback (`data/hospivance.db`).
12. **Synthetic Hospital Dataset Generator**: Generates 730 days (4,380 records) of realistic department-day kinetics including seasonal flu cycles, weekday/weekend spikes, and temperature factors.
13. **Model Training & Evaluation Pipeline**: Evaluates real model performance using chronological train/test splitting and exports artifacts to `backend/ml/artifacts/`.
14. **Real-Time Dashboard Updates**: WebSocket feed (`/ws/live`) streaming live simulated patient arrivals and bed census fluctuations with live pulsing heartbeat indicator.

---

## Project Architecture & Directory Map

```text
Hospivance_AI/
├── .env                              # Root environment variables
├── .env.example                      # Root environment example template
├── .gitignore                        # Git exclusion rules
├── docker-compose.yml                # Optional PostgreSQL 16 container
├── HACKATHON_INTEGRATION.md          # Guide for organizer REST APIs & hosted instances
├── README.md                         # Comprehensive documentation
├── data/
│   ├── hospital_daily.csv            # 730-day synthetic hospital dataset
│   └── hospivance.db                 # SQLite database file
├── backend/
│   ├── .env                          # Backend environment variables
│   ├── .env.example                  # Backend template
│   ├── requirements.txt              # Python dependencies
│   ├── app/
│   │   ├── main.py                   # FastAPI app, CORS, WebSocket, and lifecycle
│   │   ├── config.py                 # Pydantic/dotenv configuration loader
│   │   ├── database/
│   │   │   ├── session.py            # Dual PostgreSQL / SQLite session manager
│   │   │   ├── models.py             # Dual SQLAlchemy / SQLite ORM models
│   │   │   ├── seed.py               # Database seeder (departments, alerts, encounters)
│   │   │   └── sqlite_adapter.py     # Pure-Python SQLite query builder
│   │   ├── routes/
│   │   │   ├── dashboard.py          # GET /api/dashboard
│   │   │   ├── beds.py               # GET /api/beds
│   │   │   ├── departments.py        # GET /api/departments
│   │   │   ├── predict.py            # POST /api/predict
│   │   │   ├── alerts.py             # GET /api/alerts, POST /api/alerts/{id}/ack, POST /api/alerts/simulate
│   │   │   ├── analytics.py          # GET /api/analytics, POST /api/analytics/retrain
│   │   │   ├── recommendations.py    # POST /api/recommendations
│   │   │   ├── reports.py            # GET /api/reports/export
│   │   │   ├── fhir.py               # GET /api/fhir/metadata, GET /api/fhir/Bundle/encounters
│   │   │   └── organizer.py          # GET /api/organizer/status, POST /api/organizer/test, POST /api/organizer/sync
│   │   └── services/
│   │       ├── forecast_service.py   # Forecast orchestration
│   │       ├── alert_service.py      # Threshold alert monitoring and ack
│   │       ├── llm_service.py        # Gemini API / OpenAI API / Heuristic fallback
│   │       ├── fhir_service.py       # HL7 FHIR R4 Bundle generator
│   │       └── organizer_sync.py     # External hackathon REST synchronizer
│   └── ml/
│       ├── generate_data.py          # Synthetic dataset generator
│       ├── features.py               # Lag, rolling window, calendar feature pipeline
│       ├── models.py                 # Pure-Python Random Forest ensemble fallback
│       ├── train.py                  # Chronological train/test split and training
│       ├── inference.py              # Multi-horizon forecast and confidence bounds
│       └── artifacts/
│           ├── model.joblib          # Trained ML model weights
│           └── metrics.json          # Scorecard metrics (MAE, RMSE, R², MAPE)
├── frontend/
│   ├── .env                          # Frontend environment variables
│   ├── .env.example                  # Frontend template
│   ├── package.json                  # Node.js dependencies
│   ├── vite.config.js                # Vite development server and backend proxy
│   ├── index.html                    # HTML shell
│   └── src/
│       ├── main.jsx                  # React DOM mount point
│       ├── App.jsx                   # Main layout and tab navigator
│       ├── index.css                 # Healthcare navy/white/teal design system
│       ├── api/
│       │   └── client.js             # REST API client
│       ├── components/
│       │   ├── Navbar.jsx            # Top navigation bar
│       │   ├── Sidebar.jsx           # 8-tab sidebar navigation
│       │   ├── StatCard.jsx          # KPI card component
│       │   ├── RiskBadge.jsx         # LOW, MODERATE, HIGH risk badges
│       │   ├── LiveStatusBadge.jsx   # WebSocket pulsing live feed indicator
│       │   └── Charts.jsx            # SVG line, bar, and circular gauge charts
│       └── pages/
│           ├── DashboardOverview.jsx # Command Center overview
│           ├── PredictionsPage.jsx   # 24h, 3d, 7d admission predictions
│           ├── BedMonitoringPage.jsx # Bed census and 14d occupancy curves
│           ├── DepartmentOvercrowdingPage.jsx # 30d department overcrowding series
│           ├── AlertsPage.jsx        # Operational alerts and surge drill simulator
│           ├── RecommendationsPage.jsx # AI clinical resource recommendations
│           ├── AnalyticsPage.jsx     # 90d analytics and ML model evaluation
│           └── SettingsReportsPage.jsx # FHIR export, JSON report, organizer hook
└── tests/
    └── test_backend.py               # 16-endpoint end-to-end automated test suite
```

---

## Windows VS Code Installation & Execution Guide

Follow these exact commands in **Visual Studio Code** on Windows.

### Prerequisites
1. **Python 3.11 or 3.12** installed ([python.org](https://www.python.org/downloads/)). Check **"Add Python to PATH"** during installation.
2. **Node.js 18 or 20+** installed ([nodejs.org](https://nodejs.org/)).
3. **Visual Studio Code** installed.

---

### Step 1: Open Project in VS Code
Open VS Code, press `Ctrl + O` (or `File -> Open Folder...`), and select the unzipped `Hospivance_AI` folder.

---

### Step 2: Configure Environment Variables
In VS Code, open a new Terminal (`Ctrl + ~` or `Terminal -> New Terminal`) and run:

**PowerShell:**
```powershell
Copy-Item .env.example .env
Copy-Item .env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

**Command Prompt (cmd):**
```cmd
copy .env.example .env
copy .env.example backend\.env
copy frontend\.env.example frontend\.env
```

*(Optional: If you have a Google Gemini API key, edit `backend/.env` and set `GEMINI_API_KEY=your_key_here`. If left empty, Hospivance AI automatically uses the intelligent hospital operations heuristic fallback engine).*

---

### Step 3: Set Up and Run the Python Backend

In the VS Code Terminal:

```powershell
# 1. Navigate to backend
cd backend

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# (If PowerShell gives an execution policy error, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
# On Windows Command Prompt (CMD):
# .venv\Scripts\activate.bat

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. (Optional) Run the training pipeline explicitly:
python -m ml.train

# 6. Start the FastAPI backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend is now live at:
- **API Server**: http://127.0.0.1:8000
- **Interactive Swagger Docs**: http://127.0.0.1:8000/docs
- **Health Endpoint**: http://127.0.0.1:8000/health

---

### Step 4: Set Up and Run the React Frontend

Open a **second terminal tab** in VS Code (`Ctrl + Shift + 5` or click the `+` icon in the terminal panel):

```powershell
# 1. Navigate to frontend
cd frontend

# 2. Install Node.js dependencies
npm install

# 3. Start Vite development server
npm run dev
```

Open your browser at:
- **Hospivance AI Command Center**: http://localhost:5173

---

### Step 5: Run Automated Tests
In a terminal tab with the virtual environment activated:

```powershell
cd Hospivance_AI
python tests/test_backend.py
```
*Expected output: All 16 backend test suites pass with 100% success.*

---

## REST API Specification

| Method | Path | Role & Functionality |
| :--- | :--- | :--- |
| `GET` | `/health` | Health status, database connection, model readiness, LLM flag |
| `GET` | `/api/dashboard` | Executive KPIs, 7-day trend, department capacity grid |
| `GET` | `/api/beds` | Bed availability matrix, 14-day history, discharge targets |
| `GET` | `/api/departments` | 30-day time series, net patient flow, ambulance diversions |
| `POST` | `/api/predict` | Multi-horizon admissions forecast (`1`, `3`, or `7` days) |
| `GET` | `/api/alerts` | Active bottleneck alerts filtered by severity (`HIGH`, `MODERATE`, `LOW`) |
| `POST` | `/api/alerts/{id}/ack` | Charge nurse / bed coordinator acknowledgment |
| `POST` | `/api/alerts/simulate` | Trigger emergency surge drill alert |
| `GET` | `/api/analytics` | 90-day seasonal admissions, day-of-week patterns, ML scorecard |
| `POST` | `/api/analytics/retrain` | Triggers explicit model retraining on chronological dataset |
| `POST` | `/api/recommendations` | AI-generated resource allocation briefings (Gemini / Heuristics) |
| `GET` | `/api/reports/export` | Download full hospital operations report as JSON |
| `GET` | `/api/fhir/metadata` | HL7 FHIR R4 CapabilityStatement |
| `GET` | `/api/fhir/Bundle/encounters`| Synthetic FHIR R4 Encounter bundle |
| `GET` | `/api/organizer/status` | Hackathon organizer API hook status |
| `POST` | `/api/organizer/test` | Ping external organizer endpoint |
| `POST` | `/api/organizer/sync` | Synchronize external organizer feeds |
| `WS` | `/ws/live` | Simulated real-time occupancy WebSocket stream |

---

## Risk Threshold Classification

Hospivance AI classifies hospital operational risk according to standard clinical capacity guidelines:

| Occupancy Rate | Risk Level | Operational Protocol |
| :---: | :---: | :--- |
| **< 75%** | **LOW** | Normal operations; standard patient flow and discharge schedules. |
| **75% – 89%** | **MODERATE** | Pre-surge alert; accelerate morning discharges, notify on-call float nurses. |
| **≥ 90%** | **HIGH** | Critical bottleneck; initiate ICU step-down review, buffer elective surgeries, activate fast-track triage. |
