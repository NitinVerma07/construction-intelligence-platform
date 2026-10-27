# AI-Powered Multimodal Construction Intelligence Platform

A full-stack decision-support system for construction professionals. It analyses **text, site images and structured project data** with a multimodal LLM and returns **strict JSON** that the React UI renders safely.

| Module | Input | Output |
|---|---|---|
| Site Safety Monitoring | Site photo (+ notes) | Risk level/score, PPE detected/missing, hazards with fixes |
| Crack Detection & Analysis | Wall/slab photo (+ notes) | Crack type, severity, causes, actions, urgency, confidence |
| Real Estate Valuation | Property details | Value, price/sq ft, range, value drivers |
| Construction Planning | Project parameters | Phases & schedule, materials, cost breakdown, risks |
| Weather-Aware Advisory | City + activity | Live weather, 3-day outlook, go / caution / stop guidance |
| Daily Site Assistant | Question + site context | Answer, checklist, follow-ups |
| Knowledge Assistant | Question | Answer, key points, IS/code references |
| History | - | Every analysis saved in SQLite, viewable and deletable |

## Architecture

```
React (Vite)  --/api-->  FastAPI routers  -->  services/pipeline
                                                  |-- services/llm.py       (multimodal LLM -> JSON -> Pydantic validation)
                                                  |-- services/fallbacks.py (deterministic rules; offline demo + safety net)
                                                  |-- services/weather.py   (Open-Meteo, no key needed)
                                                  `-- database.py           (SQLite via SQLAlchemy)
```

**Strict JSON contracts** live in `backend/app/schemas.py`. The JSON Schema of each response model is sent to the LLM, the reply is parsed and validated, retried once, and finally replaced by a rule-based fallback, so the frontend always receives a valid shape. Every response is wrapped as:

```json
{ "source": "llm | mock | fallback", "analysis_id": 12, "result": { "...module contract..." } }
```

## Project structure

```
construction-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router registration
│   │   ├── config.py          # Settings from .env
│   │   ├── database.py        # SQLAlchemy engine, Analysis model
│   │   ├── schemas.py         # Strict JSON data contracts
│   │   ├── routers/           # safety, cracks, valuation, planning, assistant, knowledge, weather, history
│   │   └── services/          # llm, pipeline, fallbacks, weather, images
│   ├── tests/                 # pytest suite (runs offline)
│   └── pytest.ini
├── frontend/                  # React 18 + Vite
│   ├── src/ (App.jsx, api.js, components/, styles.css)
│   ├── index.html, package.json, vite.config.js, vercel.json
├── db/
│   └── schema.sql             # SQLite schema (DB file is created here at runtime)
├── Dockerfile                 # Production multi-stage Docker build
├── render.yaml                # 1-click deployment blueprint for Render
├── requirements.txt
├── .env / .env.example
├── .gitignore
└── README.md
```

## Prerequisites

Python 3.10+, Node.js 18+, Git. An Anthropic API key is optional: without one, the app runs in **demo mode** using built-in rules (the UI says so clearly). Image analysis and refined answers need a key.

## Quick start

**1. Backend**
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# edit .env and set ANTHROPIC_API_KEY (optional)
cd backend
uvicorn app.main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

**2. Frontend** (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. Vite proxies `/api` to port 8000.

## Configuration (`.env` in the project root)

| Variable | Default | Meaning |
|---|---|---|
| `ANTHROPIC_API_KEY` | empty | Enables live AI. Empty means demo mode |
| `LLM_MODE` | `auto` | `auto`, `live` (always call AI) or `mock` (never call AI) |
| `LLM_MODEL` | `claude-sonnet-5-5` | Model used for all modules |
| `DATABASE_URL` | `sqlite:///<root>/db/construction.db` | Any SQLAlchemy URL (e.g. PostgreSQL/RDS) |
| `CORS_ORIGINS` | localhost:5173 | Comma-separated allowed origins |
| `MAX_IMAGE_MB` | `5` | Upload size limit |

Never commit `.env`; it is git-ignored. Use `.env.example` as the template.

## API

| Method | Endpoint | Body |
|---|---|---|
| GET | `/api/health` | - |
| POST | `/api/safety/analyze` | multipart: `file`, `notes` |
| POST | `/api/cracks/analyze` | multipart: `file`, `notes` |
| POST | `/api/valuation/estimate` | JSON (`city`, `area_sqft`, `property_type`, ...) |
| POST | `/api/planning/generate` | JSON (`location`, `built_up_area_sqft`, `floors`, ...) |
| POST | `/api/weather/advisory` | JSON (`city`, `activity`) |
| POST | `/api/assistant/ask` | JSON (`query`, `site_context`) |
| POST | `/api/knowledge/ask` | JSON (`question`) |
| GET / DELETE | `/api/history`, `/api/history/{id}` | - |

Example:
```bash
curl -X POST http://127.0.0.1:8000/api/valuation/estimate \
  -H "Content-Type: application/json" \
  -d '{"city":"Indore","area_sqft":1200,"property_type":"apartment","age_years":5}'
```

## Tests

```bash
cd backend
pytest
```
The suite forces offline mode and an isolated temp database, so it needs no API key or network.

## Deployment Guide (Live Demo Link)

### Option 1: Render.com (Recommended - Free & 1-Click)
1. Sign in to [Render.com](https://render.com) using your GitHub account (`NitinVerma07`).
2. Click **New +** > **Web Service**.
3. Select your repository: `construction-intelligence-platform`.
4. Render detects the `Dockerfile` automatically.
5. Select the **Free** instance type.
6. (Optional) Under **Environment Variables**, add `ANTHROPIC_API_KEY` if you have one.
7. Click **Create Web Service**.
8. Once built, Render gives you a live public URL (e.g. `https://construction-intelligence-platform.onrender.com`).

### Option 2: Railway.app
1. Go to [Railway.app](https://railway.app) and login with GitHub.
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select `NitinVerma07/construction-intelligence-platform`.
4. Click **Deploy**. Railway builds the multi-stage Docker container and provides a public domain under Settings > Domains.

## Submission checklist (SkillWallet)

Add the GitHub repository link and your live demo link:
- **Repository URL:** `https://github.com/NitinVerma07/construction-intelligence-platform`
- **Demo Link:** Your deployed URL from Render/Railway (or screen recording).
