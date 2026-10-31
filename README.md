# 🇪🇬 Egyptian Legal AI

An educational tool for Egyptian legal questions in Arabic — source-grounded, never fabricated. A person asks a question in their own words and gets back the relevant legal field, the exact law and article(s), the current and (eventually) historical version, an Arabic explanation, missing facts, procedural next steps, and real source links.

**Core rule, never compromised:** if the database doesn't contain enough verified information to answer, the correct answer is to say so — not to sound confident. See `docs/legal-source-policy.md` and `docs/security.md#no-hallucination-policy`.

## Status: v1 skeleton (Stage 1 of the full spec)

This repo is a **working skeleton**, not a finished platform. The full production spec (auth, cases, admin dashboard, lawyer mode, contract analysis, OCR pipeline, judgment database, knowledge graph, 500–10,000-question evaluation set reviewed by licensed Egyptian lawyers) is a multi-month build for a team, not something any single session — AI or human — can honestly deliver "finished" overnight. This skeleton is honest about what's real right now:

**Actually working:**
- Backend (FastAPI + SQLite for now, Postgres/pgvector-ready) — real auth (JWT + bcrypt), real hybrid search (exact article-reference detection + keyword), a real RAG pipeline that calls Google Gemini and falls back to an honest "insufficient information" answer rather than guessing when Gemini isn't configured or the retrieved context is thin.
- Frontend (Next.js + TypeScript + Tailwind, Arabic RTL) — a real chat interface at `/ask` rendering the 8-section Arabic answer format, real content pages (about, how-it-works, disclaimer, privacy, terms), graceful error handling when the backend is unreachable.
- 4 flagship laws registered in `data/inventory/legal_sources.xlsx` with real, independently-cross-checked metadata (law number, year, official Gazette issue, source URLs) — **not yet** article-level text; that's the next phase.

**Explicitly deferred (placeholder pages, TODO-stubbed code):** user dashboard, case management, document upload/OCR, admin dashboard, lawyer mode, contract analysis, legal knowledge graph, judgment database, evaluation dataset. Each placeholder names exactly what it's waiting on.

## Why this scope, and why it can stay free

See `docs/deployment.md` for the full reasoning, but in short: Postgres+pgvector has genuine free tiers (Supabase, Neon) and Next.js/FastAPI deploy free (Vercel, Render) — PythonAnywhere's free-tier network allowlist made an earlier, unrelated project painful, so it's not part of this plan. Gemini's free tier handles the LLM calls; live web search (for laws not yet in the local database) is deferred until there's a confirmed-working, genuinely free search provider wired in.

## Project structure

```
egyptian-legal-ai/
├── backend/     FastAPI app — see backend/README.md (generated) and inline docstrings
├── frontend/    Next.js app
├── docs/        architecture, legal-source-policy, data-policy, security, evaluation, deployment
├── data/        inventory (source registry), raw/processed/ocr/validated/evaluation (empty — Stage 2)
├── scripts/     ingestion/processing scripts (mostly documented TODO stubs — need real source documents first)
├── tests/       retrieval/legal_qa/security/regression test scaffolding
└── docker-compose.yml   postgres+pgvector, backend, frontend — for when you're ready to move off SQLite
```

## Local development (no Docker)

Backend:
```
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY (free at https://aistudio.google.com/apikey), JWT_SECRET
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (separate terminal):
```
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit `http://localhost:3000`.

## Local development (Docker)

```
cp .env.example .env   # fill in secrets
docker compose up --build
```

## Roadmap (next real steps, in order)

1. Article-level extraction for the 4 flagship laws already in the registry (Stage 2 of the spec) — real text, source-linked, byte-verified against the actual fetched page, the same careful way as before.
2. Expand the registry to more laws within the same 4 domains before adding new domains.
3. Wire real hybrid search over that real article data.
4. Build a small (30–50 question), honestly-scoped evaluation set — not 500+ yet — and measure retrieval accuracy before generation quality.
5. Only then: accounts, cases, document upload.

## Disclaimer

This tool provides general educational legal information, not official legal advice. Users are always directed to consult a licensed Egyptian lawyer for their specific situation.
