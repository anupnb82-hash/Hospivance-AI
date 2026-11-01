# Where to plug in organizer APIs and hosted apps

Hospivance AI is built so a hackathon organizer can hand you a URL and a key and you can connect without rewriting the product.

This demo uses **synthetic hospital data only**. It does not make clinical decisions.

## 1. Organizer gives you a REST API

Edit **one file**: `backend/.env` (copy from `.env.example`).

Set:

```
ORGANIZER_API_BASE_URL=https://api.example-hackathon.com
ORGANIZER_API_KEY=the-key-they-gave-you
ORGANIZER_API_AUTH_HEADER=Authorization
ORGANIZER_API_AUTH_SCHEME=Bearer
ORGANIZER_PATH_ADMISSIONS=/admissions
ORGANIZER_PATH_BEDS=/beds
ORGANIZER_PATH_DEPARTMENTS=/departments
```

If they use a different header (for example `X-API-Key` with an empty scheme):

```
ORGANIZER_API_AUTH_HEADER=X-API-Key
ORGANIZER_API_AUTH_SCHEME=
```

Then restart the backend. In the app, open **Settings → Organizer integration** and click **Test connection** or **Sync now**.

Code that performs the call:

- `backend/app/services/organizer_sync.py`
- `backend/app/routes/organizer.py`

If their JSON shape is different from ours, adapt the mapping functions in `organizer_sync.py` only. The dashboard keeps reading Hospivance’s own tables.

## 2. Organizer hosts YOUR frontend or backend

| They say… | You change… |
| --- | --- |
| “Point the UI at our backend URL” | `frontend/.env` → `VITE_API_BASE_URL=https://their-backend.example` |
| “Deploy the API at this origin” | Run uvicorn behind that host; set `CORS_ORIGINS` in `backend/.env` |
| “Add our API key for LLM” | `OPENAI_API_KEY` or `GEMINI_API_KEY` in `backend/.env` only |
| “Embed this dashboard in our portal” | They iframe `/` or `/app`; CORS and `VITE_API_BASE_URL` must match |

Frontend env example (`frontend/.env`):

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Never put organizer or OpenAI keys in `VITE_*` variables. Anything starting with `VITE_` is visible in the browser.

## 3. Organizer gives HL7 FHIR

Use:

- `GET /api/fhir/metadata`
- `GET /api/fhir/Bundle/encounters`

Mapper: `backend/app/services/fhir_service.py`

If they provide a FHIR base URL, add it as `ORGANIZER_API_BASE_URL` and extend `organizer_sync.py` to pull `Encounter` resources.

## 4. What you should not edit for a last-minute hookup

- Trained model artifacts (`backend/ml/`)
- Chart components
- Table names in the dashboard

Keep integration in env vars + `organizer_sync.py`.
