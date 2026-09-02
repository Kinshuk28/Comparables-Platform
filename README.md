# Fairness Opinion Generator

Generates a fairness opinion report for a proposed M&A transaction by combining three
standard valuation methodologies — Discounted Cash Flow (DCF), Comparable Company
Analysis (trading comps), and Precedent Transaction Analysis — into a football field
valuation summary, then drafts the accompanying narrative report with an LLM. It talks
to any OpenAI-compatible chat completions API, and defaults to **Groq's free tier** so
generating reports costs nothing.

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
4. On request, the computed numbers (never invented ones) are handed to the LLM, which
   drafts the narrative fairness opinion report around them.
5. Everything is persisted to PostgreSQL so past analyses and reports can be revisited.

## Tech stack

- **Frontend:** Next.js 14 (App Router, TypeScript, Tailwind CSS, Recharts)
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL (JSONB columns store the full input/output payloads)
- **AI:** any OpenAI-compatible Chat Completions API (defaults to Groq, free)

## Getting a free API key

The "Generate Fairness Opinion Report" step needs an LLM API key. The valuation math
(DCF, comps, precedent transactions, the football field) works without one.

By default the app is wired to **[Groq](https://console.groq.com/keys)** — sign up
with just an email, no credit card, and it gives you a free API key immediately with a
generous daily quota running Llama 3.3 70B, which is plenty for this. That's the
recommended path if you don't want to spend anything.

If you'd rather use something else, `backend/.env.example` has the settings for real
OpenAI (paid) and Google Gemini (also free, no credit card) — just swap
`OPENAI_BASE_URL` and `OPENAI_MODEL`.

## Quick start (Docker — recommended)

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

```bash
cp .env.example .env
# edit .env and paste your (free) Groq API key into OPENAI_API_KEY

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
   report. This calls the configured LLM API, so `OPENAI_API_KEY` must be set on the
   backend (see "Getting a free API key" above).
4. Past reports are listed under **Past Reports** in the nav bar.

## Deploying so others can use it (free)

This app has **no login** — everyone who uses the deployed link shares one database, so
anyone can see anyone else's past valuations and reports under "Past Reports." Fine for
a demo among friends; don't put real confidential deal data in it if that's not okay.

The free stack (no credit card required on any of the three):

- **[Neon](https://neon.tech)** — free PostgreSQL database
- **[Render](https://render.com)** — free hosting for the backend (FastAPI). Free
  instances sleep after 15 minutes of no traffic; the first request after that takes
  30-50 seconds to wake up. Fine for a demo, mention it if others notice a slow first
  load.
- **[Vercel](https://vercel.com)** — free hosting for the frontend (Next.js)

Steps (in this order — each one feeds the next):

1. **Neon:** sign up, create a project, copy the connection string it gives you
   (starts with `postgresql://...`).
2. **Render:** sign up, connect your GitHub account, **New → Blueprint**, pick this
   repo. Render reads `render.yaml` at the repo root and sets up the backend service.
   It'll prompt you for the env vars marked as secrets:
   - `DATABASE_URL` → the Neon connection string from step 1
   - `OPENAI_API_KEY` → your free Groq key
   - `CORS_ORIGINS` → leave as `http://localhost:3000` for now, you'll fix this in
     step 4
   Deploy, then copy the `.onrender.com` URL Render assigns the service.
3. **Vercel:** sign up, connect GitHub, import this repo. When it asks for the **Root
   Directory**, set it to `frontend` (important — this is a two-app repo). Add an
   environment variable `NEXT_PUBLIC_API_BASE_URL` set to the Render URL from step 2.
   Deploy, then copy the `.vercel.app` URL it gives you.
4. **Back in Render:** open the backend service's Environment settings, set
   `CORS_ORIGINS` to the Vercel URL from step 3 (e.g.
   `https://your-app.vercel.app`), save — this redeploys the backend.
5. Share the Vercel URL.

## Project layout

```
backend/
  app/
    valuation/        DCF, comparable company, and precedent transaction math (pure functions, unit tested)
    narrative.py       Builds the prompt and calls the configured LLM API
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
