# Fairness Opinion Generator

Generates a fairness opinion report for a proposed M&A transaction by combining three
standard valuation methodologies — Discounted Cash Flow (DCF), Comparable Company
Analysis (trading comps), and Precedent Transaction Analysis — into a football field
valuation summary, then drafts the accompanying narrative report with the OpenAI API.

**This produces an AI-generated draft for educational and internal discussion purposes
only.** It is not a substitute for a fairness opinion prepared by a licensed investment
bank or valuation professional, and must not be relied on for an actual transaction,
disclosure document, or fiduciary decision. Every generated report repeats this
disclaimer, and the AI is instructed to never omit it.

## How it works

1. You enter the deal terms (offer price, shares outstanding, net debt), DCF
   assumptions (revenue growth, margins, WACC, terminal growth), a list of comparable
   public companies, and a list of precedent M&A transactions.
2. The backend runs all three valuations:
   - **DCF** — projects unlevered free cash flow for the forecast period, discounts it
     and a Gordon Growth terminal value at WACC, and derives a per-share range from a
     WACC/terminal-growth sensitivity grid.
   - **Comparable Company Analysis** — applies the peer group's 25th–75th percentile
     EV/Revenue and EV/EBITDA multiples to the target's own metrics.
   - **Precedent Transaction Analysis** — same math, using multiples paid in historical
     deals (which already embed a control premium).
3. The three implied ranges are plotted against the offer price on a football field
   chart, and a rule-based check flags whether the offer sits within, above, or below
   each range.
4. On request, the computed numbers (never invented ones) are handed to the OpenAI API,
   which drafts the narrative fairness opinion report around them.
5. Everything is persisted to PostgreSQL so past analyses and reports can be revisited.

## Tech stack

- **Frontend:** Next.js 14 (App Router, TypeScript, Tailwind CSS, Recharts)
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL (JSONB columns store the full input/output payloads)
- **AI:** OpenAI Chat Completions API

## Quick start (Docker — recommended)

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
and an [OpenAI API key](https://platform.openai.com/api-keys) (only needed for the
"Generate Fairness Opinion Report" step — the valuation math works without it).

```bash
cp .env.example .env
# edit .env and paste your OPENAI_API_KEY

docker compose up --build
```

Then open:
- **App:** http://localhost:3000
- **API docs:** http://localhost:8000/docs

The database schema is created automatically on first startup.

## Manual setup (without Docker)

### 1. PostgreSQL

Create a local database named `fairness_opinion` (or point `DATABASE_URL` at whatever
Postgres instance you have).

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL and OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```

Run the test suite (pure calculation logic, no database needed):

```bash
PYTHONPATH=. pytest tests/ -v
```

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

Open http://localhost:3000.

## Using the app

1. On the home page, fill in (or use the pre-filled sample values for) the deal
   overview, DCF assumptions, comparable companies, and precedent transactions.
2. Click **Run Valuation Analysis** to see the football field chart and per-method
   valuation summary.
3. Click **Generate Fairness Opinion Report** to have the AI draft the full narrative
   report. This calls the OpenAI API, so `OPENAI_API_KEY` must be set on the backend.
4. Past reports are listed under **Past Reports** in the nav bar.

## Project layout

```
backend/
  app/
    valuation/        DCF, comparable company, and precedent transaction math (pure functions, unit tested)
    narrative.py       Builds the OpenAI prompt and calls the API
    models.py           SQLAlchemy models (Valuation, FairnessOpinion)
    schemas.py           Pydantic request/response models
    routers/              FastAPI endpoints
  tests/                    Unit tests for the valuation engine
frontend/
  app/                        Pages: new analysis (/), report (/reports/[id]), report list (/reports)
  components/            Form inputs, football field chart, valuation summary, report view
  lib/                        API client and shared TypeScript types
docker-compose.yml
```

## API summary

| Method | Path | Description |
|---|---|---|
| POST | `/api/valuations` | Run DCF + comps + precedent transaction analysis, persist, return results |
| GET | `/api/valuations` | List past valuations |
| GET | `/api/valuations/{id}` | Get one valuation's full inputs and results |
| POST | `/api/valuations/{id}/opinion` | Generate the AI fairness opinion narrative for a valuation |
| GET | `/api/opinions/{id}` | Get a generated report (with its valuation) |
| GET | `/api/opinions` | List generated reports |

Full interactive docs are at `/docs` on the running backend.

## Known limitations

- `npm audit` flags a handful of advisories against the pinned Next.js version. The
  ones that apply to a running app (Server Actions request smuggling / DoS) don't
  affect this project — it has no Server Actions; all mutations go through the FastAPI
  backend. Upgrading to Next.js 16 would clear the rest but requires reworking the
  dynamic route's `params` API (now async) and is left as a future improvement.
- The fairness read (`supports_fairness` / `mixed` / `does_not_support_fairness`) is a
  simple rule — offer price vs. each method's implied range — not a judgment call. The
  AI narrative explains it in prose but doesn't override it.
